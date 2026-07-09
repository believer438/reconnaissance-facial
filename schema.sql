-- =============================================
-- SCHEMA SUPABASE / PostgreSQL
-- =============================================

-- Table des élèves
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    matricule VARCHAR(50) UNIQUE,
    classe VARCHAR(50),
    photo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des horaires par classe
CREATE TABLE IF NOT EXISTS schedule (
    id SERIAL PRIMARY KEY,
    classe VARCHAR(50) NOT NULL,
    heure_debut TIME NOT NULL
);

-- Table des présences
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    date DATE NOT NULL,
    heure_arrivee TIME NOT NULL,
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('Present', 'Retard', 'Absent')),
    UNIQUE(student_id, date)
);

-- =============================================
-- DONNÉES D'EXEMPLE (à adapter)
-- =============================================

-- Exemple d'horaire : classe "L3Info" commence à 08h00
INSERT INTO schedule (classe, heure_debut) VALUES ('L3Info', '08:00:00') ON CONFLICT DO NOTHING;
INSERT INTO schedule (classe, heure_debut) VALUES ('L2Info', '08:30:00') ON CONFLICT DO NOTHING;
