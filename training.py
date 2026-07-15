import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.attendance.services.training import train_model


if __name__ == "__main__":
    try:
        summary = train_model()
    except Exception as exc:
        print(f"Erreur entrainement: {exc}")
        raise SystemExit(1)

    print(
        f"Modele entraine: {summary.students} eleve(s), "
        f"{summary.photos} photo(s), {summary.faces} visage(s)."
    )
