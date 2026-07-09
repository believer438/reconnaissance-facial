#!/usr/bin/env bash
# =============================================================================
# UniPresence — Script d'installation locale (Linux / macOS)
# Exécuter depuis le dossier du projet : bash sql/setup_local.sh
# =============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   UniPresence — Installation locale             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── 1. Vérifier Python
echo "[1/5] Vérification de Python..."
if ! command -v python3 &>/dev/null; then
    echo "  ERREUR : Python 3 n'est pas installé."
    echo "  Installez Python 3.10+ depuis https://www.python.org/"
    exit 1
fi
PY_VERSION=$(python3 --version 2>&1)
echo "  OK : $PY_VERSION"

# ── 2. Environnement virtuel
echo ""
echo "[2/5] Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  OK : venv créé"
else
    echo "  OK : venv déjà existant"
fi
source venv/bin/activate

# ── 3. Dépendances
echo ""
echo "[3/5] Installation des dépendances Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  OK : dépendances installées"

# ── 4. Base de données
echo ""
echo "[4/5] Initialisation de la base de données..."
if [ -f "db.sqlite3" ]; then
    echo "  INFO : db.sqlite3 déjà présent — migrations seulement"
    python3 manage.py migrate --run-syncdb
else
    echo "  Création d'une nouvelle base..."
    python3 manage.py migrate --run-syncdb
    echo "  Application des données initiales..."
    python3 sql/restore_db.py --config-only 2>/dev/null || true
fi
echo "  OK : base de données prête"

# ── 5. Fichiers statiques
echo ""
echo "[5/5] Collecte des fichiers statiques..."
python3 manage.py collectstatic --noinput -v 0 2>/dev/null || true
echo "  OK"

# ── Résumé
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   Installation terminée avec succès !           ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "  Pour lancer le serveur :"
echo "    source venv/bin/activate"
echo "    python manage.py runserver 0.0.0.0:8008"
echo ""
echo "  Accès : http://localhost:8008/facial/"
echo "  Admin : admin / admin123"
echo ""
