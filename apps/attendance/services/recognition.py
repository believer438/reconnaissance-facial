from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta

import cv2
import numpy as np
from django.db import transaction
from django.utils import timezone

from apps.attendance.models import (
    AttendanceRecord,
    Camera,
    ClassroomSchedule,
    CourseSession,
    DailyAttendance,
    FaceDetectionEvent,
    RecognitionReviewQueue,
    Student,
    SystemConfig,
)

from .paths import LABEL_FILE, MODEL_FILE
from .vision import build_detector, ensure_opencv_face_available
from . import sface
from .embedding import (
    AMBIGUITY_MARGIN,
    AUTO_ACCEPT_THRESHOLD,
    compute_face_embedding,
    find_best_match,
    bytes_to_vector,
    SIMILARITY_THRESHOLD,
)

LBPH_RADIUS = 2
LBPH_NEIGHBORS = 8
LBPH_GRID_X = 8
LBPH_GRID_Y = 8

HAAR_SCALE_FACTOR = 1.1
HAAR_MIN_NEIGHBORS = 4         # Aligné avec l'entraînement (était 6, trop strict → ratait des vrais visages)
HAAR_MIN_SIZE = (40, 40)       # Aligné avec l'entraînement (était 60x60 → ratait les visages à distance)
FACE_MIN_AREA_RATIO = 0.003
NMS_OVERLAP_THRESHOLD = 0.5    # IoU max — 0.5 supprime mieux les boîtes dupliquées

# Valeurs par défaut — remplacées par SystemConfig.get()
LBPH_DISTANCE_THRESHOLD = 60.0
COOLDOWN_MINUTES = 5


def _load_all_embeddings() -> list[tuple[int, np.ndarray]]:
    """
    Charge tous les embeddings de la base de données.
    Retourne [(student_id, vector), ...].
    """
    from apps.attendance.models import FaceEmbedding
    rows = FaceEmbedding.objects.select_related("student").filter(
        student__is_active=True
    ).values_list("student_id", "vector")
    result = []
    for sid, raw in rows:
        try:
            vec = bytes_to_vector(bytes(raw))
            result.append((sid, vec))
        except Exception:
            pass
    return result


def _load_sface_embeddings() -> list[tuple[int, np.ndarray]]:
    """Charge les embeddings SFace modernes (128 float32)."""
    from apps.attendance.models import FaceEmbedding
    rows = FaceEmbedding.objects.select_related("student").filter(
        student__is_active=True
    ).values_list("student_id", "vector")
    result = []
    for sid, raw in rows:
        try:
            vec = sface.bytes_to_vector(bytes(raw))
            result.append((sid, vec))
        except Exception:
            pass
    return result


@dataclass
class RecognitionSummary:
    recognized_count: int
    unknown_count: int
    saved_records: int


@dataclass
class FaceResult:
    status: str          # "recognized" | "unknown" | "not_in_class" | "low_confidence" | "multiple_match"
    student: Student | None
    confidence: float
    already_marked: bool = False
    refused: bool = False
    too_early: bool = False
    not_in_class: bool = False
    low_confidence: bool = False      # Zone de doute — mis en file de revue
    distance_lbph: float = 0.0       # Distance brute LBPH
    face_bytes: bytes | None = None
    bbox_x_pct: float = 0.0
    bbox_y_pct: float = 0.0
    bbox_w_pct: float = 0.0
    bbox_h_pct: float = 0.0
    # Scores de debug — utiles pour l'overlay et la page de diagnostic
    debug_chi2: float = 0.0          # Score chi2 (0-100), composante principale
    debug_cos: float = 0.0           # Score cosinus (0-100), composante secondaire
    debug_margin: float = 0.0
    debug_engine: str = "lbp"
    debug_reason: str = ""


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_config() -> SystemConfig:
    """Retourne la configuration systeme (singleton, non-bloquant)."""
    try:
        return SystemConfig.get()
    except Exception:
        return SystemConfig()  # valeurs par défaut


