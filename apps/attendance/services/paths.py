from pathlib import Path

from django.conf import settings


MODEL_DIR = Path(settings.MEDIA_ROOT) / "models"
MODEL_FILE = MODEL_DIR / "trainer.yml"
LABEL_FILE = MODEL_DIR / "labels.json"
YUNET_MODEL_FILE = MODEL_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_MODEL_FILE = MODEL_DIR / "face_recognition_sface_2021dec.onnx"
