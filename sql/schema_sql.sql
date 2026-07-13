-- ============================================================
-- UniPresence — Schema complet (SQLite)
-- Genere automatiquement depuis la base de donnees de production
-- ============================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Table: attendance_attendanceauditlog
CREATE TABLE "attendance_attendanceauditlog" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "modifie_par" varchar(120) NOT NULL, "ancienne_valeur" varchar(20) NOT NULL, "nouvelle_valeur" varchar(20) NOT NULL, "raison" text NOT NULL, "date_modification" datetime NOT NULL, "attendance_record_id" bigint NOT NULL REFERENCES "attendance_attendancerecord" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: attendance_attendancerecord
CREATE TABLE "attendance_attendancerecord" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "student_name_snapshot" varchar(120) NOT NULL, "classroom_snapshot" varchar(80) NOT NULL, "recognized_at" datetime NOT NULL, "confidence_score" real NOT NULL, "status" varchar(12) NOT NULL, "source" varchar(20) NOT NULL, "student_id" bigint NULL REFERENCES "attendance_student" (
    "id") DEFERRABLE INITIALLY DEFERRED, "course_session_id" bigint NULL REFERENCES "attendance_coursesession" (
    "id") DEFERRABLE INITIALLY DEFERRED, "camera_id" bigint NULL REFERENCES "attendance_camera" (
    "id") DEFERRABLE INITIALLY DEFERRED, "excuse_notes" text NOT NULL, "excuse_reason" varchar(20) NOT NULL, "modified_by" varchar(120) NOT NULL
);

-- Table: attendance_camera
CREATE TABLE "attendance_camera" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "location" varchar(150) NOT NULL, "camera_type" varchar(10) NOT NULL, "source" varchar(300) NOT NULL, "resolution_w" integer unsigned NOT NULL CHECK (
    "resolution_w" >= 0), "resolution_h" integer unsigned NOT NULL CHECK (
    "resolution_h" >= 0), "is_active" bool NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "salle_id" bigint NULL REFERENCES "attendance_salle" (
    "id") DEFERRABLE INITIALLY DEFERRED, "zone_type" varchar(12) NOT NULL, "detection_mode" varchar(16) NOT NULL, "error_count" integer unsigned NOT NULL CHECK (
    "error_count" >= 0), "fps_estimate" real NOT NULL, "frames_processed" integer unsigned NOT NULL CHECK (
    "frames_processed" >= 0), "is_online" bool NOT NULL, "last_error" varchar(500) NOT NULL, "last_seen" datetime NULL
);

-- Table: attendance_classe
CREATE TABLE "attendance_classe" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(100) NOT NULL, "niveau" varchar(50) NOT NULL, "option" varchar(100) NOT NULL, "annee_academique" varchar(20) NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL
);

-- Table: attendance_classroomschedule
CREATE TABLE "attendance_classroomschedule" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "classroom" varchar(80) NOT NULL UNIQUE, "start_time" time NOT NULL, "late_after_minutes" integer unsigned NOT NULL CHECK (
    "late_after_minutes" >= 0)
);

-- Table: attendance_course
CREATE TABLE "attendance_course" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "code" varchar(30) NOT NULL UNIQUE, "name" varchar(150) NOT NULL, "faculty" varchar(20) NOT NULL, "professor" varchar(120) NOT NULL, "credits" integer unsigned NOT NULL CHECK (
    "credits" >= 0), "created_at" datetime NOT NULL
);

-- Table: attendance_coursesession
CREATE TABLE "attendance_coursesession" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" date NOT NULL, "start_time" time NOT NULL, "end_time" time NULL, "room" varchar(80) NOT NULL, "late_after_minutes" integer unsigned NOT NULL CHECK (
    "late_after_minutes" >= 0), "notes" text NOT NULL, "closed" bool NOT NULL, "created_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "attendance_course" (
    "id") DEFERRABLE INITIALLY DEFERRED, "status" varchar(12) NOT NULL, "schedule_id" bigint NULL REFERENCES "attendance_schedule" (
    "id") DEFERRABLE INITIALLY DEFERRED, "minutes_avant_cours" integer unsigned NOT NULL CHECK (
    "minutes_avant_cours" >= 0), "motif_annulation" varchar(200) NOT NULL
);

