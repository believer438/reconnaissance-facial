from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import (
    Camera,
    DailyAttendance,
    FaceDetectionEvent,
    JourFerie,
    SchoolDayConfig,
    Student,
    SystemConfig,
)


@dataclass(frozen=True)
class DailyCheckInResult:
    record: DailyAttendance | None
    op: str
    saved: bool = False
    refused: bool = False
    duplicate: bool = False
    message: str = ""


@dataclass(frozen=True)
class AbsenceGenerationResult:
    count: int
    blocked: bool = False
    message: str = ""


def _as_time(value) -> time:
    if isinstance(value, time):
        return value.replace(tzinfo=None, microsecond=0)
    if isinstance(value, str):
        parts = [int(p) for p in value.split(":")]
        while len(parts) < 3:
            parts.append(0)
        return time(parts[0], parts[1], parts[2])
    return value


def day_block_reason(date, config: SchoolDayConfig | None = None) -> str:
    config = config or SchoolDayConfig.get()
    if JourFerie.is_ferie(date):
        jour = JourFerie.objects.filter(date=date).first()
        return f"Jour non ouvrable: {jour.nom if jour else 'jour ferie'}"
    if not config.is_school_day(date):
        return "Jour non scolaire selon la configuration"
    return ""


def time_block_reason(now_time: time, config: SchoolDayConfig | None = None) -> str:
    config = config or SchoolDayConfig.get()
    heure_ouverture = _as_time(config.heure_ouverture)
    heure_fermeture = _as_time(config.heure_fermeture)
    if now_time < heure_ouverture:
        return f"Portail pas encore ouvert ({heure_ouverture:%H:%M})"
    if now_time > heure_fermeture:
        return f"Portail ferme ({heure_fermeture:%H:%M})"
    return ""


def absence_generation_block_reason(date, now_time: time, config: SchoolDayConfig | None = None) -> str:
    config = config or SchoolDayConfig.get()
    blocked = day_block_reason(date, config)
    if blocked:
        return blocked
    heure_fin_cours = _as_time(config.heure_fin_cours)
    if date == timezone.localdate() and now_time <= heure_fin_cours:
        return f"Attendez la fin des cours ({heure_fin_cours:%H:%M})"
    return ""


def arrival_status(now_time: time, config: SchoolDayConfig | None = None) -> str:
    config = config or SchoolDayConfig.get()
    return (
        DailyAttendance.STATUS_PRESENT
        if now_time <= _as_time(config.heure_limite_arrivee)
        else DailyAttendance.STATUS_RETARD
    )


def generate_absences_for_date(
    date=None,
    *,
    config: SchoolDayConfig | None = None,
    now=None,
    modified_by: str = "Systeme (generation auto)",
) -> AbsenceGenerationResult:
    """
    Cree les absences de fin de cours pour tous les eleves actifs non traces.
    Ne touche jamais aux presences, retards ou excuses deja enregistres.
    """
    config = config or SchoolDayConfig.get()
    current = timezone.localtime(now or timezone.now())
    target_date = date or current.date()
    now_time = current.time().replace(tzinfo=None, microsecond=0)

    blocked = day_block_reason(target_date, config)
    heure_fin_cours = _as_time(config.heure_fin_cours)
    if not blocked and target_date == current.date() and now_time <= heure_fin_cours:
        blocked = f"Attendez la fin des cours ({heure_fin_cours:%H:%M})"
    if blocked:
        return AbsenceGenerationResult(0, blocked=True, message=blocked)

    present_ids = set(
        DailyAttendance.objects.filter(date=target_date).values_list("student_id", flat=True)
    )
    count = 0
    with transaction.atomic():
        for student in Student.objects.filter(is_active=True).exclude(id__in=present_ids):
            DailyAttendance.objects.create(
                student=student,
                date=target_date,
                status=DailyAttendance.STATUS_ABSENT,
                modified_by=modified_by,
            )
            count += 1
    return AbsenceGenerationResult(count, message=f"{count} absence(s) generee(s)")


