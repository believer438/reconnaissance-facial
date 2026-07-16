from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Classes
    path("classes/", views.classe_list, name="classe_list"),
    path("classes/<int:classe_id>/", views.classe_detail, name="classe_detail"),
    path("classes/<int:classe_id>/delete/", views.classe_delete, name="classe_delete"),

    # Salles
    path("salles/", views.salle_list, name="salle_list"),
    path("salles/<int:salle_id>/delete/", views.salle_delete, name="salle_delete"),

    # Jours feries
    path("jours-feries/", views.jours_feries_list, name="jours_feries_list"),
    path("jours-feries/<int:jour_id>/delete/", views.jours_feries_delete, name="jours_feries_delete"),

    # Students
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.student_create, name="student_create"),
    path("students/<int:student_id>/", views.student_detail, name="student_detail"),
    path("students/<int:student_id>/edit/", views.student_edit, name="student_edit"),
    path("students/<int:student_id>/delete/", views.student_delete, name="student_delete"),
    path("students/<int:student_id>/photos/", views.student_add_photos, name="student_add_photos"),
    path("photos/<int:photo_id>/delete/", views.photo_delete, name="photo_delete"),
    path("api/student-code/check/", views.api_student_code_check, name="api_student_code_check"),

    # Courses
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),
    path("courses/<int:course_id>/delete/", views.course_delete, name="course_delete"),
    path("courses/<int:course_id>/enroll/", views.enrollment_add, name="enrollment_add"),
    path("enrollments/<int:enrollment_id>/remove/", views.enrollment_remove, name="enrollment_remove"),

    # Sessions
    path("courses/<int:course_id>/sessions/add/", views.session_create, name="session_create"),
    path("sessions/<int:session_id>/", views.session_detail, name="session_detail"),
    path("sessions/<int:session_id>/open/", views.session_open, name="session_open"),
    path("sessions/<int:session_id>/close/", views.session_close, name="session_close"),
    path("sessions/<int:session_id>/cancel/", views.session_cancel, name="session_cancel"),
    path("sessions/<int:session_id>/mark-absent/", views.session_mark_absent, name="session_mark_absent"),
    path("sessions/<int:session_id>/delete/", views.session_delete, name="session_delete"),

    # Cameras
    path("cameras/", views.camera_list, name="camera_list"),
    path("cameras/monitor/", views.camera_monitor, name="camera_monitor"),
    path("cameras/<int:camera_id>/edit/", views.camera_edit, name="camera_edit"),
    path("cameras/<int:camera_id>/delete/", views.camera_delete, name="camera_delete"),
    path("cameras/<int:camera_id>/live/", views.camera_live, name="camera_live"),

    # API (AJAX — exempt du middleware login pour le navigateur caméra)
    path("api/recognize-frame/", views.api_recognize_frame, name="api_recognize_frame"),

    # ── Diagnostic de reconnaissance ─────────────────────────────────────────
    path("diagnostic/", views.diagnostic_view, name="diagnostic"),
    path("api/diagnostic/", views.api_diagnostic, name="api_diagnostic"),

    # Schedules
    path("schedules/", views.schedule_list, name="schedule_list"),
    path("schedules/<int:schedule_id>/delete/", views.schedule_delete, name="schedule_delete"),

    # Attendance
    path("attendance/", views.attendance_list, name="attendance_list"),
    path("attendance/<int:record_id>/edit/", views.attendance_edit, name="attendance_edit"),

    # Reports & exports
    path("reports/", views.report_view, name="reports"),
    path("reports/export/excel/", views.export_excel, name="export_excel"),

    # Unknown faces
    path("unknown-faces/", views.unknown_faces_view, name="unknown_faces"),
    path("unknown-faces/<int:log_id>/delete/", views.unknown_face_delete, name="unknown_face_delete"),

    # Training & recognition
    path("actions/train/", views.train_model_view, name="train_model"),
    path("actions/rebuild-embeddings/", views.rebuild_all_embeddings_view, name="rebuild_embeddings"),
    path("api/train/status/", views.api_train_status, name="api_train_status"),
    path("api/train/retrain/", views.api_retrain_async, name="api_retrain_async"),
    path("recognition/", views.recognize_upload_view, name="recognize_upload"),
    path("actions/recognize/", views.recognize_view, name="recognize"),

    # ── Configuration systeme ─────────────────────────────────────────────────
    path("config/", views.system_config_view, name="system_config"),

    # ── Journal d'evenements bruts ────────────────────────────────────────────
    path("events/", views.detection_events_view, name="detection_events"),

    # ── Statistiques par classe ───────────────────────────────────────────────
    path("stats/classes/", views.stats_classe_view, name="stats_classe"),

    # ── Journal d'activité système ────────────────────────────────────────────
    path("journal/", views.system_log_view, name="system_log"),

    # ── Gestion des utilisateurs ──────────────────────────────────────────────
    path("administration/", views.administration_dashboard, name="administration_dashboard"),
    path("utilisateurs/", views.user_list, name="user_list"),
    path("utilisateurs/creer/", views.user_create, name="user_create"),
    path("utilisateurs/<int:user_id>/modifier/", views.user_edit, name="user_edit"),
    path("utilisateurs/<int:user_id>/toggle/", views.user_toggle_active, name="user_toggle_active"),
    path("utilisateurs/<int:user_id>/reset-mdp/", views.user_reset_password, name="user_reset_password"),

    # ── File de revue reconnaissance ──────────────────────────────────────────
    path("review/", views.review_queue_list, name="review_queue_list"),
    path("review/<int:ticket_id>/", views.review_queue_detail, name="review_queue_detail"),

    # ── Contrôle des caméras ──────────────────────────────────────────────────
    path("cameras/control/", views.camera_control_panel, name="camera_control_panel"),
    path("cameras/<int:camera_id>/mode/", views.camera_set_mode, name="camera_set_mode"),
    path("api/camera/<int:camera_id>/heartbeat/", views.api_camera_heartbeat, name="api_camera_heartbeat"),
    path("api/cameras/status/", views.api_cameras_status, name="api_cameras_status"),

    # ── ECOLE SECONDAIRE : Presence journaliere ───────────────────────────────
    path("daily/list/", views.daily_attendance_list, name="daily_attendance_list"),
    path("daily/<int:record_id>/edit/", views.daily_attendance_edit, name="daily_attendance_edit"),
    path("daily/generate-absents/", views.daily_generate_absents, name="daily_generate_absents"),
    path("daily/config/", views.school_day_config_view, name="school_day_config"),
]