-- Table: attendance_dailyattendance
CREATE TABLE "attendance_dailyattendance" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" date NOT NULL, "heure_entree" time NULL, "heure_sortie" time NULL, "status" varchar(20) NOT NULL, "modified_by" varchar(120) NOT NULL, "excuse_reason" varchar(50) NOT NULL, "excuse_notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "camera_entree_id" bigint NULL REFERENCES "attendance_camera" (
    "id") DEFERRABLE INITIALLY DEFERRED, "camera_sortie_id" bigint NULL REFERENCES "attendance_camera" (
    "id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "attendance_student" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: attendance_enrollment
CREATE TABLE "attendance_enrollment" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "enrolled_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "attendance_course" (
    "id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "attendance_student" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: attendance_facedetectionevent
CREATE TABLE "attendance_facedetectionevent" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "etape" varchar(10) NOT NULL, "confiance" real NOT NULL, "source" varchar(20) NOT NULL, "raison" varchar(200) NOT NULL, "detected_at" datetime NOT NULL, "camera_id" bigint NULL REFERENCES "attendance_camera" (
    "id") DEFERRABLE INITIALLY DEFERRED, "course_session_id" bigint NULL REFERENCES "attendance_coursesession" (
    "id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NULL REFERENCES "attendance_student" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: attendance_jourferie
CREATE TABLE "attendance_jourferie" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(150) NOT NULL, "date" date NOT NULL UNIQUE, "type_jour" varchar(20) NOT NULL, "created_at" datetime NOT NULL
);

-- Table: attendance_recognitionreviewqueue
CREATE TABLE "attendance_recognitionreviewqueue" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "confidence_proposed" real NOT NULL, "distance_lbph" real NOT NULL, "confidence_second" real NOT NULL, "technical_status" varchar(20) NOT NULL, "daily_date" date NULL, "face_image" varchar(100) NULL, "detected_at" datetime NOT NULL, "source" varchar(20) NOT NULL, "status" varchar(12) NOT NULL, "reviewed_by" varchar(120) NOT NULL, "reviewed_at" datetime NULL, "review_notes" text NOT NULL, "camera_id" bigint NULL REFERENCES "attendance_camera" (
    "id") DEFERRABLE INITIALLY DEFERRED, "course_session_id" bigint NULL REFERENCES "attendance_coursesession" (
    "id") DEFERRABLE INITIALLY DEFERRED, "second_candidate_id" bigint NULL REFERENCES "attendance_student" (
    "id") DEFERRABLE INITIALLY DEFERRED, "student_proposed_id" bigint NULL REFERENCES "attendance_student" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: attendance_salle
CREATE TABLE "attendance_salle" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(80) NOT NULL UNIQUE, "batiment" varchar(80) NOT NULL, "capacite" integer unsigned NOT NULL CHECK (
    "capacite" >= 0), "description" text NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL
);

-- Table: attendance_schedule
CREATE TABLE "attendance_schedule" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "jour_semaine" integer NOT NULL, "heure_debut" time NOT NULL, "heure_fin" time NOT NULL, "tolerance_retard_minutes" integer unsigned NOT NULL CHECK (
    "tolerance_retard_minutes" >= 0), "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "classe_id" bigint NOT NULL REFERENCES "attendance_classe" (
    "id") DEFERRABLE INITIALLY DEFERRED, "course_id" bigint NOT NULL REFERENCES "attendance_course" (
    "id") DEFERRABLE INITIALLY DEFERRED, "minutes_avant_cours" integer unsigned NOT NULL CHECK (
    "minutes_avant_cours" >= 0), "salle_id" bigint NULL REFERENCES "attendance_salle" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: attendance_schooldayconfig
CREATE TABLE "attendance_schooldayconfig" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(100) NOT NULL, "heure_ouverture" time NOT NULL, "heure_debut_cours" time NOT NULL, "heure_limite_arrivee" time NOT NULL, "heure_fin_cours" time NOT NULL, "heure_sortie_precoce" time NOT NULL, "heure_fermeture" time NOT NULL, "lundi" bool NOT NULL, "mardi" bool NOT NULL, "mercredi" bool NOT NULL, "jeudi" bool NOT NULL, "vendredi" bool NOT NULL, "samedi" bool NOT NULL, "updated_at" datetime NOT NULL
);

