"""
Service d'empreintes faciales — LBP Histogram (256-dim).

Architecture :
  - Aucune dépendance lourde (uniquement numpy + OpenCV déjà installés).
  - Aucun réentraînement complet nécessaire : chaque photo génère son embedding.
  - Ajout d'un nouvel élève = calculer + stocker ses embeddings.
  - Reconnaissance = comparer l'embedding inconnu à tous les embeddings en base.
"""
from __future__ import annotations

import struct
from collections import defaultdict
from dataclasses import dataclass

import cv2
import numpy as np

from .vision import build_detector

EMBED_DIM = 256
EMBED_FACE_SIZE = 64
BLUR_THRESHOLD = 15.0   # Seuil abaissé — on accepte les photos légèrement floues

# Grille spatiale 2×2 = 4 cellules × 64 bins = 256 dims (même stockage)
# ─ TOP-LEFT   : front + œil gauche          ─ TOP-RIGHT  : front + œil droit
# ─ BOTTOM-LEFT: joue gauche + bouche gauche ─ BOTTOM-RIGHT: joue droite + menton
#
# Pourquoi 2×2 et pas 4×4 ?
#  • 4×4 est trop sensible aux petits décalages de recadrage et d'angle webcam
#    → la même personne en conditions live score souvent < 50%, reconnue INCONNUE.
#  • 2×2 préserve la structure gauche/droite et haut/bas du visage (discriminant)
#    sans être fragile aux variations d'éclairage intra-personne.
GRID_N = 2
BINS_PER_CELL = EMBED_DIM // (GRID_N * GRID_N)   # = 64

# Seuil de reconnaissance. Il doit rester conservateur: une mauvaise présence
# officielle coûte plus cher qu'un visage envoyé en revue ou rejeté.
SIMILARITY_THRESHOLD = 72.0
AUTO_ACCEPT_THRESHOLD = 82.0
AMBIGUITY_MARGIN = 12.0
MIN_TOP_SAMPLES = 3
# Multiplicateur chi2 — calibré pour histogrammes LBP normalisés (grille 2×2).
CHI2_MULTIPLIER = 38.0


# ─── Prétraitement robuste ─────────────────────────────────────────────────────

def _preprocess_face(face_gray: np.ndarray, size: int = EMBED_FACE_SIZE) -> np.ndarray:
    """
    Prétraitement robuste :
      1. Redimensionner à size×size
      2. Netteté adaptative (aide pour caméras floues)
      3. CLAHE (normalisation locale du contraste, meilleure que equalizeHist)

    NOTE : Ne pas modifier ce pipeline sans régénérer tous les embeddings en base,
    car les vecteurs stockés et les vecteurs de requête DOIVENT utiliser le même
    prétraitement pour que la comparaison soit valide.
    """
    face = cv2.resize(face_gray, (size, size), interpolation=cv2.INTER_AREA)

    # Netteté légère — améliore les images floues sans sur-accentuer les détails
    kernel = np.array([[0, -0.5, 0],
                       [-0.5, 3.0, -0.5],
                       [0, -0.5, 0]], dtype=np.float32)
    sharpened = cv2.filter2D(face.astype(np.float32), -1, kernel)
    face = np.clip(sharpened, 0, 255).astype(np.uint8)

    # CLAHE — bien meilleur qu'equalizeHist pour les variations d'éclairage
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    face = clahe.apply(face)

    return face


# ─── Génération de l'embedding ────────────────────────────────────────────────

