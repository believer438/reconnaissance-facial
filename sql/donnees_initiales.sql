-- ============================================================
-- UniPresence — Donnees initiales (configuration de base)
-- A executer APRES schema.sql pour pre-remplir la configuration
-- ============================================================

BEGIN TRANSACTION;

-- attendance_systemconfig : (vide)

-- attendance_schooldayconfig : (vide)

-- Table: attendance_classroomschedule (3 ligne(s))
INSERT OR REPLACE INTO "attendance_classroomschedule" ("id", "classroom", "start_time", "late_after_minutes") VALUES (1, 'L3 Info', '08:00:00', 5);
INSERT OR REPLACE INTO "attendance_classroomschedule" ("id", "classroom", "start_time", "late_after_minutes") VALUES (2, 'L2 Info', '08:30:00', 10);
INSERT OR REPLACE INTO "attendance_classroomschedule" ("id", "classroom", "start_time", "late_after_minutes") VALUES (3, 'M1 Data', '09:00:00', 10);

-- attendance_jourferie : (vide)

-- Table: auth_user (1 ligne(s))
INSERT OR REPLACE INTO "auth_user" ("id", "password", "last_login", "is_superuser", "username", "last_name", "email", "is_staff", "is_active", "date_joined", "first_name") VALUES (1, 'pbkdf2_sha256$1000000$HK70j7GXEw6q9FXke80Ge3$kjTn+k2lhd3PwTCmJwYI50zoRjVwkNySqPCuE1bUubc=', NULL, 1, 'admin', '', '', 1, 1, '2026-05-16 14:53:15.646646', '');

COMMIT;
