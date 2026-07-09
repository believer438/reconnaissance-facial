"""
Gestion de l'état d'entraînement LBPH en arrière-plan.

- start_training_async()   : lance l'entraînement dans un thread séparé
- schedule_auto_retrain()  : version debounce (attend N secondes après la dernière photo)
- get_state()              : état actuel (dict JSON-serialisable)
"""
from __future__ import annotations

import threading
import time as _time
from datetime import datetime

_lock = threading.Lock()
_debounce_timer: threading.Timer | None = None

_state: dict = {
    "status": "idle",        # "idle" | "running" | "success" | "error"
    "triggered_by": None,    # "manual" | "auto"
    "last_run": None,        # ISO string
    "students": 0,
    "faces": 0,
    "duration": 0.0,
    "error": None,
}


def get_state() -> dict:
    with _lock:
        return dict(_state)


def _run_training(triggered_by: str = "manual") -> None:
    global _state
    with _lock:
        _state = {**_state, "status": "running", "error": None, "triggered_by": triggered_by}

    t_start = _time.monotonic()
    try:
        from apps.attendance.services.training import train_model
        summary = train_model()
        duration = round(_time.monotonic() - t_start, 2)
        with _lock:
            _state.update({
                "status": "success",
                "last_run": datetime.now().isoformat(timespec="seconds"),
                "students": summary.students,
                "faces": summary.faces,
                "duration": duration,
                "error": None,
            })
        try:
            from apps.attendance.models import TrainingHistory
            TrainingHistory.objects.create(
                triggered_by=triggered_by,
                success=True,
                nb_students=summary.students,
                nb_photos=summary.faces,
                nb_skipped_blurry=summary.skipped_blurry,
                duration_seconds=duration,
            )
        except Exception:
            pass
    except Exception as exc:
        duration = round(_time.monotonic() - t_start, 2)
        with _lock:
            _state.update({
                "status": "error",
                "last_run": datetime.now().isoformat(timespec="seconds"),
                "error": str(exc)[:300],
                "duration": duration,
            })
        try:
            from apps.attendance.models import TrainingHistory
            TrainingHistory.objects.create(
                triggered_by=triggered_by,
                success=False,
                error_message=str(exc)[:1000],
                duration_seconds=duration,
            )
        except Exception:
            pass


def start_training_async(triggered_by: str = "manual") -> bool:
    """Lance l'entraînement en arrière-plan. Retourne False si déjà en cours."""
    with _lock:
        if _state["status"] == "running":
            return False
    t = threading.Thread(target=_run_training, args=(triggered_by,), daemon=True, name="lbph-trainer")
    t.start()
    return True


def schedule_auto_retrain(delay_seconds: int = 6) -> None:
    """
    Déclenche un entraînement automatique après un délai (debounce).
    Si plusieurs photos sont ajoutées rapidement, un seul entraînement est lancé.
    """
    global _debounce_timer
    with _lock:
        if _debounce_timer is not None:
            _debounce_timer.cancel()
        _debounce_timer = threading.Timer(
            delay_seconds,
            lambda: start_training_async("auto"),
        )
        _debounce_timer.daemon = True
        _debounce_timer.start()
