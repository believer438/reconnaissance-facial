# UniPresence — Installation locale

## Contenu de ce dossier

| Fichier | Description |
|---------|-------------|
| `schema.sql` | Schéma complet de la base de données (tables + index) |
| `donnees_initiales.sql` | Configuration de base + compte admin |
| `sauvegarde_complete.sql` | Dump complet (schema + toutes les données) |
| `setup_local.sh` | Script d'installation automatique (Linux/macOS) |
| `setup_local_windows.bat` | Script d'installation automatique (Windows) |
| `restore_db.py` | Restaurer la base de données depuis `sauvegarde_complete.sql` |

---

## Installation rapide (Linux / macOS)

```bash
# 1. Cloner ou copier le dossier du projet
cd reconnaissance_facial

# 2. Créer un environnement virtuel Python
python3 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Option A — Base vierge (structure seulement)
python restore_db.py --schema-only

# 5. Option B — Restaurer une sauvegarde complète
python restore_db.py --full

# 6. Lancer le serveur
python manage.py runserver 0.0.0.0:8008
```

Accéder à : http://localhost:8008/facial/
Compte admin : **admin** / **admin123**

---

## Installation rapide (Windows)

```bat
:: Double-cliquer sur setup_local_windows.bat
:: OU depuis l'invite de commandes :
setup_local_windows.bat
```

---

## Base de données SQLite

Le projet utilise SQLite — **aucun serveur de base de données n'est nécessaire**.
Le fichier de base de données est : `db.sqlite3` (créé automatiquement au premier lancement).

### Appliquer les migrations manuellement

```bash
python manage.py migrate
```

### Recréer le compte admin

```bash
python manage.py createsuperuser
```

### Exporter une nouvelle sauvegarde

```bash
python manage.py dumpdata --natural-foreign --indent 2 > sql/backup_$(date +%Y%m%d).json
```

---

## Structure des dossiers importants

```
reconnaissance_facial/
├── apps/attendance/          ← Application principale
│   ├── models.py             ← Modèles de données
│   ├── views.py              ← Vues / contrôleurs
│   ├── urls.py               ← Routes URL
│   └── migrations/           ← Migrations de base de données
├── config/
│   └── settings.py           ← Configuration Django
├── media/                    ← Photos des étudiants (à sauvegarder!)
├── static/                   ← Fichiers statiques
├── templates/                ← Templates HTML
├── db.sqlite3                ← Base de données (à sauvegarder!)
├── sql/                      ← Fichiers SQL (ce dossier)
└── requirements.txt          ← Dépendances Python
```

---

## Sauvegarde des données importantes

**Toujours sauvegarder ces fichiers avant une mise à jour :**

1. `db.sqlite3` — toute la base de données
2. `media/` — toutes les photos des étudiants et le modèle entraîné

```bash
# Sauvegarde rapide
cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
cp -r media/ media_backup_$(date +%Y%m%d)/
```

---

## Dépendances requises

```
django>=5.2
opencv-contrib-python
numpy
pillow
```

Voir `requirements.txt` pour la liste complète.