def compute_face_embedding(face_gray: np.ndarray) -> np.ndarray:
    """
    Calcule un embedding LBP spatial (256-dim) depuis un visage en niveaux de gris.

    Architecture — grille 2×2 spatiale :
      1. Redimensionner (64×64) + netteté + CLAHE
      2. Calculer les codes LBP 8-voisins sur toute la face → carte 62×62
      3. Diviser en 2×2 = 4 cellules (≈31×31 pixels chacune)
      4. Pour chaque cellule : histogramme 64 bins (LBP >> 2, valeurs 0-63)
      5. Concaténer → 4 × 64 = 256 dims → normaliser L1

    Grille 2×2 (robustesse vs discrimination) :
    • Suffit à séparer front+yeux (haut) de nez+bouche (bas) et gauche de droite.
    • Moins fragile aux petits décalages de recadrage / angles webcam que 4×4.
    • Beaucoup plus discriminant qu'un histogramme global (aucune info spatiale).
    """
    face = _preprocess_face(face_gray).astype(np.int16)

    # ── Carte LBP 8-voisins (vectorisé) ──────────────────────────────────────
    center = face[1:-1, 1:-1]
    pattern = np.zeros_like(center, dtype=np.uint8)
    neighbors = [
        face[0:-2, 0:-2], face[0:-2, 1:-1], face[0:-2, 2:],
        face[1:-1, 2:],   face[2:,   2:],   face[2:,   1:-1],
        face[2:,   0:-2], face[1:-1, 0:-2],
    ]
    for k, n in enumerate(neighbors):
        pattern |= ((n >= center).astype(np.uint8) << k)
    # pattern : 62×62

    # ── Histogrammes par cellule (2×2 grille) ────────────────────────────────
    H, W = pattern.shape          # 62×62
    gh = H // GRID_N              # = 31
    gw = W // GRID_N              # = 31

    parts: list[np.ndarray] = []
    for i in range(GRID_N):
        for j in range(GRID_N):
            cell = pattern[i * gh:(i + 1) * gh, j * gw:(j + 1) * gw]
            # 64 bins : top 6 bits du code LBP (valeurs 0-63)
            coarse = (cell >> 2).ravel()
            hist, _ = np.histogram(coarse, bins=BINS_PER_CELL, range=(0, BINS_PER_CELL))
            parts.append(hist)

    vec = np.concatenate(parts).astype(np.float32)   # 4×64 = 256 dims
    total = vec.sum()
    if total > 0:
        vec /= total
    return vec


def blur_score(gray_face: np.ndarray) -> float:
    """Variance du Laplacien — plus élevé = plus net."""
    return float(cv2.Laplacian(gray_face, cv2.CV_64F).var())


def vector_to_bytes(vec: np.ndarray) -> bytes:
    """Sérialise float32[256] → bytes (1024 octets)."""
    return struct.pack(f"{EMBED_DIM}f", *vec.tolist())


def bytes_to_vector(data: bytes) -> np.ndarray:
    """Désérialise bytes → float32[256]."""
    return np.array(struct.unpack(f"{EMBED_DIM}f", data), dtype=np.float32)


# ─── Similarité ───────────────────────────────────────────────────────────────

