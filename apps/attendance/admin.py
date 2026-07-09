from django.contrib import admin

from .models import (
    AttendanceAuditLog,
    AttendanceRecord,
    Classe,
    ClassroomSchedule,
    Course,
    CourseSession,
    DailyAttendance,
    FaceDetectionEvent,
    JourFerie,
    RecognitionReviewQueue,
    Salle,
    Schedule,
    SchoolDayConfig,
    Student,
    SystemConfig,
    SystemLog,
    TrainingHistory,
    TrainingPhoto,
    UnknownFaceLog,
)


class TrainingPhotoInline(admin.TabularInline):
    model = TrainingPhoto
    extra = 1
    readonly_fields = ("trained_at", "face_detected")


class AttendanceAuditLogInline(admin.TabularInline):
    model = AttendanceAuditLog
    extra = 0
    readonly_fields = ("modifie_par", "ancienne_valeur", "nouvelle_valeur", "raison", "date_modification")
    can_delete = False


# ── École secondaire ──────────────────────────────────────────────────────────

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "object_type", "object_repr", "ip_address", "success")
    list_filter = ("action", "object_type", "success")
    search_fields = ("user", "object_repr", "details")
    readonly_fields = ("created_at", "user", "action", "object_type", "object_id", "object_repr", "details", "ip_address", "success")
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(TrainingHistory)
class TrainingHistoryAdmin(admin.ModelAdmin):
    list_display = ("started_at", "triggered_by", "nb_students", "nb_photos", "nb_skipped_blurry", "duration_seconds", "success")
    list_filter = ("success",)
    readonly_fields = ("started_at", "completed_at", "triggered_by", "nb_students", "nb_photos", "nb_skipped_blurry", "duration_seconds", "success", "error_message")
    ordering = ["-started_at"]
    date_hierarchy = "started_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(RecognitionReviewQueue)
class RecognitionReviewQueueAdmin(admin.ModelAdmin):
    list_display = (
        "id", "student_proposed", "confidence_proposed", "distance_lbph",
        "technical_status", "camera", "status", "reviewed_by", "detected_at",
    )
    list_filter = ("status", "technical_status")
    search_fields = ("student_proposed__full_name", "student_proposed__student_code")
    readonly_fields = ("detected_at", "face_image")
    ordering = ["-detected_at"]
    date_hierarchy = "detected_at"

    def has_add_permission(self, request):
        return False


@admin.register(SchoolDayConfig)
class SchoolDayConfigAdmin(admin.ModelAdmin):
    list_display = (
        "nom", "heure_ouverture", "heure_debut_cours", "heure_limite_arrivee",
        "heure_fin_cours", "heure_fermeture",
        "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi",
    )
    fieldsets = (
        ("Identification", {"fields": ("nom",)}),
        ("Horaires journaliers", {
            "fields": (
                "heure_ouverture", "heure_debut_cours", "heure_limite_arrivee",
                "heure_fin_cours", "heure_fermeture",
            ),
        }),
        ("Jours de classe", {
            "fields": ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"),
        }),
    )

    def has_add_permission(self, request):
        return not SchoolDayConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "student", "date", "status", "heure_entree",
        "camera_entree", "excuse_reason", "modified_by",
    )
    list_filter = ("status", "date", "excuse_reason")
    search_fields = ("student__full_name", "student__student_code")
    date_hierarchy = "date"
    ordering = ["-date", "student__full_name"]
    readonly_fields = ("created_at", "updated_at")


# ── Système ───────────────────────────────────────────────────────────────────

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = (
        "retard_minutes", "ouverture_avant_minutes", "cooldown_detection_minutes",
        "seuil_distance_lbph", "seuil_alerte_absences", "filtrer_par_classe",
        "archiver_evenements_bruts", "updated_at",
    )
    fieldsets = (
        ("Regles temporelles", {
            "fields": ("retard_minutes", "ouverture_avant_minutes", "cooldown_detection_minutes"),
        }),
        ("Reconnaissance faciale", {
            "fields": ("seuil_distance_lbph", "filtrer_par_classe"),
        }),
        ("Alertes & journalisation", {
            "fields": ("seuil_alerte_absences", "archiver_evenements_bruts"),
        }),
    )

    def has_add_permission(self, request):
        return not SystemConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FaceDetectionEvent)
class FaceDetectionEventAdmin(admin.ModelAdmin):
    list_display = ("detected_at", "etape", "student", "confiance", "source", "raison", "course_session")
    list_filter = ("etape", "source")
    search_fields = ("student__full_name", "student__student_code", "raison")
    readonly_fields = ("detected_at",)
    ordering = ["-detected_at"]
    date_hierarchy = "detected_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ── Structure scolaire ────────────────────────────────────────────────────────

@admin.register(JourFerie)
class JourFerieAdmin(admin.ModelAdmin):
    list_display = ("nom", "date", "type_jour")
    list_filter = ("type_jour",)
    ordering = ["date"]
    search_fields = ("nom",)


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ("nom", "batiment", "capacite", "is_active")
    list_filter = ("is_active", "batiment")
    search_fields = ("nom", "batiment")


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ("nom", "niveau", "option", "annee_academique", "is_active")
    list_filter = ("is_active", "annee_academique")
    search_fields = ("nom", "niveau", "option")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "student_code", "classe", "faculty", "is_active", "created_at")
    list_filter = ("classe", "faculty", "is_active")
    search_fields = ("full_name", "student_code")
    inlines = [TrainingPhotoInline]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("classe", "course", "salle", "jour_semaine", "heure_debut", "heure_fin", "tolerance_retard_minutes", "is_active")
    list_filter = ("classe", "course", "jour_semaine", "is_active")
    search_fields = ("classe__nom", "course__code", "course__professor")


@admin.register(ClassroomSchedule)
class ClassroomScheduleAdmin(admin.ModelAdmin):
    list_display = ("classroom", "start_time", "late_after_minutes")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "professor", "faculty", "credits")
    search_fields = ("code", "name", "professor")


@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ("course", "date", "start_time", "end_time", "status", "room")
    list_filter = ("status", "date")
    search_fields = ("course__code", "course__name")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "student_name_snapshot", "classroom_snapshot", "status", "excuse_reason",
        "confidence_score", "recognized_at", "source", "modified_by",
    )
    list_filter = ("status", "excuse_reason", "source")
    search_fields = ("student_name_snapshot",)
    inlines = [AttendanceAuditLogInline]
    readonly_fields = ("recognized_at",)


@admin.register(AttendanceAuditLog)
class AttendanceAuditLogAdmin(admin.ModelAdmin):
    list_display = ("attendance_record", "modifie_par", "ancienne_valeur", "nouvelle_valeur", "date_modification")
    list_filter = ("ancienne_valeur", "nouvelle_valeur")
    search_fields = ("modifie_par", "raison")
    readonly_fields = ("date_modification",)


@admin.register(UnknownFaceLog)
class UnknownFaceLogAdmin(admin.ModelAdmin):
    list_display = ("detected_at", "source", "camera", "notes")
    list_filter = ("source",)