def _log_event(
    etape: str,
    student: Student | None,
    camera: Camera | None,
    confiance: float,
    source: str,
    raison: str,
) -> None:
    try:
        if not SystemConfig.get().archiver_evenements_bruts:
            return
        FaceDetectionEvent.objects.create(
            student=student,
            camera=camera,
            etape=etape,
            confiance=round(confiance, 1),
            source=source,
            raison=raison[:200],
        )
    except Exception:
        pass


def register_check_in(
    student: Student,
    camera: Camera | None = None,
    *,
    config: SchoolDayConfig | None = None,
    source: str = "live",
    confidence: float = 0.0,
    now=None,
    log_event: bool = True,
) -> DailyCheckInResult:
    """
    Point d'entree unique pour l'arrivee journaliere.
    Ne remplace jamais une excuse manuelle et n'ecrase jamais une premiere heure.
    """
    config = config or SchoolDayConfig.get()
    current = timezone.localtime(now or timezone.now())
    target_date = current.date()
    now_time = current.time().replace(tzinfo=None, microsecond=0)

    blocked = day_block_reason(target_date, config) or time_block_reason(now_time, config)
    if blocked:
        if log_event:
            _log_event(FaceDetectionEvent.ETAPE_REFUSE, student, camera, confidence, source, blocked)
        return DailyCheckInResult(None, blocked, refused=True, message=blocked)

    existing = DailyAttendance.objects.filter(student=student, date=target_date).first()
    if existing and existing.status == DailyAttendance.STATUS_EXCUSE:
        msg = "Presence justifiee manuellement, non remplacee par la camera"
        if log_event:
            _log_event(FaceDetectionEvent.ETAPE_DOUBLON, student, camera, confidence, source, msg)
        return DailyCheckInResult(existing, "manual_excuse", duplicate=True, message=msg)

    if existing and existing.heure_entree is not None:
        msg = f"Arrivee deja enregistree a {existing.heure_entree:%H:%M:%S}"
        if log_event:
            _log_event(FaceDetectionEvent.ETAPE_DOUBLON, student, camera, confidence, source, msg)
        return DailyCheckInResult(existing, "doublon", duplicate=True, message=msg)

    heure_fin_cours = _as_time(config.heure_fin_cours)
    if now_time > heure_fin_cours:
        absences = generate_absences_for_date(
            target_date,
            config=config,
            now=current,
            modified_by="Systeme (reconnaissance apres fin des cours)",
        )
        existing = DailyAttendance.objects.filter(student=student, date=target_date).first()
        msg = (
            f"Reconnu apres la fin des cours ({heure_fin_cours:%H:%M}); "
            f"{absences.message if not absences.blocked else absences.message}"
        )
        if log_event:
            _log_event(FaceDetectionEvent.ETAPE_REFUSE, student, camera, confidence, source, msg)
        return DailyCheckInResult(existing, "after_end", refused=True, message=msg)

    status = arrival_status(now_time, config)
    with transaction.atomic():
        if existing:
            existing.heure_entree = now_time
            existing.status = status
            existing.camera_entree = camera
            existing.modified_by = f"Systeme (reconnaissance {source})"
            existing.save(update_fields=["heure_entree", "status", "camera_entree", "modified_by", "updated_at"])
            record = existing
            op = "updated"
        else:
            record = DailyAttendance.objects.create(
                student=student,
                date=target_date,
                heure_entree=now_time,
                status=status,
                camera_entree=camera,
                modified_by=f"Systeme (reconnaissance {source})",
            )
            op = "created"

    if log_event:
        label = dict(DailyAttendance.STATUS_CHOICES).get(status, status)
        _log_event(FaceDetectionEvent.ETAPE_ENREGISTRE, student, camera, confidence, source, f"Presence journaliere: {label}")
    return DailyCheckInResult(record, op, saved=True, message=f"Presence journaliere {status}")
