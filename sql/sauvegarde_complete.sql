-- ============================================================
-- UniPresence — Sauvegarde COMPLETE (schema + donnees)
-- Restauration : python restore_db.py  (voir README_LOCAL.md)
-- ============================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=OFF;

BEGIN TRANSACTION;

-- ── attendance_attendanceauditlog ──
DROP TABLE IF EXISTS "attendance_attendanceauditlog";
CREATE TABLE "attendance_attendanceauditlog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "modifie_par" varchar(120) NOT NULL, "ancienne_valeur" varchar(20) NOT NULL, "nouvelle_valeur" varchar(20) NOT NULL, "raison" text NOT NULL, "date_modification" datetime NOT NULL, "attendance_record_id" bigint NOT NULL REFERENCES "attendance_attendancerecord" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── attendance_attendancerecord ──
DROP TABLE IF EXISTS "attendance_attendancerecord";
CREATE TABLE "attendance_attendancerecord" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "student_name_snapshot" varchar(120) NOT NULL, "classroom_snapshot" varchar(80) NOT NULL, "recognized_at" datetime NOT NULL, "confidence_score" real NOT NULL, "status" varchar(12) NOT NULL, "source" varchar(20) NOT NULL, "student_id" bigint NULL REFERENCES "attendance_student" ("id") DEFERRABLE INITIALLY DEFERRED, "course_session_id" bigint NULL REFERENCES "attendance_coursesession" ("id") DEFERRABLE INITIALLY DEFERRED, "camera_id" bigint NULL REFERENCES "attendance_camera" ("id") DEFERRABLE INITIALLY DEFERRED, "excuse_notes" text NOT NULL, "excuse_reason" varchar(20) NOT NULL, "modified_by" varchar(120) NOT NULL);

INSERT INTO "attendance_attendancerecord" ("id", "student_name_snapshot", "classroom_snapshot", "recognized_at", "confidence_score", "status", "source", "student_id", "course_session_id", "camera_id", "excuse_notes", "excuse_reason", "modified_by") VALUES (1, 'believer', 'l2', '2026-05-05 18:40:50.404961', 41.4, 'present', 'live', 3, NULL, 1, '', '', '');
INSERT INTO "attendance_attendancerecord" ("id", "student_name_snapshot", "classroom_snapshot", "recognized_at", "confidence_score", "status", "source", "student_id", "course_session_id", "camera_id", "excuse_notes", "excuse_reason", "modified_by") VALUES (2, 'believer', 'l2', '2026-05-06 10:35:36.197876', 46.3, 'present', 'live', 3, NULL, 1, '', '', '');
INSERT INTO "attendance_attendancerecord" ("id", "student_name_snapshot", "classroom_snapshot", "recognized_at", "confidence_score", "status", "source", "student_id", "course_session_id", "camera_id", "excuse_notes", "excuse_reason", "modified_by") VALUES (3, 'believer', 'l2', '2026-05-16 14:13:08.805371', 68.6, 'present', 'live', 3, NULL, 1, '', '', '');

-- ── attendance_camera ──
DROP TABLE IF EXISTS "attendance_camera";
CREATE TABLE "attendance_camera" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "location" varchar(150) NOT NULL, "camera_type" varchar(10) NOT NULL, "source" varchar(300) NOT NULL, "resolution_w" integer unsigned NOT NULL CHECK ("resolution_w" >= 0), "resolution_h" integer unsigned NOT NULL CHECK ("resolution_h" >= 0), "is_active" bool NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "salle_id" bigint NULL REFERENCES "attendance_salle" ("id") DEFERRABLE INITIALLY DEFERRED, "zone_type" varchar(12) NOT NULL, "detection_mode" varchar(16) NOT NULL, "error_count" integer unsigned NOT NULL CHECK ("error_count" >= 0), "fps_estimate" real NOT NULL, "frames_processed" integer unsigned NOT NULL CHECK ("frames_processed" >= 0), "is_online" bool NOT NULL, "last_error" varchar(500) NOT NULL, "last_seen" datetime NULL);

INSERT INTO "attendance_camera" ("id", "name", "location", "camera_type", "source", "resolution_w", "resolution_h", "is_active", "notes", "created_at", "salle_id", "zone_type", "detection_mode", "error_count", "fps_estimate", "frames_processed", "is_online", "last_error", "last_seen") VALUES (1, 'entrer', 'a', 'webcam', '', 640, 480, 1, '', '2026-05-05 18:40:30.394766', NULL, 'monitoring', 'recognition', 0, 0.0, 0, 0, '', NULL);

-- ── attendance_classe ──
DROP TABLE IF EXISTS "attendance_classe";
CREATE TABLE "attendance_classe" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(100) NOT NULL, "niveau" varchar(50) NOT NULL, "option" varchar(100) NOT NULL, "annee_academique" varchar(20) NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL);

-- ── attendance_classroomschedule ──
DROP TABLE IF EXISTS "attendance_classroomschedule";
CREATE TABLE "attendance_classroomschedule" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "classroom" varchar(80) NOT NULL UNIQUE, "start_time" time NOT NULL, "late_after_minutes" integer unsigned NOT NULL CHECK ("late_after_minutes" >= 0));

INSERT INTO "attendance_classroomschedule" ("id", "classroom", "start_time", "late_after_minutes") VALUES (1, 'L3 Info', '08:00:00', 5);
INSERT INTO "attendance_classroomschedule" ("id", "classroom", "start_time", "late_after_minutes") VALUES (2, 'L2 Info', '08:30:00', 10);
INSERT INTO "attendance_classroomschedule" ("id", "classroom", "start_time", "late_after_minutes") VALUES (3, 'M1 Data', '09:00:00', 10);

-- ── attendance_course ──
DROP TABLE IF EXISTS "attendance_course";
CREATE TABLE "attendance_course" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "code" varchar(30) NOT NULL UNIQUE, "name" varchar(150) NOT NULL, "faculty" varchar(20) NOT NULL, "professor" varchar(120) NOT NULL, "credits" integer unsigned NOT NULL CHECK ("credits" >= 0), "created_at" datetime NOT NULL);

-- ── attendance_coursesession ──
DROP TABLE IF EXISTS "attendance_coursesession";
CREATE TABLE "attendance_coursesession" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" date NOT NULL, "start_time" time NOT NULL, "end_time" time NULL, "room" varchar(80) NOT NULL, "late_after_minutes" integer unsigned NOT NULL CHECK ("late_after_minutes" >= 0), "notes" text NOT NULL, "closed" bool NOT NULL, "created_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "attendance_course" ("id") DEFERRABLE INITIALLY DEFERRED, "status" varchar(12) NOT NULL, "schedule_id" bigint NULL REFERENCES "attendance_schedule" ("id") DEFERRABLE INITIALLY DEFERRED, "minutes_avant_cours" integer unsigned NOT NULL CHECK ("minutes_avant_cours" >= 0), "motif_annulation" varchar(200) NOT NULL);

-- ── attendance_dailyattendance ──
DROP TABLE IF EXISTS "attendance_dailyattendance";
CREATE TABLE "attendance_dailyattendance" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" date NOT NULL, "heure_entree" time NULL, "heure_sortie" time NULL, "status" varchar(20) NOT NULL, "modified_by" varchar(120) NOT NULL, "excuse_reason" varchar(50) NOT NULL, "excuse_notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "camera_entree_id" bigint NULL REFERENCES "attendance_camera" ("id") DEFERRABLE INITIALLY DEFERRED, "camera_sortie_id" bigint NULL REFERENCES "attendance_camera" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "attendance_student" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── attendance_enrollment ──
DROP TABLE IF EXISTS "attendance_enrollment";
CREATE TABLE "attendance_enrollment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "enrolled_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "attendance_course" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "attendance_student" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── attendance_facedetectionevent ──
DROP TABLE IF EXISTS "attendance_facedetectionevent";
CREATE TABLE "attendance_facedetectionevent" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "etape" varchar(10) NOT NULL, "confiance" real NOT NULL, "source" varchar(20) NOT NULL, "raison" varchar(200) NOT NULL, "detected_at" datetime NOT NULL, "camera_id" bigint NULL REFERENCES "attendance_camera" ("id") DEFERRABLE INITIALLY DEFERRED, "course_session_id" bigint NULL REFERENCES "attendance_coursesession" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NULL REFERENCES "attendance_student" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── attendance_jourferie ──
DROP TABLE IF EXISTS "attendance_jourferie";
CREATE TABLE "attendance_jourferie" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(150) NOT NULL, "date" date NOT NULL UNIQUE, "type_jour" varchar(20) NOT NULL, "created_at" datetime NOT NULL);

