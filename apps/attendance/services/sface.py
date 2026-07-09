from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import cv2
import numpy as np

from .paths import SFACE_MODEL_FILE, YUNET_MODEL_FILE

SFACE_DIM = 128
DETECT_SCORE_THRESHOLD = 0.85
DETECT_NMS_THRESHOLD = 0.30
DETECT_TOP_K = 5000

# SFace/OpenCV cosine values are not percentages. These values are intentionally
# conservative for attendance: ambiguous faces must go to review/unknown.
SFACE_MATCH_THRESHOLD = 0.60
SFACE_AUTO_ACCEPT_THRESHOLD = 0.72
SFACE_AMBIGUITY_MARGIN = 0.12
MIN_TOP_SAMPLES = 3


@dataclass(frozen=True)
class SFaceDetection:
    bbox: tuple[int, int, int, int]
    face: np.ndarray
    score: float


@dataclass(frozen=True)
class SFaceCandidate:
    student_id: int
    cosine: float
    best_cosine: float
    margin: float = 0.0
    samples: int = 0

    @property
    def confidence(self) -> float:
        return cosine_to_confidence(self.cosine)

    @property
    def best_confidence(self) -> float:
        return cosine_to_confidence(self.best_cosine)


def models_available() -> bool:
    return YUNET_MODEL_FILE.exists() and SFACE_MODEL_FILE.exists()


def ensure_models_available() -> None:
    missing = [
        str(path)
        for path in (YUNET_MODEL_FILE, SFACE_MODEL_FILE)
        if not path.exists()
    ]
    if missing:
        raise RuntimeError(
            "Modeles YuNet/SFace manquants. Telechargez les fichiers ONNX dans media/models: "
            + ", ".join(missing)
        )
    if not hasattr(cv2, "FaceDetectorYN_create") or not hasattr(cv2, "FaceRecognizerSF_create"):
        raise RuntimeError("OpenCV ne supporte pas FaceDetectorYN/FaceRecognizerSF.")


def _create_detector(width: int, height: int):
    ensure_models_available()
    return cv2.FaceDetectorYN_create(
        str(YUNET_MODEL_FILE),
        "",
        (int(width), int(height)),
        float(DETECT_SCORE_THRESHOLD),
        float(DETECT_NMS_THRESHOLD),
        int(DETECT_TOP_K),
    )


def _create_recognizer():
    ensure_models_available()
    return cv2.FaceRecognizerSF_create(str(SFACE_MODEL_FILE), "")


def detect_faces(frame_bgr: np.ndarray) -> list[SFaceDetection]:
    height, width = frame_bgr.shape[:2]
    detector = _create_detector(width, height)
    _retval, faces = detector.detect(frame_bgr)
    if faces is None or len(faces) == 0:
        return []

    detections: list[SFaceDetection] = []
    for face in faces:
        x, y, w, h = face[:4]
        x = max(0, int(round(x)))
        y = max(0, int(round(y)))
        w = min(width - x, int(round(w)))
        h = min(height - y, int(round(h)))
        if w <= 0 or h <= 0:
            continue
        detections.append(
            SFaceDetection(
                bbox=(x, y, w, h),
                face=face.astype(np.float32),
                score=float(face[-1]),
            )
        )
    detections.sort(key=lambda item: item.bbox[2] * item.bbox[3], reverse=True)
    return detections


def extract_feature(frame_bgr: np.ndarray, detection: SFaceDetection) -> np.ndarray:
    recognizer = _create_recognizer()
    aligned = recognizer.alignCrop(frame_bgr, detection.face)
    feature = recognizer.feature(aligned).reshape(-1).astype(np.float32)
    norm = np.linalg.norm(feature)
    if norm > 0:
        feature = feature / norm
    return feature


def extract_largest_feature(image_bytes: bytes) -> tuple[np.ndarray | None, float]:
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        return None, 0.0

    detections = detect_faces(frame)
    if not detections:
        return None, 0.0
    detection = detections[0]
    return extract_feature(frame, detection), detection.score


def vector_to_bytes(vector: np.ndarray) -> bytes:
    vec = np.asarray(vector, dtype=np.float32).reshape(-1)
    return vec.tobytes()


def bytes_to_vector(data: bytes) -> np.ndarray:
    vec = np.frombuffer(data, dtype=np.float32).copy()
    if vec.size != SFACE_DIM:
        raise ValueError(f"Vecteur SFace invalide: {vec.size} dimensions")
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.astype(np.float32)


def cosine_to_confidence(cosine: float) -> float:
    # Map readable 0-100. Values below 0.35 are not useful matches; >=0.75 is excellent.
    score = (float(cosine) - 0.35) / 0.40 * 100.0
    return round(float(np.clip(score, 0.0, 100.0)), 1)


def _group_by_student(
    embeddings: list[tuple[int, np.ndarray]],
) -> dict[int, np.ndarray]:
    grouped: dict[int, list[np.ndarray]] = defaultdict(list)
    for student_id, vector in embeddings:
        grouped[student_id].append(vector)
    return {student_id: np.stack(vectors) for student_id, vectors in grouped.items()}


def _score_student(query_vector: np.ndarray, student_id: int, matrix: np.ndarray) -> SFaceCandidate:
    similarities = matrix @ query_vector.reshape(-1, 1)
    similarities = similarities.reshape(-1)
    order = np.argsort(similarities)[::-1]
    top_n = min(MIN_TOP_SAMPLES, len(order))
    top = similarities[order[:top_n]]
    if len(top) == 1:
        cosine = float(top[0])
    else:
        cosine = float(0.70 * top[0] + 0.30 * np.mean(top[1:]))
    return SFaceCandidate(
        student_id=student_id,
        cosine=cosine,
        best_cosine=float(top[0]),
        samples=int(len(order)),
    )


def rank_matches(
    query_vector: np.ndarray,
    embeddings: list[tuple[int, np.ndarray]],
) -> list[SFaceCandidate]:
    if not embeddings:
        return []
    grouped = _group_by_student(embeddings)
    candidates = [
        _score_student(query_vector, student_id, matrix)
        for student_id, matrix in grouped.items()
    ]
    candidates.sort(key=lambda item: item.cosine, reverse=True)
    if candidates:
        second = candidates[1].cosine if len(candidates) > 1 else 0.0
        best = candidates[0]
        candidates[0] = SFaceCandidate(
            student_id=best.student_id,
            cosine=best.cosine,
            best_cosine=best.best_cosine,
            margin=best.cosine - second,
            samples=best.samples,
        )
    return candidates


def is_auto_match(candidate: SFaceCandidate) -> bool:
    return (
        candidate.cosine >= SFACE_AUTO_ACCEPT_THRESHOLD
        and candidate.margin >= SFACE_AMBIGUITY_MARGIN
    )
