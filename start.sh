#!/bin/bash
set -e
cd "$(dirname "$0")"

# ── Résoudre le chemin Python ──────────────────────────────────────────────────
PYTHON=""
for candidate in \
    "/home/runner/workspace/.pythonlibs/bin/python3" \
    "/home/runner/.pythonlibs/bin/python3" \
    "$(which python3 2>/dev/null)" \
    "$(which python 2>/dev/null)"; do
    if [ -x "$candidate" ]; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "==> [ERREUR] Aucun interpréteur Python trouvé. Installez Python 3.11+."
    exit 1
fi

echo "==> [INFO] Utilisation de Python : $PYTHON"

# ── Verrou anti-double démarrage ──────────────────────────────────────────────
LOCKFILE="/tmp/secpresence_django.lock"

# Supprimer le verrou précédent si laissé par un crash
rmdir "$LOCKFILE" 2>/dev/null || true

if ! mkdir "$LOCKFILE" 2>/dev/null; then
    echo "==> [INFO] Une instance est déjà en cours de démarrage. En attente..."
    for i in $(seq 1 60); do
        if curl -s --max-time 1 "http://localhost:${PORT:-8008}/facial/login/" > /dev/null 2>&1; then
            echo "==> [INFO] Serveur détecté sur port ${PORT:-8008}. En veille."
            break
        fi
        sleep 1
    done
    exec sleep infinity
fi

trap 'rmdir "$LOCKFILE" 2>/dev/null || true' EXIT INT TERM

# ── Installation des dépendances ──────────────────────────────────────────────
echo "==> [INFO] Installation des dépendances..."
"$PYTHON" -m pip install -r requirements.txt --quiet 2>&1 | grep -v "already satisfied" || true

# ── Migrations ────────────────────────────────────────────────────────────────
echo "==> [INFO] Migrations..."
"$PYTHON" manage.py migrate --run-syncdb 2>&1

# ── Création du superutilisateur par défaut ───────────────────────────────────
"$PYTHON" manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', '', 'admin123')
    print('==> Superutilisateur cree : admin / admin123')
" 2>&1 || true

# ── Démarrage Django ──────────────────────────────────────────────────────────
echo "==> [INFO] Démarrage Django sur 0.0.0.0:${PORT:-8008}..."
exec "$PYTHON" manage.py runserver 0.0.0.0:${PORT:-8008}
