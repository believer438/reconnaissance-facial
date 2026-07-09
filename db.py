import os
import sqlite3
from datetime import datetime, date
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY and not SUPABASE_URL.startswith("https://ton-projet"))

DB_PATH = os.path.join(BASE_DIR, "attendance.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema_local.sql")

if USE_SUPABASE:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[DB] Connexion Supabase activée")
else:
    supabase = None
    print("[DB] Mode SQLite local activé")

    def _init_sqlite():
        conn = sqlite3.connect(DB_PATH)
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

    _init_sqlite()


def _sqlite_conn():
    return sqlite3.connect(DB_PATH)


# -----------------------------------------------
# Récupérer un élève par son nom
# -----------------------------------------------
def get_student_by_name(nom):
    if USE_SUPABASE:
        res = supabase.table("students").select("*").eq("nom", nom).execute()
        return res.data[0] if res.data else None
    else:
        conn = _sqlite_conn()
        cur = conn.execute("SELECT * FROM students WHERE nom = ?", (nom,))
        row = cur.fetchone()
        conn.close()
        if row:
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))
        return None


# -----------------------------------------------
# Créer un élève s'il n'existe pas
# -----------------------------------------------
def get_or_create_student(nom, classe):
    student = get_student_by_name(nom)
    if student:
        return student

    if USE_SUPABASE:
        res = supabase.table("students").insert({
            "nom": nom,
            "classe": classe
        }).execute()
        return res.data[0]
    else:
        conn = _sqlite_conn()
        conn.execute("INSERT OR IGNORE INTO students (nom, classe) VALUES (?, ?)", (nom, classe))
        conn.commit()
        conn.close()
        return get_student_by_name(nom)


# -----------------------------------------------
# Récupérer l'horaire d'une classe
# -----------------------------------------------
def get_heure_debut(classe):
    if USE_SUPABASE:
        res = supabase.table("schedule").select("heure_debut").eq("classe", classe).execute()
        if res.data:
            return res.data[0]["heure_debut"]
    else:
        conn = _sqlite_conn()
        cur = conn.execute("SELECT heure_debut FROM schedule WHERE classe = ?", (classe,))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]

    return None


# -----------------------------------------------
# Vérifier si présence déjà enregistrée aujourd'hui
# -----------------------------------------------
def deja_enregistre(student_id, today):
    if USE_SUPABASE:
        res = supabase.table("attendance").select("id")\
            .eq("student_id", student_id)\
            .eq("date", str(today))\
            .execute()
        return len(res.data) > 0
    else:
        conn = _sqlite_conn()
        cur = conn.execute(
            "SELECT id FROM attendance WHERE student_id = ? AND date = ?",
            (student_id, str(today))
        )
        row = cur.fetchone()
        conn.close()
        return row is not None


# -----------------------------------------------
# Enregistrer la présence
# -----------------------------------------------
def enregistrer_presence(student_id, heure_arrivee, statut):
    today = date.today()

    if deja_enregistre(student_id, today):
        return False, "Déjà enregistré aujourd'hui"

    if USE_SUPABASE:
        supabase.table("attendance").insert({
            "student_id": student_id,
            "date": str(today),
            "heure_arrivee": str(heure_arrivee),
            "statut": statut
        }).execute()
    else:
        conn = _sqlite_conn()
        try:
            conn.execute(
                "INSERT INTO attendance (student_id, date, heure_arrivee, statut) VALUES (?, ?, ?, ?)",
                (student_id, str(today), str(heure_arrivee), statut)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Déjà enregistré aujourd'hui"
        conn.close()

    return True, statut


# -----------------------------------------------
# Déterminer le statut selon l'heure
# -----------------------------------------------
def determiner_statut(heure_arrivee, heure_debut_str):
    if heure_debut_str is None:
        return "Present"

    h, m, s = map(int, heure_debut_str.split(":"))
    heure_debut = heure_arrivee.replace(hour=h, minute=m, second=s, microsecond=0)

    if heure_arrivee <= heure_debut:
        return "Present"
    else:
        return "Retard"
