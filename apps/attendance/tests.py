import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import NoReverseMatch, reverse

from .models import Camera, Classe, DailyAttendance, FaceDetectionEvent, JourFerie, SchoolDayConfig, Student, TrainingPhoto
from .services.daily_attendance import generate_absences_for_date, register_check_in
from .views import _daily_arrival_status


class AuthenticatedTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin-test",
            password="pass-test",
            is_staff=True,
        )
        self.client.force_login(self.user)


class DashboardTests(AuthenticatedTestCase):
    def test_dashboard_loads_as_main_attendance_dashboard(self):
        response = self.client.get(reverse("attendance:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tableau de bord")
        self.assertContains(response, "Presence journaliere")
        self.assertNotContains(response, "Dernieres presences")

    def test_removed_daily_dashboard_route_is_not_reversible(self):
        with self.assertRaises(NoReverseMatch):
            reverse("attendance:daily_dashboard")


class StudentCreationTests(AuthenticatedTestCase):
    def test_create_student_without_photos(self):
        response = self.client.post(
            reverse("attendance:student_create"),
            {
                "nom": "Kalala",
                "post_nom": "",
                "prenom": "Amani",
                "student_code": "AK-001",
                "statut": "actif",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Student.objects.filter(student_code="AK-001").exists())
        self.assertEqual(TrainingPhoto.objects.count(), 0)

    def test_student_detail_uses_daily_attendance_scores(self):
        student = Student.objects.create(
            nom="Muete",
            prenom="Believer",
            student_code="SM-001",
            statut="actif",
        )
        DailyAttendance.objects.create(
            student=student,
            date=datetime.date(2026, 6, 1),
            status=DailyAttendance.STATUS_PRESENT,
            heure_entree=datetime.time(7, 10),
        )
        DailyAttendance.objects.create(
            student=student,
            date=datetime.date(2026, 6, 2),
            status=DailyAttendance.STATUS_ABSENT,
        )

        response = self.client.get(reverse("attendance:student_detail", args=[student.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "50,0%")
        self.assertContains(response, "1 présent")
        self.assertContains(response, "1</span> sur 2 jour")


class DailyAttendanceRuleTests(TestCase):
    def test_arrival_status_uses_configured_late_limit(self):
        config = SchoolDayConfig(
            heure_limite_arrivee=datetime.time(7, 30),
            heure_fin_cours=datetime.time(12, 0),
        )

        self.assertEqual(
            _daily_arrival_status(datetime.time(7, 30), config),
            DailyAttendance.STATUS_PRESENT,
        )
        self.assertEqual(
            _daily_arrival_status(datetime.time(7, 31), config),
            DailyAttendance.STATUS_RETARD,
        )

    def test_checkin_records_first_arrival_and_status_from_saved_time(self):
        config = SchoolDayConfig.get()
        config.heure_ouverture = datetime.time(6, 30)
        config.heure_limite_arrivee = datetime.time(7, 30)
        config.heure_fin_cours = datetime.time(15, 30)
        config.lundi = True
        config.save()
        student = Student.objects.create(nom="Kalala", prenom="Amani", student_code="AK-010", statut="actif")
        camera = Camera.objects.create(name="Entree", zone_type=Camera.ZONE_CHECK_IN)
        late_time = timezone.make_aware(datetime.datetime(2026, 6, 1, 7, 31, 12))

        outcome = register_check_in(student, camera, config=config, now=late_time, confidence=91.5)

        self.assertTrue(outcome.saved)
        self.assertEqual(outcome.record.status, DailyAttendance.STATUS_RETARD)
        self.assertEqual(outcome.record.heure_entree, datetime.time(7, 31, 12))
        self.assertTrue(FaceDetectionEvent.objects.filter(etape=FaceDetectionEvent.ETAPE_ENREGISTRE).exists())

    def test_configured_arrival_windows_present_retard_absent(self):
        config = SchoolDayConfig.get()
        config.heure_ouverture = datetime.time(6, 30)
        config.heure_limite_arrivee = datetime.time(10, 0)
        config.heure_fin_cours = datetime.time(13, 0)
        config.lundi = True
        config.save()
        present_student = Student.objects.create(nom="Kanku", prenom="Mina", student_code="KM-010", statut="actif")
        late_student = Student.objects.create(nom="Tshibanda", prenom="Noah", student_code="TN-010", statut="actif")
        absent_student = Student.objects.create(nom="Banza", prenom="Lina", student_code="BL-010", statut="actif")

        at_limit = timezone.make_aware(datetime.datetime(2026, 6, 1, 10, 0, 0))
        after_limit = timezone.make_aware(datetime.datetime(2026, 6, 1, 10, 1, 0))
        after_end = timezone.make_aware(datetime.datetime(2026, 6, 1, 13, 1, 0))

        present = register_check_in(present_student, config=config, now=at_limit, log_event=False)
        late = register_check_in(late_student, config=config, now=after_limit, log_event=False)
        absences = generate_absences_for_date(
            datetime.date(2026, 6, 1),
            config=config,
            now=after_end,
            modified_by="Test",
        )

        self.assertEqual(present.record.status, DailyAttendance.STATUS_PRESENT)
        self.assertEqual(late.record.status, DailyAttendance.STATUS_RETARD)
        self.assertFalse(absences.blocked)
        self.assertEqual(absences.count, 1)
        self.assertEqual(
            DailyAttendance.objects.get(student=absent_student, date=datetime.date(2026, 6, 1)).status,
            DailyAttendance.STATUS_ABSENT,
        )

    def test_absences_are_not_generated_before_course_end(self):
        config = SchoolDayConfig.get()
        config.heure_ouverture = datetime.time(6, 30)
        config.heure_limite_arrivee = datetime.time(10, 0)
        config.heure_fin_cours = datetime.time(13, 0)
        config.lundi = True
        config.save()
        Student.objects.create(nom="Kasongo", prenom="Ari", student_code="KA-011", statut="actif")
        before_end = timezone.make_aware(datetime.datetime(2026, 6, 1, 12, 59, 0))

        outcome = generate_absences_for_date(datetime.date(2026, 6, 1), config=config, now=before_end)

        self.assertTrue(outcome.blocked)
        self.assertEqual(DailyAttendance.objects.count(), 0)

    def test_checkin_duplicate_keeps_original_arrival_time(self):
        config = SchoolDayConfig.get()
        config.heure_ouverture = datetime.time(6, 30)
        config.heure_limite_arrivee = datetime.time(7, 30)
        config.heure_fin_cours = datetime.time(15, 30)
        config.lundi = True
        config.save()
        student = Student.objects.create(nom="Ilunga", prenom="Nora", student_code="IN-010", statut="actif")
        first = timezone.make_aware(datetime.datetime(2026, 6, 1, 7, 12, 0))
        second = timezone.make_aware(datetime.datetime(2026, 6, 1, 8, 5, 0))

        register_check_in(student, config=config, now=first, log_event=False)
        duplicate = register_check_in(student, config=config, now=second, log_event=False)

        record = DailyAttendance.objects.get(student=student, date=datetime.date(2026, 6, 1))
        self.assertTrue(duplicate.duplicate)
        self.assertEqual(record.status, DailyAttendance.STATUS_PRESENT)
        self.assertEqual(record.heure_entree, datetime.time(7, 12))

    def test_checkin_does_not_overwrite_manual_excuse(self):
        config = SchoolDayConfig.get()
        config.heure_ouverture = datetime.time(6, 30)
        config.heure_limite_arrivee = datetime.time(7, 30)
        config.heure_fin_cours = datetime.time(15, 30)
        config.lundi = True
        config.save()
        student = Student.objects.create(nom="Mbuyi", prenom="Lea", student_code="ML-010", statut="actif")
        DailyAttendance.objects.create(
            student=student,
            date=datetime.date(2026, 6, 1),
            status=DailyAttendance.STATUS_EXCUSE,
            excuse_reason="maladie",
            modified_by="Secretariat",
        )
        now = timezone.make_aware(datetime.datetime(2026, 6, 1, 7, 10, 0))

        outcome = register_check_in(student, config=config, now=now, log_event=False)

        record = DailyAttendance.objects.get(student=student, date=datetime.date(2026, 6, 1))
        self.assertEqual(outcome.op, "manual_excuse")
        self.assertEqual(record.status, DailyAttendance.STATUS_EXCUSE)
        self.assertIsNone(record.heure_entree)


class SchoolCalendarTests(AuthenticatedTestCase):
    def test_holiday_does_not_list_all_students_as_missing(self):
        Student.objects.create(
            nom="Kalala",
            prenom="Amani",
            student_code="AK-002",
            statut="actif",
        )
        JourFerie.objects.create(
            nom="Congé test",
            date=datetime.date(2026, 6, 5),
            type_jour=JourFerie.TYPE_FERIE,
        )

        response = self.client.get(
            reverse("attendance:daily_attendance_list"),
            {"date": "2026-06-05"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucune absence automatique")
        self.assertNotContains(response, "Non enregistres aujourd'hui")

    def test_class_stats_do_not_turn_blocked_day_missing_students_into_absent(self):
        classe = Classe.objects.create(nom="1ere A", niveau="1ere")
        Student.objects.create(
            nom="Kalala",
            prenom="Amani",
            student_code="AK-003",
            statut="actif",
            classe=classe,
        )
        JourFerie.objects.create(
            nom="Congé stats",
            date=datetime.date(2026, 6, 5),
            type_jour=JourFerie.TYPE_FERIE,
        )

        response = self.client.get(reverse("attendance:stats_classe"), {"date": "2026-06-05"})

        self.assertEqual(response.status_code, 200)
        row = response.context["rows"][0]
        self.assertEqual(row["nb_absent"], 0)
        self.assertEqual(row["nb_missing"], 1)
        self.assertContains(response, "Stats informatives uniquement")
