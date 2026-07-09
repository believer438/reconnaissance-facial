-- =============================================
-- SCHEMA SQLite (base de données locale)
-- =============================================

-- Table des élèves
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT UNIQUE NOT NULL,
    matricule TEXT UNIQUE,
    classe TEXT,
    photo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des horaires par classe
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classe TEXT NOT NULL,
    heure_debut TEXT NOT NULL
);

-- Table des présences
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER REFERENCES students(id),
    date TEXT NOT NULL,
    heure_arrivee TEXT NOT NULL,
    statut TEXT NOT NULL CHECK (statut IN ('Present', 'Retard', 'Absent')),
    UNIQUE(student_id, date)
);

-- =============================================
-- DONNÉES D'EXEMPLE (à adapter)
-- =============================================
INSERT OR IGNORE INTO schedule (classe, heure_debut) VALUES ('L3Info', '08:00:00');
INSERT OR IGNORE INTO schedule (classe, heure_debut) VALUES ('L2Info', '08:30:00');
