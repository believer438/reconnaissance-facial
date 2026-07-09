"""
Commande de gestion automatique de la présence journalière.

Usage:
    python manage.py auto_daily [--generate-absents] [--check-school-day]

Peut être lancé automatiquement via un cron ou un scheduler.
Pour programmer l'exécution automatique, ajouter dans le système:
    0 16 * * 1-5  cd /path/to/app && python manage.py auto_daily --generate-absents
"""
from __future__ import annotations

import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Gestion automatique de la présence journalière (école secondaire)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--generate-absents",
            action="store_true",
            help="Génère les enregistrements ABSENT pour les élèves sans présence aujourd'hui",
        )
        parser.add_argument(
            "--check-school-day",
            action="store_true",
            help="Vérifie si aujourd'hui est un jour de classe et affiche le statut",
        )
        parser.add_argument(
            "--date",
            type=str,
            default=None,
            help="Date cible (format YYYY-MM-DD). Défaut : aujourd'hui",
        )

    def handle(self, *args, **options):
        from apps.attendance.models import (
            DailyAttendance,
            JourFerie,
            SchoolDayConfig,
            Student,
            SystemLog,
        )

        target_date: datetime.date
        if options["date"]:
            try:
                target_date = datetime.date.fromisoformat(options["date"])
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Format de date invalide : {options['date']}. Utilisez YYYY-MM-DD."))
                return
        else:
            target_date = timezone.localdate()

        config = SchoolDayConfig.get()
        is_school_day = config.is_school_day(target_date)
        is_ferie = JourFerie.is_ferie(target_date)

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  SecPresence — Gestion journalière")
        self.stdout.write(f"  Date : {target_date.strftime('%A %d/%m/%Y')}")
        self.stdout.write(f"  Jour de classe : {'OUI' if is_school_day else 'NON'}")
        self.stdout.write(f"  Jour férié/vacances : {'OUI' if is_ferie else 'NON'}")
        self.stdout.write(f"{'='*60}\n")

        if options["check_school_day"]:
            if not is_school_day or is_ferie:
                self.stdout.write(self.style.WARNING("Pas de cours ce jour. Aucune action effectuée."))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"Jour de classe — Cours de {config.heure_debut_cours} à {config.heure_fin_cours}. "
                    f"Limite retard : {config.heure_limite_arrivee}"
                ))
            return

        if options["generate_absents"]:
            if not is_school_day:
                self.stdout.write(self.style.WARNING(
                    f"Pas un jour de classe ({target_date.strftime('%A')}). Génération annulée."
                ))
                return
            if is_ferie:
                self.stdout.write(self.style.WARNING(
                    "Jour férié / vacances. Génération annulée."
                ))
                return
            if target_date == timezone.localdate() and timezone.localtime().time() <= config.heure_fin_cours:
                self.stdout.write(self.style.WARNING(
                    f"Fin des cours non atteinte ({config.heure_fin_cours}). Génération annulée."
                ))
                return

            all_active = Student.objects.filter(is_active=True)
            present_ids = set(
                DailyAttendance.objects.filter(date=target_date).values_list("student_id", flat=True)
            )
            absent_students = all_active.exclude(id__in=present_ids)
            count = 0

            for student in absent_students:
                DailyAttendance.objects.create(
                    student=student,
                    date=target_date,
                    status=DailyAttendance.STATUS_ABSENT,
                    modified_by="Système (auto_daily)",
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(
                f"{count} absence(s) générée(s) automatiquement pour le {target_date.strftime('%d/%m/%Y')}."
            ))

            # Journaliser
            try:
                SystemLog.objects.create(
                    user="system",
                    action=SystemLog.ACTION_OTHER,
                    object_type=SystemLog.OBJ_ATTENDANCE,
                    object_repr=f"Génération absences {target_date}",
                    details=f"{count} absences générées automatiquement par auto_daily",
                    success=True,
                )
            except Exception:
                pass

            # Résumé
            total = all_active.count()
            enregistres = DailyAttendance.objects.filter(date=target_date).count()
            self.stdout.write(f"\nRésumé pour {target_date.strftime('%d/%m/%Y')} :")
            self.stdout.write(f"  Total élèves actifs : {total}")
            self.stdout.write(f"  Enregistrements présence : {enregistres}")
            presents = DailyAttendance.objects.filter(date=target_date, status=DailyAttendance.STATUS_PRESENT).count()
            retards = DailyAttendance.objects.filter(date=target_date, status=DailyAttendance.STATUS_RETARD).count()
            absents = DailyAttendance.objects.filter(date=target_date, status=DailyAttendance.STATUS_ABSENT).count()
            self.stdout.write(f"  Présents   : {presents}")
            self.stdout.write(f"  Retards    : {retards}")
            self.stdout.write(f"  Absents    : {absents}")
            return

        self.stdout.write("Options disponibles :")
        self.stdout.write("  --generate-absents   Générer les absences de la journée")
        self.stdout.write("  --check-school-day   Vérifier si aujourd'hui est un jour de classe")
        self.stdout.write("  --date YYYY-MM-DD    Spécifier une date cible\n")
        self.stdout.write("Exemple cron (lundi-vendredi à 16h30) :")
        self.stdout.write("  30 16 * * 1-5  python manage.py auto_daily --generate-absents\n")