def _chi2_score(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Distance chi-carrée normalisée, convertie en score 0-100.
    Multiplicateur CHI2_MULTIPLIER=38 (réduit de 50) pour mieux tolérer les
    variations d'éclairage entre photos d'entraînement et frames live webcam.
    Chi2 typique même personne webcam : 0.5-1.2  →  score 54-81% (était 40-75%)
    Chi2 typique personne différente  : 1.5-4.0  →  score 0-43% (sous le seuil 28%)
    """
    eps = 1e-7
    chi2 = float(0.5 * np.sum((v1 - v2) ** 2 / (v1 + v2 + eps)))
    return max(0.0, 100.0 - chi2 * CHI2_MULTIPLIER)


def _cosine_score(v1: np.ndarray, v2: np.ndarray) -> float:
    """Similarité cosinus — robuste aux variations d'échelle et d'éclairage."""
    norm = np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-7
    return float(max(0.0, np.dot(v1, v2) / norm) * 100.0)


@dataclass(frozen=True)
class MatchCandidate:
    student_id: int
    combined_score: float
    chi2_score: float
    cos_score: float
    best_score: float
    margin: float = 0.0
    samples: int = 0


def chi2_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Score combiné chi2+cosinus pour une reconnaissance plus robuste."""
    return round(0.6 * _chi2_score(v1, v2) + 0.4 * _cosine_score(v1, v2), 2)


# ─── Extraction depuis image brute ────────────────────────────────────────────

def extract_embedding_from_image(
    image_bytes: bytes,
    detector=None,
) -> tuple[np.ndarray | None, float, float]:
    """
    Détecte le premier visage dans une image JPEG/PNG et retourne :
      (embedding, blur_score, confidence_quality)
    Retourne (None, 0, 0) si aucun visage détecté.
    """
    if detector is None:
        detector = build_detector()

    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        return None, 0.0, 0.0

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Netteté légère pour améliorer la détection sur les images floues
    blurred = cv2.GaussianBlur(gray, (0, 0), 2)
    gray_sharp = cv2.addWeighted(gray, 1.4, blurred, -0.4, 0)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray_sharp)

    faces = detector.detectMultiScale(
        gray_eq,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(40, 40),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    if len(faces) == 0:
        # Fallback : image déjà recadrée sur le visage (ex. cap_*_face.jpg).
        # Le détecteur Haar échoue sur des photos sans contexte autour du visage.
        # Si l'image est d'une taille raisonnable, on la traite directement.
        h_img, w_img = gray_eq.shape
        if h_img >= 30 and w_img >= 30:
            bscore = blur_score(gray_eq)
            if bscore < BLUR_THRESHOLD:
                return None, bscore, 0.0
            embedding = compute_face_embedding(gray_eq)
            return embedding, bscore, float(np.max(embedding) * 100)
        return None, 0.0, 0.0

    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_gray = gray_eq[y:y + h, x:x + w]
    bscore = blur_score(face_gray)
    embedding = compute_face_embedding(face_gray)
    return embedding, bscore, float(np.max(embedding) * 100)


# ─── Reconnaissance par base d'embeddings ─────────────────────────────────────

def _compute_scores_matrix(
    query_vector: np.ndarray,
    matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Retourne (chi2_scores, cos_scores, combined_scores) vectorisés pour une matrice (N, D).
    """
    q = query_vector[np.newaxis, :]
    eps = 1e-7
    chi2_vec = 0.5 * np.sum((matrix - q) ** 2 / (matrix + q + eps), axis=1)
    chi2_scores = np.clip(100.0 - chi2_vec * CHI2_MULTIPLIER, 0.0, 100.0)
    norms = np.linalg.norm(matrix, axis=1) * (np.linalg.norm(q) + eps)
    cos_scores = np.clip((matrix @ q.T).flatten() / (norms + eps) * 100.0, 0.0, 100.0)
    combined = 0.6 * chi2_scores + 0.4 * cos_scores
    return chi2_scores, cos_scores, combined


def _group_by_student(
    embeddings: list[tuple[int, np.ndarray]],
) -> dict[int, np.ndarray]:
    """Groupe les embeddings par étudiant et retourne {student_id: matrix(N, D)}."""
    student_vecs: dict[int, list[np.ndarray]] = defaultdict(list)
    for sid, vec in embeddings:
        student_vecs[sid].append(vec)
    return {sid: np.stack(vecs) for sid, vecs in student_vecs.items()}


def _score_student(query_vector: np.ndarray, sid: int, matrix: np.ndarray) -> MatchCandidate:
    """
    Score un étudiant avec plusieurs photos.

    Ancien comportement: prendre uniquement la meilleure photo. C'est très
    permissif: une seule image mal cadrée peut donner un faux 98%.
    Nouveau comportement: meilleur score + moyenne des meilleurs échantillons.
    """
    chi2s, coss, combs = _compute_scores_matrix(query_vector, matrix)
    order = np.argsort(combs)[::-1]
    best_idx = int(order[0])
    top_n = min(MIN_TOP_SAMPLES, len(order))
    top_scores = combs[order[:top_n]]

    if len(top_scores) == 1:
        combined = float(top_scores[0])
    else:
        combined = float(0.65 * top_scores[0] + 0.35 * np.mean(top_scores[1:]))

    return MatchCandidate(
        student_id=sid,
        combined_score=combined,
        chi2_score=float(chi2s[best_idx]),
        cos_score=float(coss[best_idx]),
        best_score=float(combs[best_idx]),
        samples=int(len(order)),
    )


def rank_matches(
    query_vector: np.ndarray,
    embeddings: list[tuple[int, np.ndarray]],
) -> list[MatchCandidate]:
    """Retourne les candidats triés du plus probable au moins probable."""
    if not embeddings:
        return []

    grouped = _group_by_student(embeddings)
    candidates = [
        _score_student(query_vector, sid, matrix)
        for sid, matrix in grouped.items()
    ]
    candidates.sort(key=lambda item: item.combined_score, reverse=True)

    if candidates:
        second = candidates[1].combined_score if len(candidates) > 1 else 0.0
        candidates[0] = MatchCandidate(
            student_id=candidates[0].student_id,
            combined_score=candidates[0].combined_score,
            chi2_score=candidates[0].chi2_score,
            cos_score=candidates[0].cos_score,
            best_score=candidates[0].best_score,
            margin=candidates[0].combined_score - second,
            samples=candidates[0].samples,
        )
    return candidates


def find_best_match(
    query_vector: np.ndarray,
    embeddings: list[tuple[int, np.ndarray]],
    threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[int | None, float, float, float]:
    """
    Compare query_vector contre [(student_id, vector)].
    Retourne (student_id, combined_score, chi2_score, cos_score).
    student_id = None si le score combiné est sous le seuil.

    Stratégie prudente :
      - score agrégé par étudiant, pas seulement la meilleure photo;
      - marge minimale entre le premier et le deuxième candidat;
      - seuil d'auto-acceptation haut pour éviter les faux positifs.
    """
    import sys
    if not embeddings:
        return None, 0.0, 0.0, 0.0

    candidates = rank_matches(query_vector, embeddings)
    if not candidates:
        return None, 0.0, 0.0, 0.0

    best = candidates[0]
    min_score = max(float(threshold), AUTO_ACCEPT_THRESHOLD)
    accepted = best.combined_score >= min_score and best.margin >= AMBIGUITY_MARGIN

    print(
        f"[RECOG] best={best.combined_score:.1f}% raw={best.best_score:.1f}% "
        f"(chi2={best.chi2_score:.1f}% cos={best.cos_score:.1f}%) "
        f"student={best.student_id} marge={best.margin:.1f} "
        f"seuil={min_score:.1f}% → {'OK' if accepted else 'INCONNU'}",
        file=sys.stderr,
    )

    if accepted:
        return (
            best.student_id,
            round(best.combined_score, 2),
            round(best.chi2_score, 2),
            round(best.cos_score, 2),
        )
    return None, round(best.combined_score, 2), round(best.chi2_score, 2), round(best.cos_score, 2)


def find_all_scores(
    query_vector: np.ndarray,
    embeddings: list[tuple[int, np.ndarray]],
) -> list[dict]:
    """
    Retourne les scores de TOUS les étudiants, triés par score combiné décroissant.
    Chaque entrée : {student_id, chi2_score, cos_score, combined_score}.
    Utilisé par la page de diagnostic pour comprendre pourquoi un visage est reconnu/rejeté.
    """
    if not embeddings:
        return []

    result = []
    candidates = rank_matches(query_vector, embeddings)
    for candidate in candidates:
        result.append({
            "student_id": candidate.student_id,
            "chi2_score": round(candidate.chi2_score, 1),
            "cos_score": round(candidate.cos_score, 1),
            "combined": round(candidate.combined_score, 1),
            "best_score": round(candidate.best_score, 1),
            "margin": round(candidate.margin, 1),
            "samples": candidate.samples,
        })
    return result
