from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from django.utils import timezone
from PIL import Image

from apps.attendance.models import FaceEmbedding, Student, TrainingPhoto

from .paths import LABEL_FILE, MODEL_DIR, MODEL_FILE, SFACE_MODEL_FILE
from .vision import build_detector, ensure_opencv_face_available
from .embedding import compute_face_embedding, vector_to_bytes
from . import sface


@dataclass
class TrainingSummary:
    students: int
    photos: int
    faces: int
    skipped_blurry: int
    model_path: str


def _blur_score(gray_face: np.ndarray) -> float:
    """Laplacian variance — lower = more blurry."""
    return float(cv2.Laplacian(gray_face, cv2.CV_64F).var())


def _augment_faces(crop: np.ndarray) -> list[np.ndarray]:
    """
    Augmentation étendue pour améliorer la robustesse de reconnaissance.
    Génère plusieurs variantes de la même image pour mieux couvrir les variations réelles.
    """
    augmented = [crop]

    # Flip horizontal
    augmented.append(cv2.flip(crop, 1))

    # Légère variation de luminosité
    bright = np.clip(crop.astype(np.int16) + 20, 0, 255).astype(np.uint8)
    dark   = np.clip(crop.astype(np.int16) - 20, 0, 255).astype(np.uint8)
    augmented.append(bright)
    augmented.append(dark)

    # Flip + variation de luminosité
    augmented.append(cv2.flip(bright, 1))
    augmented.append(cv2.flip(dark, 1))

    return augmented