-- Table: attendance_student
CREATE TABLE "attendance_student" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "full_name" varchar(120) NOT NULL UNIQUE, "student_code" varchar(50) NOT NULL UNIQUE, "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "date_of_birth" date NULL, "email" varchar(254) NOT NULL, "faculty" varchar(20) NOT NULL, "phone" varchar(30) NOT NULL, "classroom" varchar(80) NOT NULL, "classe_id" bigint NULL REFERENCES "attendance_classe" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: attendance_systemconfig
CREATE TABLE "attendance_systemconfig" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "retard_minutes" integer unsigned NOT NULL CHECK (
    "retard_minutes" >= 0), "ouverture_avant_minutes" integer unsigned NOT NULL CHECK (
    "ouverture_avant_minutes" >= 0), "cooldown_detection_minutes" integer unsigned NOT NULL CHECK (
    "cooldown_detection_minutes" >= 0), "seuil_alerte_absences" integer unsigned NOT NULL CHECK (
    "seuil_alerte_absences" >= 0), "filtrer_par_classe" bool NOT NULL, "archiver_evenements_bruts" bool NOT NULL, "updated_at" datetime NOT NULL, "seuil_confiance_haute" real NOT NULL, "seuil_distance_lbph" real NOT NULL
);

-- Table: attendance_trainingphoto
CREATE TABLE "attendance_trainingphoto" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "image" varchar(100) NOT NULL, "created_at" datetime NOT NULL, "student_id" bigint NOT NULL REFERENCES "attendance_student" (
    "id") DEFERRABLE INITIALLY DEFERRED, "face_detected" bool NOT NULL, "trained_at" datetime NULL
);

-- Table: attendance_unknownfacelog
CREATE TABLE "attendance_unknownfacelog" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "image" varchar(100) NULL, "detected_at" datetime NOT NULL, "source" varchar(20) NOT NULL, "notes" varchar(200) NOT NULL, "camera_id" bigint NULL REFERENCES "attendance_camera" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: auth_group
CREATE TABLE "auth_group" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE
);

-- Table: auth_group_permissions
CREATE TABLE "auth_group_permissions" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" (
    "id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: auth_permission
CREATE TABLE "auth_permission" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" (
    "id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL
);

-- Table: auth_user
CREATE TABLE "auth_user" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "first_name" varchar(150) NOT NULL
);

-- Table: auth_user_groups
CREATE TABLE "auth_user_groups" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" (
    "id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: auth_user_user_permissions
CREATE TABLE "auth_user_user_permissions" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" (
    "id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" (
    "id") DEFERRABLE INITIALLY DEFERRED
);

-- Table: django_admin_log
CREATE TABLE "django_admin_log" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK (
    "action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" (
    "id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" (
    "id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL
);

-- Table: django_content_type
CREATE TABLE "django_content_type" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL
);

-- Table: django_migrations
CREATE TABLE "django_migrations" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL
);

-- Table: django_session
CREATE TABLE "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL
);

-- ── Index ──

CREATE INDEX "attendance__classe__7dcfd0_idx" ON "attendance_student" ("classe_id");

CREATE INDEX "attendance__course__890295_idx" ON "attendance_attendancerecord" ("course_session_id");

CREATE INDEX "attendance__course__97c44a_idx" ON "attendance_coursesession" ("course_id", "date");

CREATE INDEX "attendance__date_370344_idx" ON "attendance_dailyattendance" ("date");

CREATE INDEX "attendance__date_5afb96_idx" ON "attendance_coursesession" ("date");

CREATE INDEX "attendance__detecte_0c2e68_idx" ON "attendance_facedetectionevent" ("detected_at");

CREATE INDEX "attendance__detecte_8a9992_idx" ON "attendance_recognitionreviewqueue" ("detected_at");

CREATE INDEX "attendance__etape_0c7070_idx" ON "attendance_facedetectionevent" ("etape");

CREATE INDEX "attendance__is_acti_2f65d1_idx" ON "attendance_student" ("is_active");

CREATE INDEX "attendance__recogni_daff1a_idx" ON "attendance_attendancerecord" ("recognized_at");

CREATE INDEX "attendance__status_0f9648_idx" ON "attendance_coursesession" ("status");

CREATE INDEX "attendance__status_741eb8_idx" ON "attendance_attendancerecord" ("status");

CREATE INDEX "attendance__status_ac56c5_idx" ON "attendance_dailyattendance" ("status");

CREATE INDEX "attendance__status_b48807_idx" ON "attendance_recognitionreviewqueue" ("status");

CREATE INDEX "attendance__student_0b1a6a_idx" ON "attendance_facedetectionevent" ("student_id", "detected_at");

CREATE INDEX "attendance__student_52589a_idx" ON "attendance_student" ("student_code");