-- ── attendance_recognitionreviewqueue ──
DROP TABLE IF EXISTS "attendance_recognitionreviewqueue";
CREATE TABLE "attendance_recognitionreviewqueue" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "confidence_proposed" real NOT NULL, "distance_lbph" real NOT NULL, "confidence_second" real NOT NULL, "technical_status" varchar(20) NOT NULL, "daily_date" date NULL, "face_image" varchar(100) NULL, "detected_at" datetime NOT NULL, "source" varchar(20) NOT NULL, "status" varchar(12) NOT NULL, "reviewed_by" varchar(120) NOT NULL, "reviewed_at" datetime NULL, "review_notes" text NOT NULL, "camera_id" bigint NULL REFERENCES "attendance_camera" ("id") DEFERRABLE INITIALLY DEFERRED, "course_session_id" bigint NULL REFERENCES "attendance_coursesession" ("id") DEFERRABLE INITIALLY DEFERRED, "second_candidate_id" bigint NULL REFERENCES "attendance_student" ("id") DEFERRABLE INITIALLY DEFERRED, "student_proposed_id" bigint NULL REFERENCES "attendance_student" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── attendance_salle ──
DROP TABLE IF EXISTS "attendance_salle";
CREATE TABLE "attendance_salle" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(80) NOT NULL UNIQUE, "batiment" varchar(80) NOT NULL, "capacite" integer unsigned NOT NULL CHECK ("capacite" >= 0), "description" text NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL);

-- ── attendance_schedule ──
DROP TABLE IF EXISTS "attendance_schedule";
CREATE TABLE "attendance_schedule" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "jour_semaine" integer NOT NULL, "heure_debut" time NOT NULL, "heure_fin" time NOT NULL, "tolerance_retard_minutes" integer unsigned NOT NULL CHECK ("tolerance_retard_minutes" >= 0), "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "classe_id" bigint NOT NULL REFERENCES "attendance_classe" ("id") DEFERRABLE INITIALLY DEFERRED, "course_id" bigint NOT NULL REFERENCES "attendance_course" ("id") DEFERRABLE INITIALLY DEFERRED, "minutes_avant_cours" integer unsigned NOT NULL CHECK ("minutes_avant_cours" >= 0), "salle_id" bigint NULL REFERENCES "attendance_salle" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── attendance_schooldayconfig ──
DROP TABLE IF EXISTS "attendance_schooldayconfig";
CREATE TABLE "attendance_schooldayconfig" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(100) NOT NULL, "heure_ouverture" time NOT NULL, "heure_debut_cours" time NOT NULL, "heure_limite_arrivee" time NOT NULL, "heure_fin_cours" time NOT NULL, "heure_sortie_precoce" time NOT NULL, "heure_fermeture" time NOT NULL, "lundi" bool NOT NULL, "mardi" bool NOT NULL, "mercredi" bool NOT NULL, "jeudi" bool NOT NULL, "vendredi" bool NOT NULL, "samedi" bool NOT NULL, "updated_at" datetime NOT NULL);

-- ── attendance_student ──
DROP TABLE IF EXISTS "attendance_student";
CREATE TABLE "attendance_student" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "full_name" varchar(120) NOT NULL UNIQUE, "student_code" varchar(50) NOT NULL UNIQUE, "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "date_of_birth" date NULL, "email" varchar(254) NOT NULL, "faculty" varchar(20) NOT NULL, "phone" varchar(30) NOT NULL, "classroom" varchar(80) NOT NULL, "classe_id" bigint NULL REFERENCES "attendance_classe" ("id") DEFERRABLE INITIALLY DEFERRED);

INSERT INTO "attendance_student" ("id", "full_name", "student_code", "is_active", "created_at", "date_of_birth", "email", "faculty", "phone", "classroom", "classe_id") VALUES (3, 'believer', 'STI-001', 1, '2026-05-05 17:57:45.519426', '2004-06-22', 'believingb7@gmail.com', 'ing', '+243999371251', 'l2', NULL);
INSERT INTO "attendance_student" ("id", "full_name", "student_code", "is_active", "created_at", "date_of_birth", "email", "faculty", "phone", "classroom", "classe_id") VALUES (4, 'divine', 'STI-002', 1, '2026-05-06 07:25:53.706330', NULL, 'believingb7@gmail.com', 'eco', '+243999371251', 'l3', NULL);

-- ── attendance_systemconfig ──
DROP TABLE IF EXISTS "attendance_systemconfig";
CREATE TABLE "attendance_systemconfig" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "retard_minutes" integer unsigned NOT NULL CHECK ("retard_minutes" >= 0), "ouverture_avant_minutes" integer unsigned NOT NULL CHECK ("ouverture_avant_minutes" >= 0), "cooldown_detection_minutes" integer unsigned NOT NULL CHECK ("cooldown_detection_minutes" >= 0), "seuil_alerte_absences" integer unsigned NOT NULL CHECK ("seuil_alerte_absences" >= 0), "filtrer_par_classe" bool NOT NULL, "archiver_evenements_bruts" bool NOT NULL, "updated_at" datetime NOT NULL, "seuil_confiance_haute" real NOT NULL, "seuil_distance_lbph" real NOT NULL);

-- ── attendance_trainingphoto ──
DROP TABLE IF EXISTS "attendance_trainingphoto";
CREATE TABLE "attendance_trainingphoto" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "image" varchar(100) NOT NULL, "created_at" datetime NOT NULL, "student_id" bigint NOT NULL REFERENCES "attendance_student" ("id") DEFERRABLE INITIALLY DEFERRED, "face_detected" bool NOT NULL, "trained_at" datetime NULL);

INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (4, 'students/li.jpg', '2026-05-05 17:57:45.558746', 3, 0, NULL);
INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (5, 'students/beau.jpg', '2026-05-05 17:57:45.568762', 3, 0, NULL);
INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (7, 'students/IMG-20250325-WA0009.jpg', '2026-05-05 19:20:57.023035', 3, 1, '2026-05-06 10:30:30.689278');
INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (8, 'students/IMG-20250406-WA0059.jpg', '2026-05-05 19:20:57.056924', 3, 1, '2026-05-06 10:30:30.689278');
INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (9, 'students/IMG-20250406-WA0060.jpg', '2026-05-05 19:20:57.065932', 3, 1, '2026-05-06 10:30:30.689278');
INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (10, 'students/IMG-20250406-WA0061.jpg', '2026-05-05 19:20:57.075490', 3, 1, '2026-05-06 10:30:30.689278');
INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (12, 'students/IMG-20250406-WA0063.jpg', '2026-05-05 19:20:57.095311', 3, 0, NULL);
INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (15, 'students/IMG-20250419-WA0010.jpg', '2026-05-05 19:20:57.121277', 3, 1, '2026-05-06 10:30:30.689278');
INSERT INTO "attendance_trainingphoto" ("id", "image", "created_at", "student_id", "face_detected", "trained_at") VALUES (16, 'students/IMG-20250419-WA0025.jpg', '2026-05-05 19:20:57.131189', 3, 1, '2026-05-06 10:30:30.689278');

-- ── attendance_unknownfacelog ──
DROP TABLE IF EXISTS "attendance_unknownfacelog";
CREATE TABLE "attendance_unknownfacelog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "image" varchar(100) NULL, "detected_at" datetime NOT NULL, "source" varchar(20) NOT NULL, "notes" varchar(200) NOT NULL, "camera_id" bigint NULL REFERENCES "attendance_camera" ("id") DEFERRABLE INITIALLY DEFERRED);

INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (2, 'unknown_faces/unknown_live_20260505_184338_310972.jpg', '2026-05-05 18:43:38.311972', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (3, 'unknown_faces/unknown_live_20260505_184339_809500.jpg', '2026-05-05 18:43:39.810204', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (4, 'unknown_faces/unknown_live_20260505_184354_829248.jpg', '2026-05-05 18:43:54.829934', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (5, 'unknown_faces/unknown_live_20260505_184405_020019.jpg', '2026-05-05 18:44:05.020572', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (6, 'unknown_faces/unknown_live_20260505_184406_806626.jpg', '2026-05-05 18:44:06.807189', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (7, 'unknown_faces/unknown_live_20260505_184406_816657.jpg', '2026-05-05 18:44:06.817188', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (8, 'unknown_faces/unknown_live_20260505_184406_829698.jpg', '2026-05-05 18:44:06.830214', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (9, 'unknown_faces/unknown_live_20260505_184411_330092.jpg', '2026-05-05 18:44:11.331022', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (10, 'unknown_faces/unknown_live_20260505_184412_851747.jpg', '2026-05-05 18:44:12.852273', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (11, 'unknown_faces/unknown_live_20260505_184412_862707.jpg', '2026-05-05 18:44:12.863223', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (12, 'unknown_faces/unknown_live_20260505_184415_846916.jpg', '2026-05-05 18:44:15.847509', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (13, 'unknown_faces/unknown_live_20260505_184418_857728.jpg', '2026-05-05 18:44:18.858260', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (14, 'unknown_faces/unknown_live_20260505_184420_372449.jpg', '2026-05-05 18:44:20.373117', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (15, 'unknown_faces/unknown_live_20260505_184426_325277.jpg', '2026-05-05 18:44:26.325871', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (16, 'unknown_faces/unknown_live_20260505_184439_835913.jpg', '2026-05-05 18:44:39.836548', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (17, 'unknown_faces/unknown_live_20260505_184445_809645.jpg', '2026-05-05 18:44:45.810147', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (18, 'unknown_faces/unknown_live_20260505_184453_307364.jpg', '2026-05-05 18:44:53.307898', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (19, 'unknown_faces/unknown_live_20260505_184456_301037.jpg', '2026-05-05 18:44:56.301708', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (20, 'unknown_faces/unknown_live_20260505_184513_310434.jpg', '2026-05-05 18:45:13.311050', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (21, 'unknown_faces/unknown_live_20260505_184514_809413.jpg', '2026-05-05 18:45:14.811439', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (22, 'unknown_faces/unknown_live_20260505_184522_553526.jpg', '2026-05-05 18:45:22.554366', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (23, 'unknown_faces/unknown_live_20260505_184527_409801.jpg', '2026-05-05 18:45:27.410401', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (24, 'unknown_faces/unknown_live_20260505_184533_984444.jpg', '2026-05-05 18:45:33.985345', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (25, 'unknown_faces/unknown_live_20260505_184535_759071.jpg', '2026-05-05 18:45:35.759885', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (26, 'unknown_faces/unknown_live_20260505_184549_631501.jpg', '2026-05-05 18:45:49.632293', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (27, 'unknown_faces/unknown_live_20260505_184602_327806.jpg', '2026-05-05 18:46:02.328451', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (28, 'unknown_faces/unknown_live_20260505_184604_925090.jpg', '2026-05-05 18:46:04.925763', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (29, 'unknown_faces/unknown_live_20260505_184607_705203.jpg', '2026-05-05 18:46:07.705774', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (30, 'unknown_faces/unknown_live_20260505_184608_128924.jpg', '2026-05-05 18:46:08.129395', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (31, 'unknown_faces/unknown_live_20260505_184608_836382.jpg', '2026-05-05 18:46:08.837078', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (32, 'unknown_faces/unknown_live_20260505_184610_321257.jpg', '2026-05-05 18:46:10.321933', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (33, 'unknown_faces/unknown_live_20260505_184611_973814.jpg', '2026-05-05 18:46:11.974523', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (34, 'unknown_faces/unknown_live_20260505_184612_555543.jpg', '2026-05-05 18:46:12.556133', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (35, 'unknown_faces/unknown_live_20260505_184616_349494.jpg', '2026-05-05 18:46:16.350080', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (36, 'unknown_faces/unknown_live_20260505_184618_240925.jpg', '2026-05-05 18:46:18.241552', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (37, 'unknown_faces/unknown_live_20260505_184622_499849.jpg', '2026-05-05 18:46:22.501275', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (38, 'unknown_faces/unknown_live_20260505_184624_263598.jpg', '2026-05-05 18:46:24.264242', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (39, 'unknown_faces/unknown_live_20260505_184626_837993.jpg', '2026-05-05 18:46:26.838585', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (43, 'unknown_faces/unknown_live_20260505_191600_305049.jpg', '2026-05-05 19:16:00.315755', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (44, 'unknown_faces/unknown_live_20260505_191600_371260.jpg', '2026-05-05 19:16:00.372138', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (45, 'unknown_faces/unknown_live_20260505_191600_395769.jpg', '2026-05-05 19:16:00.396903', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (46, 'unknown_faces/unknown_live_20260505_191603_645673.jpg', '2026-05-05 19:16:03.646447', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (47, 'unknown_faces/unknown_live_20260505_191605_623391.jpg', '2026-05-05 19:16:05.624616', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (48, 'unknown_faces/unknown_live_20260505_191613_339908.jpg', '2026-05-05 19:16:13.340663', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (49, 'unknown_faces/unknown_live_20260505_191615_331676.jpg', '2026-05-05 19:16:15.332290', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (50, 'unknown_faces/unknown_live_20260505_191621_340607.jpg', '2026-05-05 19:16:21.341177', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (51, 'unknown_faces/unknown_live_20260505_191645_354076.jpg', '2026-05-05 19:16:45.354914', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (52, 'unknown_faces/unknown_live_20260505_191649_353441.jpg', '2026-05-05 19:16:49.354052', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (53, 'unknown_faces/unknown_live_20260505_191651_940590.jpg', '2026-05-05 19:16:51.941206', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (54, 'unknown_faces/unknown_live_20260505_191655_401573.jpg', '2026-05-05 19:16:55.402182', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (55, 'unknown_faces/unknown_live_20260505_191713_103270.jpg', '2026-05-05 19:17:13.103896', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (56, 'unknown_faces/unknown_live_20260505_191714_574766.jpg', '2026-05-05 19:17:14.575333', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (57, 'unknown_faces/unknown_live_20260505_191714_585778.jpg', '2026-05-05 19:17:14.586278', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (58, 'unknown_faces/unknown_live_20260505_191718_267916.jpg', '2026-05-05 19:17:18.268422', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (59, 'unknown_faces/unknown_live_20260505_191719_111982.jpg', '2026-05-05 19:17:19.112451', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (60, 'unknown_faces/unknown_live_20260505_191720_585109.jpg', '2026-05-05 19:17:20.585734', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (61, 'unknown_faces/unknown_live_20260505_191722_059846.jpg', '2026-05-05 19:17:22.060298', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (62, 'unknown_faces/unknown_live_20260505_191722_070878.jpg', '2026-05-05 19:17:22.071450', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (63, 'unknown_faces/unknown_live_20260505_191725_090834.jpg', '2026-05-05 19:17:25.091432', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (64, 'unknown_faces/unknown_live_20260505_191735_563127.jpg', '2026-05-05 19:17:35.563759', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (65, 'unknown_faces/unknown_live_20260505_191743_107509.jpg', '2026-05-05 19:17:43.108199', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (66, 'unknown_faces/unknown_live_20260505_192313_127906.jpg', '2026-05-05 19:23:13.128697', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (67, 'unknown_faces/unknown_live_20260505_192316_075240.jpg', '2026-05-05 19:23:16.075821', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (68, 'unknown_faces/unknown_live_20260505_192320_586948.jpg', '2026-05-05 19:23:20.587477', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (69, 'unknown_faces/unknown_live_20260505_192323_557563.jpg', '2026-05-05 19:23:23.558150', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (70, 'unknown_faces/unknown_live_20260505_192325_069275.jpg', '2026-05-05 19:23:25.069895', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (71, 'unknown_faces/unknown_live_20260505_192326_553693.jpg', '2026-05-05 19:23:26.554233', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (72, 'unknown_faces/unknown_live_20260505_192329_595982.jpg', '2026-05-05 19:23:29.596487', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (73, 'unknown_faces/unknown_live_20260505_192334_128079.jpg', '2026-05-05 19:23:34.128584', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (74, 'unknown_faces/unknown_live_20260505_192340_054473.jpg', '2026-05-05 19:23:40.055114', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (75, 'unknown_faces/unknown_live_20260505_215327_141355.jpg', '2026-05-05 21:53:27.143646', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (76, 'unknown_faces/unknown_live_20260505_215327_187862.jpg', '2026-05-05 21:53:27.189589', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (77, 'unknown_faces/unknown_live_20260505_215329_163550.jpg', '2026-05-05 21:53:29.164098', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (78, 'unknown_faces/unknown_live_20260505_215337_145528.jpg', '2026-05-05 21:53:37.146212', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (79, 'unknown_faces/unknown_live_20260505_215349_144179.jpg', '2026-05-05 21:53:49.146338', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (80, 'unknown_faces/unknown_live_20260505_215353_118646.jpg', '2026-05-05 21:53:53.119290', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (81, 'unknown_faces/unknown_live_20260506_102933_599470.jpg', '2026-05-06 10:29:33.600619', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (82, 'unknown_faces/unknown_live_20260506_103311_330178.jpg', '2026-05-06 10:33:11.331088', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (83, 'unknown_faces/unknown_live_20260506_103311_371688.jpg', '2026-05-06 10:33:11.372628', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (84, 'unknown_faces/unknown_live_20260506_103314_327788.jpg', '2026-05-06 10:33:14.328596', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (85, 'unknown_faces/unknown_live_20260506_103504_975293.jpg', '2026-05-06 10:35:04.976551', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (86, 'unknown_faces/unknown_live_20260506_103506_174476.jpg', '2026-05-06 10:35:06.175536', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (87, 'unknown_faces/unknown_live_20260506_103518_218747.jpg', '2026-05-06 10:35:18.220073', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (88, 'unknown_faces/unknown_live_20260506_103545_183922.jpg', '2026-05-06 10:35:45.184820', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (89, 'unknown_faces/unknown_live_20260506_103546_686439.jpg', '2026-05-06 10:35:46.687471', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (90, 'unknown_faces/unknown_live_20260506_103548_277437.jpg', '2026-05-06 10:35:48.278332', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (91, 'unknown_faces/unknown_live_20260506_103549_720445.jpg', '2026-05-06 10:35:49.721240', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (93, 'unknown_faces/unknown_live_20260506_103624_478767.jpg', '2026-05-06 10:36:24.479721', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (95, 'unknown_faces/unknown_live_20260506_103710_056940.jpg', '2026-05-06 10:37:10.057880', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (97, 'unknown_faces/unknown_live_20260506_103713_066447.jpg', '2026-05-06 10:37:13.067153', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (98, 'unknown_faces/unknown_live_20260506_104035_548745.jpg', '2026-05-06 10:40:35.549849', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (99, 'unknown_faces/unknown_live_20260506_104035_607669.jpg', '2026-05-06 10:40:35.608344', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (100, 'unknown_faces/unknown_live_20260506_104054_990360.jpg', '2026-05-06 10:40:54.991081', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (101, 'unknown_faces/unknown_live_20260506_104055_055259.jpg', '2026-05-06 10:40:55.055897', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (102, 'unknown_faces/unknown_live_20260506_104114_560712.jpg', '2026-05-06 10:41:14.561624', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (103, 'unknown_faces/unknown_live_20260506_104116_006299.jpg', '2026-05-06 10:41:16.007157', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (104, 'unknown_faces/unknown_live_20260506_104117_593213.jpg', '2026-05-06 10:41:17.593894', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (105, 'unknown_faces/unknown_live_20260506_104117_617562.jpg', '2026-05-06 10:41:17.619445', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (106, 'unknown_faces/unknown_live_20260506_104117_638895.jpg', '2026-05-06 10:41:17.640533', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (107, 'unknown_faces/unknown_live_20260506_104120_580402.jpg', '2026-05-06 10:41:20.581175', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (108, 'unknown_faces/unknown_live_20260506_104120_600907.jpg', '2026-05-06 10:41:20.601362', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (109, 'unknown_faces/unknown_live_20260506_104120_620188.jpg', '2026-05-06 10:41:20.620733', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (110, 'unknown_faces/unknown_live_20260506_104122_075650.jpg', '2026-05-06 10:41:22.076362', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (111, 'unknown_faces/unknown_live_20260506_104122_096527.jpg', '2026-05-06 10:41:22.097052', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (112, 'unknown_faces/unknown_live_20260506_104122_116791.jpg', '2026-05-06 10:41:22.117380', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (113, 'unknown_faces/unknown_live_20260506_104126_476843.jpg', '2026-05-06 10:41:26.477459', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (114, 'unknown_faces/unknown_live_20260506_104126_497906.jpg', '2026-05-06 10:41:26.498533', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (115, 'unknown_faces/unknown_live_20260506_104128_436319.jpg', '2026-05-06 10:41:28.437077', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (116, 'unknown_faces/unknown_live_20260506_104142_960050.jpg', '2026-05-06 10:41:42.960908', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (117, 'unknown_faces/unknown_live_20260506_104144_463157.jpg', '2026-05-06 10:41:44.463735', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (118, 'unknown_faces/unknown_live_20260506_104208_481226.jpg', '2026-05-06 10:42:08.482051', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (119, 'unknown_faces/unknown_live_20260506_104230_970271.jpg', '2026-05-06 10:42:30.971651', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (120, 'unknown_faces/unknown_live_20260506_104238_458456.jpg', '2026-05-06 10:42:38.459050', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (121, 'unknown_faces/unknown_live_20260506_104239_969529.jpg', '2026-05-06 10:42:39.970235', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (122, 'unknown_faces/unknown_live_20260506_104239_989689.jpg', '2026-05-06 10:42:39.990136', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (123, 'unknown_faces/unknown_live_20260506_104245_957383.jpg', '2026-05-06 10:42:45.959288', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (124, 'unknown_faces/unknown_live_20260506_104247_448063.jpg', '2026-05-06 10:42:47.448796', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (125, 'unknown_faces/unknown_live_20260506_104250_470474.jpg', '2026-05-06 10:42:50.471248', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (126, 'unknown_faces/unknown_live_20260506_104254_991303.jpg', '2026-05-06 10:42:54.992056', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (127, 'unknown_faces/unknown_live_20260506_104355_728748.jpg', '2026-05-06 10:43:55.729691', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (128, 'unknown_faces/unknown_live_20260506_104357_246507.jpg', '2026-05-06 10:43:57.247379', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (129, 'unknown_faces/unknown_live_20260506_104429_007142.jpg', '2026-05-06 10:44:29.008221', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (130, 'unknown_faces/unknown_live_20260506_104852_978498.jpg', '2026-05-06 10:48:52.979387', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (131, 'unknown_faces/unknown_live_20260506_104857_277591.jpg', '2026-05-06 10:48:57.278582', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (132, 'unknown_faces/unknown_live_20260506_104857_337046.jpg', '2026-05-06 10:48:57.337598', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (133, 'unknown_faces/unknown_live_20260506_104858_503232.jpg', '2026-05-06 10:48:58.503898', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (134, 'unknown_faces/unknown_live_20260506_104902_123279.jpg', '2026-05-06 10:49:02.124128', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (135, 'unknown_faces/unknown_live_20260506_104905_205093.jpg', '2026-05-06 10:49:05.205913', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (136, 'unknown_faces/unknown_live_20260506_104906_093233.jpg', '2026-05-06 10:49:06.095413', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (137, 'unknown_faces/unknown_live_20260506_104907_613299.jpg', '2026-05-06 10:49:07.614285', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (138, 'unknown_faces/unknown_live_20260506_104908_805851.jpg', '2026-05-06 10:49:08.808281', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (139, 'unknown_faces/unknown_live_20260506_104908_828543.jpg', '2026-05-06 10:49:08.829154', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (140, 'unknown_faces/unknown_live_20260506_104910_382161.jpg', '2026-05-06 10:49:10.382805', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (141, 'unknown_faces/unknown_live_20260506_104910_419466.jpg', '2026-05-06 10:49:10.420505', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (142, 'unknown_faces/unknown_live_20260506_104911_866844.jpg', '2026-05-06 10:49:11.867471', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (143, 'unknown_faces/unknown_live_20260506_104911_887296.jpg', '2026-05-06 10:49:11.887982', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (144, 'unknown_faces/unknown_live_20260506_104913_348232.jpg', '2026-05-06 10:49:13.348962', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (145, 'unknown_faces/unknown_live_20260506_104913_372055.jpg', '2026-05-06 10:49:13.372662', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (146, 'unknown_faces/unknown_live_20260506_104914_836784.jpg', '2026-05-06 10:49:14.837563', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (147, 'unknown_faces/unknown_live_20260506_104914_859360.jpg', '2026-05-06 10:49:14.859978', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (148, 'unknown_faces/unknown_live_20260506_104916_660284.jpg', '2026-05-06 10:49:16.661082', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (149, 'unknown_faces/unknown_live_20260506_104916_726931.jpg', '2026-05-06 10:49:16.727614', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (150, 'unknown_faces/unknown_live_20260506_104918_084051.jpg', '2026-05-06 10:49:18.084727', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (151, 'unknown_faces/unknown_live_20260506_104918_104270.jpg', '2026-05-06 10:49:18.104709', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (152, 'unknown_faces/unknown_live_20260506_104918_123428.jpg', '2026-05-06 10:49:18.124006', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (153, 'unknown_faces/unknown_live_20260506_104920_017130.jpg', '2026-05-06 10:49:20.017761', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (154, 'unknown_faces/unknown_live_20260506_104920_037839.jpg', '2026-05-06 10:49:20.038407', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (155, 'unknown_faces/unknown_live_20260506_104920_862765.jpg', '2026-05-06 10:49:20.863381', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (156, 'unknown_faces/unknown_live_20260506_104920_882871.jpg', '2026-05-06 10:49:20.883402', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (157, 'unknown_faces/unknown_live_20260506_104922_282254.jpg', '2026-05-06 10:49:22.282741', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (158, 'unknown_faces/unknown_live_20260506_104922_302434.jpg', '2026-05-06 10:49:22.303013', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (159, 'unknown_faces/unknown_live_20260506_104924_451431.jpg', '2026-05-06 10:49:24.452077', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (160, 'unknown_faces/unknown_live_20260506_104924_472903.jpg', '2026-05-06 10:49:24.473538', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (161, 'unknown_faces/unknown_live_20260506_104925_348541.jpg', '2026-05-06 10:49:25.349064', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (162, 'unknown_faces/unknown_live_20260506_104925_373996.jpg', '2026-05-06 10:49:25.374629', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (163, 'unknown_faces/unknown_live_20260506_104926_828784.jpg', '2026-05-06 10:49:26.829521', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (164, 'unknown_faces/unknown_live_20260506_104926_849358.jpg', '2026-05-06 10:49:26.849933', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (165, 'unknown_faces/unknown_live_20260506_104926_867933.jpg', '2026-05-06 10:49:26.868383', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (166, 'unknown_faces/unknown_live_20260506_104928_312252.jpg', '2026-05-06 10:49:28.313015', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (167, 'unknown_faces/unknown_live_20260506_104929_779141.jpg', '2026-05-06 10:49:29.779648', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (168, 'unknown_faces/unknown_live_20260506_104931_326662.jpg', '2026-05-06 10:49:31.327547', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (169, 'unknown_faces/unknown_live_20260506_104931_397428.jpg', '2026-05-06 10:49:31.398032', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (170, 'unknown_faces/unknown_live_20260506_104933_450202.jpg', '2026-05-06 10:49:33.450748', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (171, 'unknown_faces/unknown_live_20260506_104933_470959.jpg', '2026-05-06 10:49:33.471392', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (172, 'unknown_faces/unknown_live_20260506_104934_535216.jpg', '2026-05-06 10:49:34.536269', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (173, 'unknown_faces/unknown_live_20260506_104934_557984.jpg', '2026-05-06 10:49:34.558642', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (174, 'unknown_faces/unknown_live_20260506_104935_816273.jpg', '2026-05-06 10:49:35.816796', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (175, 'unknown_faces/unknown_live_20260506_104937_381090.jpg', '2026-05-06 10:49:37.381793', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (176, 'unknown_faces/unknown_live_20260506_104938_785698.jpg', '2026-05-06 10:49:38.786223', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (177, 'unknown_faces/unknown_live_20260506_104940_350524.jpg', '2026-05-06 10:49:40.351315', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (178, 'unknown_faces/unknown_live_20260506_105740_052850.jpg', '2026-05-06 10:57:40.053871', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (179, 'unknown_faces/unknown_live_20260506_105740_953848.jpg', '2026-05-06 10:57:40.954546', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (180, 'unknown_faces/unknown_live_20260506_105742_471481.jpg', '2026-05-06 10:57:42.472007', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (181, 'unknown_faces/unknown_live_20260506_105744_020260.jpg', '2026-05-06 10:57:44.021326', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (182, 'unknown_faces/unknown_live_20260506_105744_043379.jpg', '2026-05-06 10:57:44.043948', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (183, 'unknown_faces/unknown_live_20260506_105745_452765.jpg', '2026-05-06 10:57:45.453544', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (184, 'unknown_faces/unknown_live_20260506_105746_987476.jpg', '2026-05-06 10:57:46.988469', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (185, 'unknown_faces/unknown_live_20260506_105748_487902.jpg', '2026-05-06 10:57:48.488679', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (186, 'unknown_faces/unknown_live_20260506_105748_509006.jpg', '2026-05-06 10:57:48.509668', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (187, 'unknown_faces/unknown_live_20260506_105749_962759.jpg', '2026-05-06 10:57:49.963595', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (188, 'unknown_faces/unknown_live_20260506_105749_984838.jpg', '2026-05-06 10:57:49.985494', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (189, 'unknown_faces/unknown_live_20260506_105751_489381.jpg', '2026-05-06 10:57:51.490001', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (190, 'unknown_faces/unknown_live_20260506_105758_935971.jpg', '2026-05-06 10:57:58.936999', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (191, 'unknown_faces/unknown_live_20260506_105801_962197.jpg', '2026-05-06 10:58:01.963172', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (192, 'unknown_faces/unknown_live_20260506_105806_455900.jpg', '2026-05-06 10:58:06.456697', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (193, 'unknown_faces/unknown_live_20260506_105807_965208.jpg', '2026-05-06 10:58:07.965946', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (194, 'unknown_faces/unknown_live_20260506_105807_987251.jpg', '2026-05-06 10:58:07.987856', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (195, 'unknown_faces/unknown_live_20260506_105809_489683.jpg', '2026-05-06 10:58:09.490469', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (196, 'unknown_faces/unknown_live_20260506_105809_511435.jpg', '2026-05-06 10:58:09.512219', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (197, 'unknown_faces/unknown_live_20260506_105809_531476.jpg', '2026-05-06 10:58:09.532075', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (198, 'unknown_faces/unknown_live_20260506_105810_946521.jpg', '2026-05-06 10:58:10.947202', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (199, 'unknown_faces/unknown_live_20260506_105810_968475.jpg', '2026-05-06 10:58:10.969046', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (200, 'unknown_faces/unknown_live_20260506_105812_466844.jpg', '2026-05-06 10:58:12.467499', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (201, 'unknown_faces/unknown_live_20260506_105813_974656.jpg', '2026-05-06 10:58:13.975803', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (202, 'unknown_faces/unknown_live_20260506_105815_493612.jpg', '2026-05-06 10:58:15.494717', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (203, 'unknown_faces/unknown_live_20260506_105820_046532.jpg', '2026-05-06 10:58:20.047605', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (204, 'unknown_faces/unknown_live_20260506_105823_013200.jpg', '2026-05-06 10:58:23.013880', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (205, 'unknown_faces/unknown_live_20260506_105824_729264.jpg', '2026-05-06 10:58:24.730272', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (206, 'unknown_faces/unknown_live_20260506_105830_608526.jpg', '2026-05-06 10:58:30.609169', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (207, 'unknown_faces/unknown_live_20260506_105833_480202.jpg', '2026-05-06 10:58:33.481076', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (208, 'unknown_faces/unknown_live_20260506_105835_005710.jpg', '2026-05-06 10:58:35.006407', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (209, 'unknown_faces/unknown_live_20260506_105836_562183.jpg', '2026-05-06 10:58:36.563150', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (210, 'unknown_faces/unknown_live_20260506_105836_586443.jpg', '2026-05-06 10:58:36.587043', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (211, 'unknown_faces/unknown_live_20260506_105836_608472.jpg', '2026-05-06 10:58:36.609311', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (212, 'unknown_faces/unknown_live_20260506_105838_177623.jpg', '2026-05-06 10:58:38.178910', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (213, 'unknown_faces/unknown_live_20260506_105838_202540.jpg', '2026-05-06 10:58:38.203163', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (214, 'unknown_faces/unknown_live_20260506_105839_532790.jpg', '2026-05-06 10:58:39.533960', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (215, 'unknown_faces/unknown_live_20260506_105841_018805.jpg', '2026-05-06 10:58:41.019478', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (216, 'unknown_faces/unknown_live_20260506_105842_533187.jpg', '2026-05-06 10:58:42.534021', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (217, 'unknown_faces/unknown_live_20260506_105844_030871.jpg', '2026-05-06 10:58:44.031545', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (218, 'unknown_faces/unknown_live_20260506_105845_530309.jpg', '2026-05-06 10:58:45.531121', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (219, 'unknown_faces/unknown_live_20260506_105845_554428.jpg', '2026-05-06 10:58:45.555017', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (220, 'unknown_faces/unknown_live_20260506_105845_574055.jpg', '2026-05-06 10:58:45.575394', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (221, 'unknown_faces/unknown_live_20260506_105845_594794.jpg', '2026-05-06 10:58:45.595391', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (222, 'unknown_faces/unknown_live_20260506_105847_013559.jpg', '2026-05-06 10:58:47.014666', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (223, 'unknown_faces/unknown_live_20260506_105847_084949.jpg', '2026-05-06 10:58:47.085671', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (224, 'unknown_faces/unknown_live_20260506_105847_106493.jpg', '2026-05-06 10:58:47.107259', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (225, 'unknown_faces/unknown_live_20260506_105848_505080.jpg', '2026-05-06 10:58:48.505966', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (226, 'unknown_faces/unknown_live_20260506_105848_530958.jpg', '2026-05-06 10:58:48.531665', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (227, 'unknown_faces/unknown_live_20260506_105849_986928.jpg', '2026-05-06 10:58:49.987458', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (228, 'unknown_faces/unknown_live_20260506_105850_009765.jpg', '2026-05-06 10:58:50.010343', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (229, 'unknown_faces/unknown_live_20260506_105850_028033.jpg', '2026-05-06 10:58:50.028602', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (230, 'unknown_faces/unknown_live_20260506_105851_470140.jpg', '2026-05-06 10:58:51.470926', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (231, 'unknown_faces/unknown_live_20260506_105851_491466.jpg', '2026-05-06 10:58:51.492033', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (232, 'unknown_faces/unknown_live_20260506_105851_511224.jpg', '2026-05-06 10:58:51.511839', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (233, 'unknown_faces/unknown_live_20260506_105851_530828.jpg', '2026-05-06 10:58:51.531460', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (234, 'unknown_faces/unknown_live_20260506_105853_301132.jpg', '2026-05-06 10:58:53.302186', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (235, 'unknown_faces/unknown_live_20260506_105853_323606.jpg', '2026-05-06 10:58:53.324218', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (236, 'unknown_faces/unknown_live_20260506_105853_343856.jpg', '2026-05-06 10:58:53.344736', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (237, 'unknown_faces/unknown_live_20260506_105854_498856.jpg', '2026-05-06 10:58:54.499648', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (238, 'unknown_faces/unknown_live_20260506_105854_520597.jpg', '2026-05-06 10:58:54.521246', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (239, 'unknown_faces/unknown_live_20260506_105855_995828.jpg', '2026-05-06 10:58:55.996650', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (240, 'unknown_faces/unknown_live_20260506_105856_018911.jpg', '2026-05-06 10:58:56.019798', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (241, 'unknown_faces/unknown_live_20260506_105858_980756.jpg', '2026-05-06 10:58:58.981312', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (242, 'unknown_faces/unknown_live_20260506_105900_524593.jpg', '2026-05-06 10:59:00.525244', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (243, 'unknown_faces/unknown_live_20260506_105902_005229.jpg', '2026-05-06 10:59:02.006396', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (244, 'unknown_faces/unknown_live_20260506_105902_077031.jpg', '2026-05-06 10:59:02.078005', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (245, 'unknown_faces/unknown_live_20260506_105903_536806.jpg', '2026-05-06 10:59:03.537686', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (246, 'unknown_faces/unknown_live_20260506_105903_559833.jpg', '2026-05-06 10:59:03.560439', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (247, 'unknown_faces/unknown_live_20260506_105905_034727.jpg', '2026-05-06 10:59:05.035373', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (248, 'unknown_faces/unknown_live_20260506_105906_484804.jpg', '2026-05-06 10:59:06.485645', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (249, 'unknown_faces/unknown_live_20260506_105906_507012.jpg', '2026-05-06 10:59:06.508339', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (250, 'unknown_faces/unknown_live_20260506_105908_036219.jpg', '2026-05-06 10:59:08.036922', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (251, 'unknown_faces/unknown_live_20260506_105908_061613.jpg', '2026-05-06 10:59:08.062197', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (252, 'unknown_faces/unknown_live_20260506_105909_510809.jpg', '2026-05-06 10:59:09.511385', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (253, 'unknown_faces/unknown_live_20260506_105911_021013.jpg', '2026-05-06 10:59:11.022694', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (254, 'unknown_faces/unknown_live_20260506_105912_536166.jpg', '2026-05-06 10:59:12.536991', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (255, 'unknown_faces/unknown_live_20260506_141533_280222.jpg', '2026-05-06 14:15:33.281535', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (256, 'unknown_faces/unknown_live_20260506_141536_647671.jpg', '2026-05-06 14:15:36.648382', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (257, 'unknown_faces/unknown_live_20260506_141537_994775.jpg', '2026-05-06 14:15:37.995475', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (258, 'unknown_faces/unknown_live_20260506_141540_992135.jpg', '2026-05-06 14:15:40.993130', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (259, 'unknown_faces/unknown_live_20260506_141550_029835.jpg', '2026-05-06 14:15:50.030775', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (260, 'unknown_faces/unknown_live_20260506_141551_498167.jpg', '2026-05-06 14:15:51.500297', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (261, 'unknown_faces/unknown_live_20260506_141553_013233.jpg', '2026-05-06 14:15:53.014148', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (262, 'unknown_faces/unknown_live_20260506_141556_000906.jpg', '2026-05-06 14:15:56.001785', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (263, 'unknown_faces/unknown_live_20260506_141557_496199.jpg', '2026-05-06 14:15:57.496874', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (264, 'unknown_faces/unknown_live_20260506_141558_989291.jpg', '2026-05-06 14:15:58.989982', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (265, 'unknown_faces/unknown_live_20260506_141600_480534.jpg', '2026-05-06 14:16:00.481163', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (266, 'unknown_faces/unknown_live_20260506_141602_130443.jpg', '2026-05-06 14:16:02.131317', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (267, 'unknown_faces/unknown_live_20260506_141623_082358.jpg', '2026-05-06 14:16:23.083242', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (268, 'unknown_faces/unknown_live_20260506_141624_651708.jpg', '2026-05-06 14:16:24.652463', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (269, 'unknown_faces/unknown_live_20260506_141626_108350.jpg', '2026-05-06 14:16:26.108969', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (270, 'unknown_faces/unknown_live_20260506_141627_538363.jpg', '2026-05-06 14:16:27.538959', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (271, 'unknown_faces/unknown_live_20260506_141629_110466.jpg', '2026-05-06 14:16:29.111208', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (272, 'unknown_faces/unknown_live_20260506_141630_556206.jpg', '2026-05-06 14:16:30.556880', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (273, 'unknown_faces/unknown_live_20260506_141633_514260.jpg', '2026-05-06 14:16:33.515088', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (274, 'unknown_faces/unknown_live_20260506_141635_007975.jpg', '2026-05-06 14:16:35.009408', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (275, 'unknown_faces/unknown_live_20260506_142045_481845.jpg', '2026-05-06 14:20:45.482753', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (276, 'unknown_faces/unknown_live_20260506_142050_184408.jpg', '2026-05-06 14:20:50.185236', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (277, 'unknown_faces/unknown_live_20260506_142052_202442.jpg', '2026-05-06 14:20:52.203238', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (278, 'unknown_faces/unknown_live_20260506_142052_211993.jpg', '2026-05-06 14:20:52.212605', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (279, 'unknown_faces/unknown_live_20260506_142053_104250.jpg', '2026-05-06 14:20:53.104850', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (280, 'unknown_faces/unknown_live_20260506_142055_228040.jpg', '2026-05-06 14:20:55.228763', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (281, 'unknown_faces/unknown_live_20260506_142055_239519.jpg', '2026-05-06 14:20:55.240735', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (282, 'unknown_faces/unknown_live_20260506_142100_485346.jpg', '2026-05-06 14:21:00.486059', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (283, 'unknown_faces/unknown_live_20260506_142100_496138.jpg', '2026-05-06 14:21:00.496814', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (284, 'unknown_faces/unknown_live_20260506_142101_986239.jpg', '2026-05-06 14:21:01.987135', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (285, 'unknown_faces/unknown_live_20260506_142103_597221.jpg', '2026-05-06 14:21:03.597948', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (286, 'unknown_faces/unknown_live_20260506_142104_974982.jpg', '2026-05-06 14:21:04.975609', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (287, 'unknown_faces/unknown_live_20260506_142106_493850.jpg', '2026-05-06 14:21:06.494731', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (288, 'unknown_faces/unknown_live_20260506_142106_505934.jpg', '2026-05-06 14:21:06.506601', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (289, 'unknown_faces/unknown_live_20260506_142107_988448.jpg', '2026-05-06 14:21:07.989087', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (290, 'unknown_faces/unknown_live_20260506_142118_576926.jpg', '2026-05-06 14:21:18.578423', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (291, 'unknown_faces/unknown_live_20260506_142120_292263.jpg', '2026-05-06 14:21:20.293140', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (292, 'unknown_faces/unknown_live_20260506_142121_044790.jpg', '2026-05-06 14:21:21.045650', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (293, 'unknown_faces/unknown_live_20260506_142124_809551.jpg', '2026-05-06 14:21:24.810284', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (294, 'unknown_faces/unknown_live_20260506_142125_114258.jpg', '2026-05-06 14:21:25.114931', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (295, 'unknown_faces/unknown_live_20260506_142126_048773.jpg', '2026-05-06 14:21:26.049571', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (296, 'unknown_faces/unknown_live_20260506_142126_062048.jpg', '2026-05-06 14:21:26.062824', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (297, 'unknown_faces/unknown_live_20260506_142127_599637.jpg', '2026-05-06 14:21:27.600313', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (298, 'unknown_faces/unknown_live_20260506_142127_609818.jpg', '2026-05-06 14:21:27.610423', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (299, 'unknown_faces/unknown_live_20260506_142129_146604.jpg', '2026-05-06 14:21:29.147258', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (300, 'unknown_faces/unknown_live_20260506_142130_210048.jpg', '2026-05-06 14:21:30.210731', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (301, 'unknown_faces/unknown_live_20260506_142130_220501.jpg', '2026-05-06 14:21:30.221134', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (302, 'unknown_faces/unknown_live_20260506_142131_913546.jpg', '2026-05-06 14:21:31.914412', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (303, 'unknown_faces/unknown_live_20260506_142133_636755.jpg', '2026-05-06 14:21:33.637525', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (304, 'unknown_faces/unknown_live_20260506_142133_647637.jpg', '2026-05-06 14:21:33.648262', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (305, 'unknown_faces/unknown_live_20260506_142137_991055.jpg', '2026-05-06 14:21:37.991814', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (306, 'unknown_faces/unknown_live_20260506_142139_499456.jpg', '2026-05-06 14:21:39.500114', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (307, 'unknown_faces/unknown_live_20260516_141325_305000.jpg', '2026-05-16 14:13:25.306190', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (308, 'unknown_faces/unknown_live_20260516_141328_132823.jpg', '2026-05-16 14:13:28.133543', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (309, 'unknown_faces/unknown_live_20260516_141331_184346.jpg', '2026-05-16 14:13:31.185031', 'live', '', 1);
INSERT INTO "attendance_unknownfacelog" ("id", "image", "detected_at", "source", "notes", "camera_id") VALUES (310, 'unknown_faces/unknown_live_20260516_141335_591571.jpg', '2026-05-16 14:13:35.592242', 'live', '', 1);

-- ── auth_group ──
DROP TABLE IF EXISTS "auth_group";
CREATE TABLE "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);

-- ── auth_group_permissions ──
DROP TABLE IF EXISTS "auth_group_permissions";
CREATE TABLE "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── auth_permission ──
DROP TABLE IF EXISTS "auth_permission";
CREATE TABLE "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL);

INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (1, 1, 'add_logentry', 'Can add log entry');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (2, 1, 'change_logentry', 'Can change log entry');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (3, 1, 'delete_logentry', 'Can delete log entry');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (4, 1, 'view_logentry', 'Can view log entry');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (5, 2, 'add_permission', 'Can add permission');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (6, 2, 'change_permission', 'Can change permission');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (7, 2, 'delete_permission', 'Can delete permission');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (8, 2, 'view_permission', 'Can view permission');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (9, 3, 'add_group', 'Can add group');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (10, 3, 'change_group', 'Can change group');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (11, 3, 'delete_group', 'Can delete group');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (12, 3, 'view_group', 'Can view group');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (13, 4, 'add_user', 'Can add user');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (14, 4, 'change_user', 'Can change user');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (15, 4, 'delete_user', 'Can delete user');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (16, 4, 'view_user', 'Can view user');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (17, 5, 'add_contenttype', 'Can add content type');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (18, 5, 'change_contenttype', 'Can change content type');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (19, 5, 'delete_contenttype', 'Can delete content type');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (20, 5, 'view_contenttype', 'Can view content type');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (21, 6, 'add_session', 'Can add session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (22, 6, 'change_session', 'Can change session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (23, 6, 'delete_session', 'Can delete session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (24, 6, 'view_session', 'Can view session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (25, 7, 'add_classroomschedule', 'Can add classroom schedule');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (26, 7, 'change_classroomschedule', 'Can change classroom schedule');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (27, 7, 'delete_classroomschedule', 'Can delete classroom schedule');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (28, 7, 'view_classroomschedule', 'Can view classroom schedule');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (29, 8, 'add_student', 'Can add student');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (30, 8, 'change_student', 'Can change student');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (31, 8, 'delete_student', 'Can delete student');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (32, 8, 'view_student', 'Can view student');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (33, 9, 'add_attendancerecord', 'Can add attendance record');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (34, 9, 'change_attendancerecord', 'Can change attendance record');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (35, 9, 'delete_attendancerecord', 'Can delete attendance record');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (36, 9, 'view_attendancerecord', 'Can view attendance record');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (37, 10, 'add_trainingphoto', 'Can add training photo');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (38, 10, 'change_trainingphoto', 'Can change training photo');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (39, 10, 'delete_trainingphoto', 'Can delete training photo');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (40, 10, 'view_trainingphoto', 'Can view training photo');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (41, 11, 'add_course', 'Can add course');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (42, 11, 'change_course', 'Can change course');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (43, 11, 'delete_course', 'Can delete course');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (44, 11, 'view_course', 'Can view course');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (45, 12, 'add_unknownfacelog', 'Can add unknown face log');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (46, 12, 'change_unknownfacelog', 'Can change unknown face log');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (47, 12, 'delete_unknownfacelog', 'Can delete unknown face log');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (48, 12, 'view_unknownfacelog', 'Can view unknown face log');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (49, 13, 'add_coursesession', 'Can add course session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (50, 13, 'change_coursesession', 'Can change course session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (51, 13, 'delete_coursesession', 'Can delete course session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (52, 13, 'view_coursesession', 'Can view course session');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (53, 14, 'add_enrollment', 'Can add enrollment');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (54, 14, 'change_enrollment', 'Can change enrollment');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (55, 14, 'delete_enrollment', 'Can delete enrollment');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (56, 14, 'view_enrollment', 'Can view enrollment');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (57, 15, 'add_camera', 'Can add camera');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (58, 15, 'change_camera', 'Can change camera');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (59, 15, 'delete_camera', 'Can delete camera');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (60, 15, 'view_camera', 'Can view camera');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (61, 16, 'add_classe', 'Can add Classe');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (62, 16, 'change_classe', 'Can change Classe');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (63, 16, 'delete_classe', 'Can delete Classe');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (64, 16, 'view_classe', 'Can view Classe');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (65, 17, 'add_schedule', 'Can add Horaire');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (66, 17, 'change_schedule', 'Can change Horaire');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (67, 17, 'delete_schedule', 'Can delete Horaire');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (68, 17, 'view_schedule', 'Can view Horaire');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (69, 18, 'add_attendanceauditlog', 'Can add Journal d''audit');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (70, 18, 'change_attendanceauditlog', 'Can change Journal d''audit');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (71, 18, 'delete_attendanceauditlog', 'Can delete Journal d''audit');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (72, 18, 'view_attendanceauditlog', 'Can view Journal d''audit');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (73, 19, 'add_jourferie', 'Can add Jour ferie');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (74, 19, 'change_jourferie', 'Can change Jour ferie');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (75, 19, 'delete_jourferie', 'Can delete Jour ferie');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (76, 19, 'view_jourferie', 'Can view Jour ferie');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (77, 20, 'add_salle', 'Can add Salle');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (78, 20, 'change_salle', 'Can change Salle');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (79, 20, 'delete_salle', 'Can delete Salle');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (80, 20, 'view_salle', 'Can view Salle');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (81, 21, 'add_systemconfig', 'Can add Configuration systeme');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (82, 21, 'change_systemconfig', 'Can change Configuration systeme');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (83, 21, 'delete_systemconfig', 'Can delete Configuration systeme');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (84, 21, 'view_systemconfig', 'Can view Configuration systeme');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (85, 22, 'add_facedetectionevent', 'Can add Evenement de detection');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (86, 22, 'change_facedetectionevent', 'Can change Evenement de detection');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (87, 22, 'delete_facedetectionevent', 'Can delete Evenement de detection');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (88, 22, 'view_facedetectionevent', 'Can view Evenement de detection');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (89, 23, 'add_schooldayconfig', 'Can add Configuration journee scolaire');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (90, 23, 'change_schooldayconfig', 'Can change Configuration journee scolaire');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (91, 23, 'delete_schooldayconfig', 'Can delete Configuration journee scolaire');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (92, 23, 'view_schooldayconfig', 'Can view Configuration journee scolaire');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (93, 24, 'add_dailyattendance', 'Can add Presence journaliere');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (94, 24, 'change_dailyattendance', 'Can change Presence journaliere');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (95, 24, 'delete_dailyattendance', 'Can delete Presence journaliere');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (96, 24, 'view_dailyattendance', 'Can view Presence journaliere');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (97, 25, 'add_recognitionreviewqueue', 'Can add Ticket de revue reconnaissance');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (98, 25, 'change_recognitionreviewqueue', 'Can change Ticket de revue reconnaissance');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (99, 25, 'delete_recognitionreviewqueue', 'Can delete Ticket de revue reconnaissance');
INSERT INTO "auth_permission" ("id", "content_type_id", "codename", "name") VALUES (100, 25, 'view_recognitionreviewqueue', 'Can view Ticket de revue reconnaissance');

-- ── auth_user ──
DROP TABLE IF EXISTS "auth_user";
CREATE TABLE "auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "first_name" varchar(150) NOT NULL);

INSERT INTO "auth_user" ("id", "password", "last_login", "is_superuser", "username", "last_name", "email", "is_staff", "is_active", "date_joined", "first_name") VALUES (1, 'pbkdf2_sha256$1000000$HK70j7GXEw6q9FXke80Ge3$kjTn+k2lhd3PwTCmJwYI50zoRjVwkNySqPCuE1bUubc=', NULL, 1, 'admin', '', '', 1, 1, '2026-05-16 14:53:15.646646', '');

-- ── auth_user_groups ──
DROP TABLE IF EXISTS "auth_user_groups";
CREATE TABLE "auth_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── auth_user_user_permissions ──
DROP TABLE IF EXISTS "auth_user_user_permissions";
CREATE TABLE "auth_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);

-- ── django_admin_log ──
DROP TABLE IF EXISTS "django_admin_log";
CREATE TABLE "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL);

-- ── django_content_type ──
DROP TABLE IF EXISTS "django_content_type";
CREATE TABLE "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);

INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (1, 'admin', 'logentry');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (2, 'auth', 'permission');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (3, 'auth', 'group');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (4, 'auth', 'user');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (5, 'contenttypes', 'contenttype');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (6, 'sessions', 'session');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (7, 'attendance', 'classroomschedule');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (8, 'attendance', 'student');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (9, 'attendance', 'attendancerecord');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (10, 'attendance', 'trainingphoto');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (11, 'attendance', 'course');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (12, 'attendance', 'unknownfacelog');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (13, 'attendance', 'coursesession');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (14, 'attendance', 'enrollment');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (15, 'attendance', 'camera');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (16, 'attendance', 'classe');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (17, 'attendance', 'schedule');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (18, 'attendance', 'attendanceauditlog');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (19, 'attendance', 'jourferie');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (20, 'attendance', 'salle');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (21, 'attendance', 'systemconfig');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (22, 'attendance', 'facedetectionevent');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (23, 'attendance', 'schooldayconfig');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (24, 'attendance', 'dailyattendance');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (25, 'attendance', 'recognitionreviewqueue');

-- ── django_migrations ──
DROP TABLE IF EXISTS "django_migrations";
CREATE TABLE "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL);

INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (1, 'contenttypes', '0001_initial', '2026-05-05 15:43:50.864742');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (2, 'auth', '0001_initial', '2026-05-05 15:43:50.915726');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (3, 'admin', '0001_initial', '2026-05-05 15:43:50.951241');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (4, 'admin', '0002_logentry_remove_auto_add', '2026-05-05 15:43:50.983160');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (5, 'admin', '0003_logentry_add_action_flag_choices', '2026-05-05 15:43:51.006202');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (6, 'attendance', '0001_initial', '2026-05-05 15:43:51.042565');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (7, 'contenttypes', '0002_remove_content_type_name', '2026-05-05 15:43:51.119870');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (8, 'auth', '0002_alter_permission_name_max_length', '2026-05-05 15:43:51.157114');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (9, 'auth', '0003_alter_user_email_max_length', '2026-05-05 15:43:51.194501');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (10, 'auth', '0004_alter_user_username_opts', '2026-05-05 15:43:51.217804');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (11, 'auth', '0005_alter_user_last_login_null', '2026-05-05 15:43:51.264136');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (12, 'auth', '0006_require_contenttypes_0002', '2026-05-05 15:43:51.274108');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (13, 'auth', '0007_alter_validators_add_error_messages', '2026-05-05 15:43:51.294451');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (14, 'auth', '0008_alter_user_username_max_length', '2026-05-05 15:43:51.330331');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (15, 'auth', '0009_alter_user_last_name_max_length', '2026-05-05 15:43:51.365700');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (16, 'auth', '0010_alter_group_name_max_length', '2026-05-05 15:43:51.404876');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (17, 'auth', '0011_update_proxy_permissions', '2026-05-05 15:43:51.441968');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (18, 'auth', '0012_alter_user_first_name_max_length', '2026-05-05 15:43:51.487793');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (19, 'sessions', '0001_initial', '2026-05-05 15:43:51.510375');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (20, 'attendance', '0002_course_unknownfacelog_student_date_of_birth_and_more', '2026-05-05 18:19:50.197648');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (21, 'attendance', '0003_camera_trainingphoto_face_detected_and_more', '2026-05-05 18:38:21.979511');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (22, 'attendance', '0004_classe_coursesession_status_and_more', '2026-05-16 14:30:16.723901');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (23, 'attendance', '0005_attendanceauditlog_jourferie_salle_and_more', '2026-05-16 14:40:49.757164');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (24, 'attendance', '0006_systemconfig_facedetectionevent', '2026-05-16 14:52:50.668206');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (25, 'attendance', '0007_daily_attendance_school_day_config_camera_zone', '2026-05-16 15:01:04.915652');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (26, 'attendance', '0008_camera_detection_mode_status', '2026-05-16 15:06:05.708830');
INSERT INTO "django_migrations" ("id", "app", "name", "applied") VALUES (27, 'attendance', '0009_review_queue_and_confidence_tiers', '2026-05-16 15:12:10.595784');

-- ── django_session ──
DROP TABLE IF EXISTS "django_session";
CREATE TABLE "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);

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

PRAGMA foreign_keys=ON;
COMMIT;