def _train_sface_model() -> TrainingSummary:
    """Generate SFace embeddings for all training photos."""
    sface.ensure_models_available()

    label_map: dict[int, dict[str, str]] = {}
    embedding_payloads: list[tuple[int, int, bytes, str, float]] = []
    photo_count = 0
    skipped = 0
    trained_photo_ids: list[int] = []

    for student in Student.objects.filter(is_active=True).prefetch_related("photos"):
        student_ok = 0
        for photo in student.photos.all():
            photo_count += 1
            try:
                image_bytes = Path(photo.image.path).read_bytes()
                feature, quality = sface.extract_largest_feature(image_bytes)
            except Exception:
                feature, quality = None, 0.0

            if feature is None:
                skipped += 1
                TrainingPhoto.objects.filter(pk=photo.pk).update(face_detected=False)
                continue

            embedding_payloads.append((
                student.id,
                photo.id,
                sface.vector_to_bytes(feature),
                photo.angle_tag or "",
                quality,
            ))
            trained_photo_ids.append(photo.pk)
            student_ok += 1

        if student_ok:
            label_map[student.id] = {
                "full_name": student.full_name,
                "student_code": student.student_code,
                "classroom": student.classe_display,
                "engine": "opencv_sface",
            }

    if not embedding_payloads:
        raise RuntimeError(
            "Aucun visage exploitable trouve avec YuNet/SFace. "
            "Ajoutez des photos nettes, de face, avec un seul visage principal."
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    FaceEmbedding.objects.all().delete()
    FaceEmbedding.objects.bulk_create([
        FaceEmbedding(
            student_id=student_id,
            photo_id=photo_id,
            vector=vector,
            angle_tag=angle_tag,
            score_qualite=quality,
        )
        for student_id, photo_id, vector, angle_tag, quality in embedding_payloads
    ])
    LABEL_FILE.write_text(json.dumps(label_map, ensure_ascii=False, indent=2), encoding="utf-8")

    now = timezone.now()
    TrainingPhoto.objects.filter(pk__in=trained_photo_ids).update(trained_at=now, face_detected=True)

    return TrainingSummary(
        students=len(label_map),
        photos=photo_count,
        faces=len(embedding_payloads),
        skipped_blurry=skipped,
        model_path=str(SFACE_MODEL_FILE),
    )


def train_model(blur_threshold: float = 12.0) -> TrainingSummary:
    """Train the LBPH model on all student photos.

    Améliorations :
    - CLAHE (meilleur que equalizeHist) — même prétraitement qu'à la reconnaissance
    - Netteté légère avant détection
    - Augmentation étendue (flip + variations de luminosité)
    - Seuil de flou abaissé à 12 (était 50) — moins de photos rejetées
    - Marque TrainingPhoto.trained_at après entraînement réussi
    """
    if sface.models_available():
        return _train_sface_model()

    ensure_opencv_face_available()
    detector = build_detector()
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=2, neighbors=8, grid_x=8, grid_y=8
    )

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    faces: list[np.ndarray] = []
    labels: list[int] = []
    label_map: dict[int, dict[str, str]] = {}
    photo_count = 0
    skipped_blurry = 0
    trained_photo_ids: list[int] = []
    embedding_payloads: list[tuple[int, int, bytes, str, float]] = []

    for student in Student.objects.filter(is_active=True).prefetch_related("photos"):
        student_photos = list(student.photos.all())
        if not student_photos:
            continue

        student_faces: list[np.ndarray] = []

        for photo in student_photos:
            photo_count += 1
            try:
                image = Image.open(photo.image.path).convert("L")
                gray = np.array(image, dtype="uint8")
            except Exception:
                continue

            # Netteté légère pour améliorer la détection sur les photos floues
            blurred = cv2.GaussianBlur(gray, (0, 0), 2)
            sharp = cv2.addWeighted(gray, 1.4, blurred, -0.4, 0)

            # CLAHE — normalisation locale du contraste (identique à la reconnaissance)
            eq = clahe.apply(sharp)

            detected = detector.detectMultiScale(
                eq,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(40, 40),
            )

            face_found = False
            for (x, y, w, h) in sorted(detected, key=lambda box: box[2] * box[3], reverse=True):
                crop = eq[y: y + h, x: x + w]

                # Rejeter les faces vraiment trop floues (seuil bas = tolérant)
                score = _blur_score(crop)
                if score < blur_threshold:
                    skipped_blurry += 1
                    continue

                # Augmentation : plusieurs variantes pour plus de robustesse
                for aug in _augment_faces(crop):
                    student_faces.append(aug)
                embedding = compute_face_embedding(crop)
                embedding_payloads.append((
                    student.id,
                    photo.id,
                    vector_to_bytes(embedding),
                    photo.angle_tag or "",
                    score,
                ))
                face_found = True
                break

            if not face_found and len(detected) == 0:
                TrainingPhoto.objects.filter(pk=photo.pk).update(face_detected=False)
            else:
                trained_photo_ids.append(photo.pk)

        if student_faces:
            faces.extend(student_faces)
            labels.extend([student.id] * len(student_faces))
            label_map[student.id] = {
                "full_name": student.full_name,
                "student_code": student.student_code,
                "classroom": student.classroom,
            }

    if not faces:
        raise RuntimeError(
            "Aucun visage exploitable trouve. "
            "Verifiez que vos photos sont nettes et montrent clairement le visage de face."
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    recognizer.train(faces, np.array(labels))
    recognizer.save(str(MODEL_FILE))
    LABEL_FILE.write_text(json.dumps(label_map, ensure_ascii=False, indent=2), encoding="utf-8")

    FaceEmbedding.objects.all().delete()
    FaceEmbedding.objects.bulk_create([
        FaceEmbedding(
            student_id=student_id,
            photo_id=photo_id,
            vector=vector,
            angle_tag=angle_tag,
            score_qualite=quality,
        )
        for student_id, photo_id, vector, angle_tag, quality in embedding_payloads
    ])

    now = timezone.now()
    TrainingPhoto.objects.filter(pk__in=trained_photo_ids).update(trained_at=now, face_detected=True)

    n_augmented = 6   # nombre de variantes par visage détecté
    return TrainingSummary(
        students=len(label_map),
        photos=photo_count,
        faces=len(faces) // n_augmented,
        skipped_blurry=skipped_blurry,
        model_path=str(MODEL_FILE),
    )
