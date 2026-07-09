from datetime import time

from django.core.management.base import BaseCommand

from apps.attendance.models import ClassroomSchedule


class Command(BaseCommand):
    help = "Ajoute quelques horaires locaux si la base est vide."

    def handle(self, *args, **options):
        defaults = [
            ("L3 Info", time(8, 0), 5),
            ("L2 Info", time(8, 30), 10),
            ("M1 Data", time(9, 0), 10),
        ]
        created = 0
        for classroom, start_time, late_after in defaults:
            _, was_created = ClassroomSchedule.objects.get_or_create(
                classroom=classroom,
                defaults={
                    "start_time": start_time,
                    "late_after_minutes": late_after,
                },
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f"{created} horaire(s) initialise(s)."))