CREATE INDEX "attendance__student_bf8a5d_idx" ON "attendance_attendancerecord" ("student_id");

CREATE INDEX "attendance__student_ed8b4b_idx" ON "attendance_dailyattendance" ("student_id", "date");

CREATE INDEX "attendance_attendanceauditlog_attendance_record_id_9eb60a2c" ON "attendance_attendanceauditlog" ("attendance_record_id");

CREATE INDEX "attendance_attendancerecord_camera_id_27afd67e" ON "attendance_attendancerecord" ("camera_id");

CREATE INDEX "attendance_attendancerecord_course_session_id_a50fd8b5" ON "attendance_attendancerecord" ("course_session_id");

CREATE INDEX "attendance_attendancerecord_student_id_d242c468" ON "attendance_attendancerecord" ("student_id");

CREATE INDEX "attendance_camera_salle_id_642ec53b" ON "attendance_camera" ("salle_id");

CREATE INDEX "attendance_coursesession_course_id_a7f6fffc" ON "attendance_coursesession" ("course_id");

CREATE INDEX "attendance_coursesession_schedule_id_6fffad77" ON "attendance_coursesession" ("schedule_id");

CREATE INDEX "attendance_dailyattendance_camera_entree_id_ce0d2f04" ON "attendance_dailyattendance" ("camera_entree_id");

CREATE INDEX "attendance_dailyattendance_camera_sortie_id_d85f7c71" ON "attendance_dailyattendance" ("camera_sortie_id");

CREATE INDEX "attendance_dailyattendance_student_id_abf3bed0" ON "attendance_dailyattendance" ("student_id");

CREATE UNIQUE INDEX "attendance_dailyattendance_student_id_date_2ddad55d_uniq" ON "attendance_dailyattendance" ("student_id", "date");

CREATE INDEX "attendance_enrollment_course_id_71c70056" ON "attendance_enrollment" ("course_id");

CREATE INDEX "attendance_enrollment_student_id_114f1e7b" ON "attendance_enrollment" ("student_id");

CREATE UNIQUE INDEX "attendance_enrollment_student_id_course_id_ba00c9e5_uniq" ON "attendance_enrollment" ("student_id", "course_id");

CREATE INDEX "attendance_facedetectionevent_camera_id_6d1561b1" ON "attendance_facedetectionevent" ("camera_id");

CREATE INDEX "attendance_facedetectionevent_course_session_id_2431c348" ON "attendance_facedetectionevent" ("course_session_id");

CREATE INDEX "attendance_facedetectionevent_student_id_5df27918" ON "attendance_facedetectionevent" ("student_id");

CREATE INDEX "attendance_recognitionreviewqueue_camera_id_3f163328" ON "attendance_recognitionreviewqueue" ("camera_id");

CREATE INDEX "attendance_recognitionreviewqueue_course_session_id_1d32247a" ON "attendance_recognitionreviewqueue" ("course_session_id");

CREATE INDEX "attendance_recognitionreviewqueue_second_candidate_id_54d04344" ON "attendance_recognitionreviewqueue" ("second_candidate_id");

CREATE INDEX "attendance_recognitionreviewqueue_student_proposed_id_2ef6080c" ON "attendance_recognitionreviewqueue" ("student_proposed_id");

CREATE INDEX "attendance_schedule_classe_id_48c209e7" ON "attendance_schedule" ("classe_id");

CREATE INDEX "attendance_schedule_course_id_64a47f4b" ON "attendance_schedule" ("course_id");

CREATE INDEX "attendance_schedule_salle_id_bcfea0c2" ON "attendance_schedule" ("salle_id");

CREATE INDEX "attendance_student_classe_id_7b5b4abf" ON "attendance_student" ("classe_id");

CREATE INDEX "attendance_trainingphoto_student_id_99e6821e" ON "attendance_trainingphoto" ("student_id");

CREATE INDEX "attendance_unknownfacelog_camera_id_f4db0cea" ON "attendance_unknownfacelog" ("camera_id");

CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");

CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");

CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");

CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");

CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");

CREATE INDEX "auth_user_groups_group_id_97559544" ON "auth_user_groups" ("group_id");

CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" ("user_id");

CREATE UNIQUE INDEX "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" ("user_id", "group_id");

CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" ("permission_id");

CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" ("user_id");

CREATE UNIQUE INDEX "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" ("user_id", "permission_id");

CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");

CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");

CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");

CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