def _create_review_ticket(
    student: "Student",
    distance: float,
    score: float,
    camera: "Camera | None",
    session: "CourseSession | None",
    face_bytes: "bytes | None",
    source: str = "live",
) -> None:
    """Crée un ticket LOW_CONFIDENCE dans la file de revue manuelle. Non-bloquant."""
    from django.core.files.base import ContentFile
    try:
        ticket = RecognitionReviewQueue(
            student_proposed=student,
            confidence_proposed=score,
            distance_lbph=distance,
            technical_status=RecognitionReviewQueue.TECH_LOW_CONFIDENCE,
            camera=camera,
            course_session=session,
            daily_date=timezone.localdate(),
            source=source,
        )
        if face_bytes:
            fname = f"review_{timezone.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            ticket.face_image.save(fname, ContentFile(face_bytes), save=False)
        ticket.save()
    except Exception:
        pass


def _log_event(
    etape: str,
    student: Student | None = None,
    session: CourseSession | None = None,
    camera: Camera | None = None,
    confiance: float = 0.0,
    source: str = "live",
    raison: str = "",
) -> None:
    """
    Journalise un événement brut dans FaceDetectionEvent.
    Non-bloquant : toute exception est silencieusement ignorée.
    """
    try:
        cfg = _get_config()
        if not cfg.archiver_evenements_bruts:
            return
        FaceDetectionEvent.objects.create(
            student=student,
            course_session=session,
            camera=camera,
            etape=etape,
            confiance=round(confiance, 1),
            source=source,
            raison=raison,
        )
    except Exception:
        pass


def _load_model():
    ensure_opencv_face_available()
    if not MODEL_FILE.exists() or not LABEL_FILE.exists():
        return None, {}
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=LBPH_RADIUS, neighbors=LBPH_NEIGHBORS,
            grid_x=LBPH_GRID_X, grid_y=LBPH_GRID_Y,
        )
        recognizer.read(str(MODEL_FILE))
        labels = json.loads(LABEL_FILE.read_text(encoding="utf-8"))
        return recognizer, {int(k): v for k, v in labels.items()}
    except Exception:
        return None, {}


# ─── Logique métier temporelle ────────────────────────────────────────────────

def _compute_status(student: Student, session: CourseSession | None = None) -> tuple[str, bool, bool]:
    """
    Retourne (statut, refuse, trop_tot).

    trop_tot=True  → detection avant la fenetre pre-cours autorisee
    refuse=True    → detection apres la fin du cours
    """
    now = timezone.localtime()
    now_naive = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)

    if session:
        session_date = session.date
        debut = datetime.combine(session_date, session.start_time)
        tolerance_retard = session.late_after_minutes
        minutes_avant = getattr(session, "minutes_avant_cours", 10)

        fenetre_debut = debut - timedelta(minutes=minutes_avant)
        threshold = debut + timedelta(minutes=tolerance_retard)

        if now_naive < fenetre_debut:
            return AttendanceRecord.STATUS_PRESENT, False, True  # too_early

        if session.end_time:
            fin = datetime.combine(session_date, session.end_time)
            if now_naive > fin:
                return AttendanceRecord.STATUS_PRESENT, True, False  # refused

        if now_naive <= threshold:
            return AttendanceRecord.STATUS_PRESENT, False, False
        return AttendanceRecord.STATUS_LATE, False, False

    # Fallback : ClassroomSchedule (ancien modèle)
    schedule = ClassroomSchedule.objects.filter(classroom=student.classroom).first()
    if not schedule:
        return AttendanceRecord.STATUS_PRESENT, False, False

    threshold_dt = timezone.make_aware(
        datetime.combine(now.date(), schedule.start_time),
        timezone.get_current_timezone(),
    ) + timedelta(minutes=schedule.late_after_minutes)
    if now <= threshold_dt:
        return AttendanceRecord.STATUS_PRESENT, False, False
    return AttendanceRecord.STATUS_LATE, False, False


def _already_marked(student: Student, session: CourseSession | None = None) -> bool:
    """
    Vérifie si l'étudiant a déjà été marqué dans cette session
    OU dans les X dernières minutes (cooldown anti-doublon, valeur issue de SystemConfig).
    """
    cfg = _get_config()
    cooldown = cfg.cooldown_detection_minutes

    if session:
        if AttendanceRecord.objects.filter(
            student=student,
            course_session=session,
            status__in=[AttendanceRecord.STATUS_PRESENT, AttendanceRecord.STATUS_LATE],
        ).exists():
            return True
        cutoff = timezone.now() - timedelta(minutes=cooldown)
        return AttendanceRecord.objects.filter(
            student=student,
            course_session=session,
            recognized_at__gte=cutoff,
        ).exists()

    now = timezone.localtime()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    return AttendanceRecord.objects.filter(
        student=student,
        recognized_at__gte=day_start,
        recognized_at__lt=day_end,
        status__in=[AttendanceRecord.STATUS_PRESENT, AttendanceRecord.STATUS_LATE],
    ).exists()


