from pathlib import Path

import cv2


CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


def ensure_opencv_face_available() -> None:
    if not hasattr(cv2, "face"):
        raise RuntimeError("OpenCV face module indisponible. Installez opencv-contrib-python.")


def build_detector() -> cv2.CascadeClassifier:
    detector = cv2.CascadeClassifier(CASCADE_PATH)
    if detector.empty():
        raise RuntimeError("Impossible de charger le detecteur Haar Cascade.")
    return detector


def list_image_files(folder: Path) -> list[Path]:
    return [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    ]
