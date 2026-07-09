import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.attendance.services.recognition import run_camera_recognition


if __name__ == "__main__":
    try:
        summary = run_camera_recognition()
    except Exception as exc:
        print(f"Erreur reconnaissance: {exc}")
        raise SystemExit(1)

    print(
        f"Reconnaissance terminee: {summary.recognized_count} reconnu(s), "
        f"{summary.saved_records} presence(s) enregistree(s), "
        f"{summary.unknown_count} inconnu(s)."
    )