# ─── Detection ───────────────────────────────────────────────────────────────

def _sharpen_gray(gray: np.ndarray) -> np.ndarray:
    """Netteté légère — améliore la détection sur les images de webcam floues."""
    blurred = cv2.GaussianBlur(gray, (0, 0), 2)
    sharp = cv2.addWeighted(gray, 1.4, blurred, -0.4, 0)
    return sharp


def _iou(a: tuple, b: tuple) -> float:
    """Intersection over Union entre deux boîtes (x, y, w, h)."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    iy = max(0, min(ay + ah, by + bh) - max(ay, by))
    inter = ix * iy
    union = aw * ah + bw * bh - inter
    return inter / (union + 1e-7)


def _nms(boxes: list[tuple], overlap_threshold: float = NMS_OVERLAP_THRESHOLD) -> list[tuple]:
    """Non-Maximum Suppression — supprime les boîtes redondantes qui se chevauchent."""
    if not boxes:
        return []
    # Trier par aire décroissante (garder la plus grande détection par groupe)
    sorted_boxes = sorted(boxes, key=lambda b: b[2] * b[3], reverse=True)
    kept: list[tuple] = []
    while sorted_boxes:
        best = sorted_boxes.pop(0)
        kept.append(best)
        sorted_boxes = [b for b in sorted_boxes if _iou(best, b) < overlap_threshold]
    return kept


_ALT2_PATH = cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"


def _build_alt2_detector() -> cv2.CascadeClassifier | None:
    try:
        d = cv2.CascadeClassifier(_ALT2_PATH)
        return None if d.empty() else d
    except Exception:
        return None


def detect_faces(gray_image: np.ndarray, img_w: int, img_h: int) -> list[tuple[int, int, int, int]]:
    """
    Détection robuste avec stratégies progressives.
    Essaie du plus strict au plus permissif (5 passes default + alt2 fallback).
    """
    import sys
    detector = build_detector()

    # Prétraitement standard : sharpen + CLAHE
    sharp = _sharpen_gray(gray_image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(sharp)

    # Stratégies progressives avec cascade default
    # (image, scaleFactor, minNeighbors, minSize)
    attempts = [
        (enhanced,    1.1,  4, (40, 40)),  # Standard
        (enhanced,    1.1,  3, (30, 30)),  # Plus permissif
        (enhanced,    1.05, 2, (25, 25)),  # Très permissif, scan plus fin
        (gray_image,  1.1,  3, (30, 30)),  # Fallback : gray brut
        (gray_image,  1.05, 2, (20, 20)),  # Dernier recours default
    ]

    detected = []
    for img, scale, neighbors, min_size in attempts:
        raw = detector.detectMultiScale(
            img,
            scaleFactor=scale,
            minNeighbors=neighbors,
            minSize=min_size,
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if len(raw) > 0:
            detected = raw
            break

    # Fallback cascade alt2 (meilleure robustesse sur certains visages)
    if len(detected) == 0:
        alt2 = _build_alt2_detector()
        if alt2:
            for img, scale, neighbors, min_size in [
                (enhanced,   1.1,  3, (30, 30)),
                (enhanced,   1.05, 2, (25, 25)),
                (gray_image, 1.05, 2, (20, 20)),
            ]:
                raw = alt2.detectMultiScale(
                    img, scaleFactor=scale, minNeighbors=neighbors,
                    minSize=min_size, flags=cv2.CASCADE_SCALE_IMAGE,
                )
                if len(raw) > 0:
                    detected = raw
                    break

    if len(detected) == 0:
        print(f"[DETECT] Aucun visage ({img_w}x{img_h}) — toutes stratégies épuisées", file=sys.stderr)
        return []

    # Filtre minimal : surface trop petite (< 0.05% du frame → bruit)
    img_area = img_w * img_h
    valid = [
        (int(x), int(y), int(w), int(h))
        for (x, y, w, h) in detected
        if w * h >= img_area * 0.0005
    ]

    print(f"[DETECT] {len(valid)} visage(s) ({img_w}x{img_h})", file=sys.stderr)
    return _nms(valid)


# ─── Pipeline principal ───────────────────────────────────────────────────────

def recognize_from_image_bytes(
    image_data: bytes,
    threshold: float | None = None,
    session: CourseSession | None = None,
    allowed_student_ids: frozenset[int] | None = None,
    camera: Camera | None = None,
    source: str = "photo",
    raise_if_no_face: bool = True,
) -> list[FaceResult]:
    """
    Pipeline complet : DETECTE → RECONNU → [HORS_CLASSE?] → FaceResult

    allowed_student_ids : si fourni, rejette les étudiants absents de cet ensemble.
    Correspond au point 12 du document (filtrage par classe active = perf + sécurité).
    """
    cfg = _get_config()
    if threshold is None:
        threshold = cfg.seuil_distance_lbph

    # ── Choisir le moteur : YuNet/SFace moderne, sinon ancien LBP, sinon LBPH ──
    sface_embeddings = _load_sface_embeddings() if sface.models_available() else []
    use_sface = len(sface_embeddings) > 0
    all_embeddings = [] if use_sface else _load_all_embeddings()
    use_embeddings = len(all_embeddings) > 0

    recognizer, _label_map = (None, {}) if (use_sface or use_embeddings) else _load_model()
    if not use_sface and not use_embeddings and recognizer is None:
        raise RuntimeError(
            "Aucun modèle disponible. "
            "Ajoutez des photos aux élèves pour activer la reconnaissance par empreintes faciales."
        )

    nparr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise RuntimeError("Impossible de lire l'image. Verifiez le format (JPG, PNG, WebP).")

    img_h, img_w = frame.shape[:2]

    # ── Downscale automatique si la frame dépasse 800px ─────────────────────
    # La détection Haar cascade est nettement plus fiable sur 640×480 que sur
    # 1280×720 (scaleFactor inadapté + face trop petite en pourcentage du frame).
    MAX_DETECT_WIDTH = 800
    if img_w > MAX_DETECT_WIDTH:
        scale_f = MAX_DETECT_WIDTH / img_w
        new_w = MAX_DETECT_WIDTH
        new_h = int(img_h * scale_f)
        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        img_h, img_w = new_h, new_w
        import sys as _sys
        print(f"[RESIZE] Frame downscalée → {img_w}×{img_h}", file=_sys.stderr)

    gray_raw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # !! CRITIQUE !!
    # Le prétraitement DOIT être identique à extract_embedding_from_image (embedding.py)
    # qui a généré tous les vecteurs stockés en base.
    # Si ce pipeline diffère, les embeddings query ≠ embeddings DB → toujours INCONNU.
    #
    # Pipeline d'entraînement (embedding.py l.157-161) :
    #   blurred     = GaussianBlur(gray, (0,0), 2)
    #   gray_sharp  = addWeighted(gray, 1.4, blurred, -0.4, 0)  ← unsharp mask doux
    #   gray_eq     = CLAHE(gray_sharp)
    #   face_gray   = gray_eq[crop]   ← envoyé tel quel à compute_face_embedding
    #
    # → On doit reproduire EXACTEMENT ce pipeline ici.
    _blur = cv2.GaussianBlur(gray_raw, (0, 0), 2)
    gray_preprocessed = cv2.addWeighted(gray_raw, 1.4, _blur, -0.4, 0)
    _clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_preprocessed = _clahe.apply(gray_preprocessed)

    sface_detections = sface.detect_faces(frame) if use_sface else []
    faces = [d.bbox for d in sface_detections] if use_sface else detect_faces(gray_raw, img_w, img_h)

    if not faces:
        if raise_if_no_face:
            raise RuntimeError(
                "Aucun visage detecte. "
                "Assurez-vous que le visage est bien visible, eclaire de face, et assez proche."
            )
        return []

    results: list[FaceResult] = []

    for idx_face, (x, y, w, h) in enumerate(faces):
        # Crop depuis gray_preprocessed (sharpen+CLAHE une fois) = identique à l'entraînement
        crop_gray = gray_preprocessed[y: y + h, x: x + w]

        crop_color = frame[y: y + h, x: x + w]
        _, buf = cv2.imencode(".jpg", crop_color, [cv2.IMWRITE_JPEG_QUALITY, 85])
        face_bytes = buf.tobytes()

        bx = round(x / img_w * 100, 2)
        by = round(y / img_h * 100, 2)
        bw = round(w / img_w * 100, 2)
        bh = round(h / img_h * 100, 2)

        if use_sface:
            detection = sface_detections[idx_face]
            query_vec = sface.extract_feature(frame, detection)
            candidates = sface.rank_matches(query_vec, sface_embeddings)
            candidate = candidates[0] if candidates else None

            if candidate is None:
                label_id = None
                score = 0.0
                distance = 100.0
                unknown = True
                dbg_chi2 = 0.0
                dbg_cos = 0.0
                dbg_margin = 0.0
                dbg_reason = "aucun candidat SFace disponible"
            else:
                auto_match = sface.is_auto_match(candidate)
                label_id = candidate.student_id if auto_match else None
                score = candidate.confidence
                distance = round(100.0 - score, 1)
                unknown = not auto_match
                dbg_chi2 = round(candidate.best_confidence, 1)
                dbg_cos = round(candidate.cosine * 100.0, 1)
                dbg_margin = round(candidate.margin, 3)
                dbg_reason = ""
                if not auto_match:
                    if candidate.cosine < sface.SFACE_AUTO_ACCEPT_THRESHOLD:
                        dbg_reason = (
                            f"score SFace trop bas ({candidate.cosine:.3f} < "
                            f"{sface.SFACE_AUTO_ACCEPT_THRESHOLD:.2f})"
                        )
                    elif candidate.margin < sface.SFACE_AMBIGUITY_MARGIN:
                        dbg_reason = (
                            f"marge trop faible ({candidate.margin:.3f} < "
                            f"{sface.SFACE_AMBIGUITY_MARGIN:.2f}); visage trop proche d'un autre eleve"
                        )
                import sys as _sys_sface
                print(
                    f"[SFACE] student={candidate.student_id} cos={candidate.cosine:.3f} "
                    f"best={candidate.best_cosine:.3f} margin={candidate.margin:.3f} "
                    f"conf={score:.1f}% -> {'OK' if auto_match else 'INCONNU'}",
                    file=_sys_sface.stderr,
                )

        elif use_embeddings:
            # ── Moteur 1 : LBP histogram embeddings ──────────────────────────
            # Seuil conservateur: les faux positifs sont pires qu'un rejet.
            # find_best_match applique aussi une marge minimale entre candidats.
            embed_threshold = SIMILARITY_THRESHOLD
            # find_best_match retourne (student_id_ou_None, combined, chi2, cos)
            query_vec = compute_face_embedding(crop_gray)
            label_id, similarity, dbg_chi2, dbg_cos = find_best_match(
                query_vec, all_embeddings, threshold=embed_threshold
            )
            score    = round(similarity, 1)                  # déjà 0-100
            distance = round(100.0 - similarity, 1)         # distance inverse (0=parfait, 100=inconnu)
            unknown  = (label_id is None or similarity < embed_threshold)
            dbg_margin = 0.0
            dbg_reason = ""
        else:
            # ── Moteur 2 : LBPH fallback ──────────────────────────────────────
            label_id, distance = recognizer.predict(crop_gray)
            # Score garanti entre 80% (au seuil) et 100% (parfait) pour les reconnus
            # Pour les inconnus, score non-affiché donc peu importe
            score = round(max(0.0, 100.0 - 20.0 * (distance / max(threshold, 1.0))), 1)
            unknown = distance > threshold
            dbg_chi2 = score   # pas de décomposition chi2/cos en mode LBPH
            dbg_cos  = score
            dbg_margin = 0.0
            dbg_reason = ""
            import sys as _sys2
            print(
                f"[LBPH] label={label_id} dist={distance:.1f} seuil={threshold:.1f} "
                f"→ {'INCONNU' if unknown else 'RECONNU'} crop={crop_gray.shape[1]}x{crop_gray.shape[0]}",
                file=_sys2.stderr
            )

        # ── Étape 1 : UNKNOWN ─────────────────────────────────────────────────
        if unknown:
            if use_sface:
                reason = (
                    f"UNKNOWN: SFace score {score:.1f}% insuffisant ou ambigu "
                    f"(cos min {sface.SFACE_AUTO_ACCEPT_THRESHOLD:.2f}, "
                    f"marge min {sface.SFACE_AMBIGUITY_MARGIN:.2f})"
                )
            elif use_embeddings:
                reason = (
                    f"UNKNOWN: score {similarity:.1f}% insuffisant ou ambigu "
                    f"(seuil auto {AUTO_ACCEPT_THRESHOLD:.1f}%, marge min {AMBIGUITY_MARGIN:.1f})"
                )
            else:
                reason = f"UNKNOWN: Distance LBPH {distance:.1f} > seuil {threshold} (inconnu/etranger)"
            _log_event(
                FaceDetectionEvent.ETAPE_INCONNU,
                student=None, session=session, camera=camera,
                confiance=score, source=source,
                raison=reason,
            )
            results.append(FaceResult(
                status="unknown", student=None, confidence=0.0,
                distance_lbph=distance,
                face_bytes=face_bytes,
                bbox_x_pct=bx, bbox_y_pct=by, bbox_w_pct=bw, bbox_h_pct=bh,
                debug_chi2=dbg_chi2, debug_cos=dbg_cos,
                debug_margin=dbg_margin,
                debug_engine="sface" if use_sface else ("lbp_embedding" if use_embeddings else "lbph"),
                debug_reason=dbg_reason,
            ))
            continue

        # ── Étape 2 : Étudiant trouvé dans la base ?
        student = Student.objects.filter(id=label_id, is_active=True).first()
        if not student:
            _log_event(
                FaceDetectionEvent.ETAPE_INCONNU,
                student=None, session=session, camera=camera,
                confiance=score, source=source,
                raison=f"Eleve id={label_id} introuvable ou inactif",
            )
            results.append(FaceResult(
                status="unknown", student=None, confidence=0.0,
                distance_lbph=distance,
                face_bytes=face_bytes,
                bbox_x_pct=bx, bbox_y_pct=by, bbox_w_pct=bw, bbox_h_pct=bh,
                debug_chi2=dbg_chi2, debug_cos=dbg_cos,
                debug_margin=dbg_margin,
                debug_engine="sface" if use_sface else ("lbp_embedding" if use_embeddings else "lbph"),
                debug_reason=dbg_reason,
            ))
            continue

        # ── Étape 3 : LOW_CONFIDENCE — zone de doute (entre seuil_haute et seuil_limite) ?
        seuil_haute = getattr(cfg, "seuil_confiance_haute", 40.0)
        if distance > seuil_haute:
            # Zone de doute : NE PAS marquer présent automatiquement
            # Créer un ticket de revue manuelle
            _log_event(
                FaceDetectionEvent.ETAPE_RECONNU,
                student=student, session=session, camera=camera,
                confiance=score, source=source,
                raison=f"LOW_CONFIDENCE: distance {distance:.1f} > seuil_haute {seuil_haute} — mis en file de revue",
            )
            _create_review_ticket(
                student=student, distance=distance, score=score,
                camera=camera, session=session, face_bytes=face_bytes, source=source,
            )
            results.append(FaceResult(
                status="low_confidence",
                student=student,
                confidence=score,
                low_confidence=True,
                distance_lbph=distance,
                face_bytes=None,
                bbox_x_pct=bx, bbox_y_pct=by, bbox_w_pct=bw, bbox_h_pct=bh,
                debug_chi2=dbg_chi2, debug_cos=dbg_cos,
                debug_margin=dbg_margin,
                debug_engine="sface" if use_sface else ("lbp_embedding" if use_embeddings else "lbph"),
                debug_reason=dbg_reason,
            ))
            continue

        # ── Étape 4 : RECOGNIZED (haute confiance) — log
        _log_event(
            FaceDetectionEvent.ETAPE_RECONNU,
            student=student, session=session, camera=camera,
            confiance=score, source=source,
            raison=f"HAUTE CONFIANCE: distance {distance:.1f} <= {seuil_haute}",
        )

        # ── Étape 5 : Filtre par classe (point 12)
        if allowed_student_ids is not None and student.id not in allowed_student_ids:
            _log_event(
                FaceDetectionEvent.ETAPE_HORS_CLASSE,
                student=student, session=session, camera=camera,
                confiance=score, source=source,
                raison=f"{student.student_code} — pas inscrit dans la classe de cette session",
            )
            results.append(FaceResult(
                status="not_in_class", student=student, confidence=score,
                not_in_class=True, distance_lbph=distance, face_bytes=None,
                bbox_x_pct=bx, bbox_y_pct=by, bbox_w_pct=bw, bbox_h_pct=bh,
                debug_chi2=dbg_chi2, debug_cos=dbg_cos,
                debug_margin=dbg_margin,
                debug_engine="sface" if use_sface else ("lbp_embedding" if use_embeddings else "lbph"),
                debug_reason=dbg_reason,
            ))
            continue

        # ── Étape 6 : Logique métier (doublon, hors-horaire, trop-tôt)
        already = _already_marked(student, session)
        status_str, refused, too_early = _compute_status(student, session)

        results.append(FaceResult(
            status="recognized",
            student=student,
            confidence=score,
            already_marked=already,
            refused=refused,
            too_early=too_early,
            distance_lbph=distance,
            face_bytes=None,
            bbox_x_pct=bx, bbox_y_pct=by, bbox_w_pct=bw, bbox_h_pct=bh,
            debug_chi2=dbg_chi2, debug_cos=dbg_cos,
            debug_margin=dbg_margin,
            debug_engine="sface" if use_sface else ("lbp_embedding" if use_embeddings else "lbph"),
            debug_reason=dbg_reason,
        ))

    return results


# ─── Sauvegarde ──────────────────────────────────────────────────────────────

def save_attendance_from_results(
    results: list[FaceResult],
    course_session: CourseSession | None = None,
    camera: Camera | None = None,
    source: str = "photo",
) -> int:
    from .daily_attendance import register_check_in

    saved = 0
    seen_ids: set[int] = set()

    for result in results:
        if result.status != "recognized" or result.student is None:
            continue

        if result.already_marked:
            _log_event(
                FaceDetectionEvent.ETAPE_DOUBLON,
                student=result.student, session=course_session, camera=camera,
                confiance=result.confidence, source=source,
                raison="Deja marque dans cette session",
            )
            continue

        if result.refused:
            _log_event(
                FaceDetectionEvent.ETAPE_REFUSE,
                student=result.student, session=course_session, camera=camera,
                confiance=result.confidence, source=source,
                raison="Hors horaire (apres fermeture du cours)",
            )
            continue

        if result.too_early:
            _log_event(
                FaceDetectionEvent.ETAPE_TROP_TOT,
                student=result.student, session=course_session, camera=camera,
                confiance=result.confidence, source=source,
                raison="Detection avant la fenetre pre-cours",
            )
            continue

        if result.student.id in seen_ids:
            continue

        status_str, refused, too_early = _compute_status(result.student, course_session)
        if refused or too_early:
            continue

        daily_outcome = register_check_in(
            result.student,
            camera,
            source=source,
            confidence=result.confidence,
            log_event=False,
        )
        if daily_outcome.refused:
            _log_event(
                FaceDetectionEvent.ETAPE_REFUSE,
                student=result.student, session=course_session, camera=camera,
                confiance=result.confidence, source=source,
                raison=daily_outcome.message or daily_outcome.op,
            )
            continue

        with transaction.atomic():
            raw_record = AttendanceRecord.objects.create(
                student=result.student,
                course_session=course_session,
                camera=camera,
                student_name_snapshot=result.student.full_name,
                classroom_snapshot=result.student.classe_display,
                recognized_at=timezone.now(),
                confidence_score=result.confidence,
                status=status_str,
                source=source,
            )

        _log_event(
            FaceDetectionEvent.ETAPE_ENREGISTRE,
            student=result.student, session=course_session, camera=camera,
            confiance=result.confidence, source=source,
            raison=(
                f"Brut: {raw_record.status}; journalier: "
                f"{daily_outcome.record.status if daily_outcome.record else daily_outcome.op}"
            ),
        )

        if daily_outcome.record and daily_outcome.record.status in [
            DailyAttendance.STATUS_PRESENT,
            DailyAttendance.STATUS_RETARD,
            DailyAttendance.STATUS_EXCUSE,
        ]:
            saved += 1
        seen_ids.add(result.student.id)

    return saved
