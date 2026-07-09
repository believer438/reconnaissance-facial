#!/usr/bin/env python3
"""
UniPresence — Script de restauration de la base de données
Usage:
    python restore_db.py --schema-only   # Crée une base vierge (structure seulement)
    python restore_db.py --full          # Restaure sauvegarde_complete.sql
    python restore_db.py --config-only   # Restaure seulement la configuration initiale
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "db.sqlite3"

SCHEMA_SQL    = SCRIPT_DIR / "schema.sql"
FULL_SQL      = SCRIPT_DIR / "sauvegarde_complete.sql"
CONFIG_SQL    = SCRIPT_DIR / "donnees_initiales.sql"


def backup_existing():
    if DB_PATH.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = DB_PATH.parent / f"db_backup_{ts}.sqlite3"
        shutil.copy2(DB_PATH, bak)
        print(f"  [OK] Sauvegarde existante : {bak.name}")


def run_sql_file(sql_path: Path):
    if not sql_path.exists():
        print(f"  [ERREUR] Fichier introuvable : {sql_path}")
        sys.exit(1)
    sql = sql_path.read_text(encoding="utf-8")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(sql)
        conn.commit()
        print(f"  [OK] {sql_path.name} appliqué")
    except Exception as e:
        print(f"  [ERREUR] {e}")
        conn.close()
        sys.exit(1)
    conn.close()


def run_django_migrate():
    """Applique les migrations Django (complète le schema si nécessaire)."""
    import subprocess
    manage = PROJECT_DIR / "manage.py"
    if manage.exists():
        result = subprocess.run(
            [sys.executable, str(manage), "migrate", "--run-syncdb"],
            cwd=str(PROJECT_DIR),
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  [OK] Migrations Django appliquées")
        else:
            print("  [WARN] Migrations Django :", result.stderr[:200])


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--help"

    print("\n=== UniPresence — Restauration de la base de données ===\n")

    if mode == "--schema-only":
        print("Mode : Structure seulement (base vierge)")
        backup_existing()
        if DB_PATH.exists():
            DB_PATH.unlink()
        run_django_migrate()
        print("\n[DONE] Base vierge créée. Lancez : python manage.py runserver 0.0.0.0:8008")

    elif mode == "--full":
        print("Mode : Restauration complète (toutes les données)")
        backup_existing()
        if DB_PATH.exists():
            DB_PATH.unlink()
        run_sql_file(FULL_SQL)
        print("\n[DONE] Base restaurée. Lancez : python manage.py runserver 0.0.0.0:8008")

    elif mode == "--config-only":
        print("Mode : Configuration initiale seulement")
        if not DB_PATH.exists():
            print("  Base vide détectée — application des migrations d'abord...")
            run_django_migrate()
        run_sql_file(CONFIG_SQL)
        print("\n[DONE] Configuration initiale appliquée.")

    else:
        print("Usage:")
        print("  python restore_db.py --schema-only   # Base vierge")
        print("  python restore_db.py --full           # Restauration complète")
        print("  python restore_db.py --config-only    # Configuration initiale seulement")
        print()
        print("Fichiers SQL disponibles:")
        for f in [SCHEMA_SQL, FULL_SQL, CONFIG_SQL]:
            size = f"({f.stat().st_size // 1024} KB)" if f.exists() else "(manquant)"
            print(f"  {f.name:<35} {size}")


if __name__ == "__main__":
    main()
