# Architecture Technique — Comment les pièces s'assemblent

## Introduction

Ce document explique comment le projet est organisé techniquement. Imaginez un immeuble : l'architecture, c'est le plan de l'immeuble — quels étages il y a, où sont les escaliers, comment on va d'un endroit à l'autre.

---

## Les grandes couches du système

### Couche 1 : L'interface utilisateur (ce que vous voyez)

C'est la partie visible dans votre navigateur web (Chrome, Firefox, Edge...). Elle est faite avec :
- **HTML** : la structure des pages (comme le squelette d'une page)
- **CSS** : la mise en forme (couleurs, polices, disposition)
- **JavaScript** : les interactions (ce qui bouge quand vous cliquez, la caméra en direct)

Les fichiers de cette couche se trouvent dans le dossier `templates/` (les pages web) et `static/css/` (le style).

### Couche 2 : Le serveur web (Django)

**Django** est un framework Python. Un « framework », c'est comme une boîte à outils avec des règles. Django gère :
- La réception des requêtes du navigateur (« l'utilisateur veut voir la liste des élèves »)
- L'exécution de la logique métier (« récupère tous les élèves actifs »)
- L'envoi de la réponse (une page HTML, ou des données JSON)

**Pourquoi Django ?** Django est très populaire, stable, et intègre nativement la gestion des utilisateurs, de la base de données, et de l'administration. C'est parfait pour un projet scolaire qui n'a pas besoin de dépasser des milliers d'utilisateurs simultanés.

### Couche 3 : Le moteur d'intelligence artificielle (OpenCV + LBPH)

C'est le cœur du projet. Cette couche :
- Reçoit une image (photo ou capture webcam)
- Détecte les visages dans cette image (algorithme Haar Cascade)
- Identifie à qui appartient chaque visage (algorithme LBPH)
- Retourne le résultat (nom, score de confiance, coordonnées du visage)

**Pourquoi OpenCV ?** OpenCV est la bibliothèque de vision par ordinateur la plus utilisée au monde. Elle est gratuite, rapide, et l'algorithme LBPH est inclus. Pas besoin de connexion internet ou de clé API payante.

### Couche 4 : La base de données (SQLite)

C'est ici que toutes les informations sont sauvegardées en permanence : les élèves, les cours, les présences, les photos, les configurations...

**SQLite** est une base de données stockée dans un seul fichier (`db.sqlite3`). C'est simple, portable, et parfait pour une application utilisée par quelques dizaines à quelques centaines d'utilisateurs simultanés.

**Pourquoi pas MySQL ou PostgreSQL ?** Ces systèmes nécessitent un serveur séparé à configurer et maintenir. SQLite est suffisant pour ce contexte scolaire et réduit la complexité de déploiement.

---

## Comment une page se charge — exemple concret

Imaginez que le secrétaire clique sur « Liste des élèves » :

```
1. Le navigateur envoie une requête HTTP GET vers /facial/students/

2. Django reçoit la requête
   → Vérifie que l'utilisateur est connecté (middleware)
   → Appelle la fonction "student_list" dans views.py

3. views.py demande à la base de données :
   SELECT * FROM attendance_student WHERE is_active = True ORDER BY full_name

4. La base de données retourne la liste des élèves

5. views.py envoie cette liste au template student_list.html

6. Le template génère du HTML avec les données des élèves

7. Django envoie ce HTML au navigateur

8. Le navigateur affiche la page
```

Toute cette chaîne se déroule en moins d'une seconde.

---

## Comment fonctionne la reconnaissance en direct (webcam)

C'est plus complexe car c'est en temps réel :

```
1. L'utilisateur ouvre la page "Caméra Live"

2. Le navigateur demande l'accès à la webcam (getUserMedia)
   → L'utilisateur autorise

3. Toutes les X secondes (configurable), le JavaScript :
   a. Capture une image de la vidéo sur un "canvas" (zone de dessin)
   b. Convertit l'image en format base64 (texte encodé)
   c. Envoie cette image au serveur via fetch() POST

4. Django reçoit l'image au endpoint /facial/api/recognize-frame/
   → Décode l'image base64
   → Applique le pipeline LBPH
   → Retourne un JSON avec les résultats

5. Le JavaScript reçoit le JSON et :
   a. Dessine des rectangles colorés autour des visages reconnus
   b. Affiche le nom de l'élève au-dessus du rectangle
   c. Vert = reconnu, Rouge = inconnu

6. Les présences sont enregistrées automatiquement dans la base de données
```

---

## Organisation des dossiers

```
reconnaissance_facial_2/
│
├── config/                     ← Configuration globale Django
│   ├── settings.py             ← Tous les paramètres (base de données, médias, fuseau horaire...)
│   └── urls.py                 ← "Table des matières" des URLs du site
│
├── apps/attendance/            ← L'application principale (toute la logique)
│   ├── models.py               ← Définition de toutes les tables de la base de données
│   ├── views.py                ← Fonctions qui répondent aux requêtes
│   ├── forms.py                ← Formulaires de saisie (validation des données)
│   ├── admin.py                ← Interface d'administration Django
│   ├── middleware.py           ← Filtre de sécurité (obligation de se connecter)
│   ├── migrations/             ← Historique des changements de la base de données
│   ├── services/               ← Services spécialisés
│   │   ├── training.py         ← Entraînement du modèle LBPH
│   │   ├── recognition.py      ← Reconnaissance faciale
│   │   ├── daily_attendance.py ← Gestion présence journalière (école secondaire)
│   │   ├── paths.py            ← Chemins vers les fichiers du modèle IA
│   │   └── vision.py           ← Utilitaires OpenCV
│   └── management/commands/    ← Commandes automatiques
│       ├── auto_daily.py       ← Génération automatique des absences
│       └── seed_demo_data.py   ← Données de démonstration
│
├── templates/                  ← Pages HTML
│   ├── base.html               ← Modèle de base (menu, entête, pied de page)
│   └── attendance/             ← Toutes les pages de l'app
│       ├── dashboard.html      ← Tableau de bord principal
│       ├── student_list.html   ← Liste des élèves
│       ├── camera_live.html    ← Page caméra en direct
│       └── ...                 ← Et toutes les autres pages
│
├── static/css/
│   └── app.css                 ← Style de l'interface (design personnalisé)
│
├── media/                      ← Fichiers générés par le système
│   ├── students/               ← Photos des élèves
│   ├── models/                 ← Fichiers du modèle IA entraîné (trainer.yml, labels.json)
│   ├── unknown_faces/          ← Photos des visages non reconnus
│   └── review_queue/           ← Photos en attente de validation manuelle
│
├── manage.py                   ← Point d'entrée Django (commandes)
├── training.py                 ← Déclencheur d'entraînement depuis la ligne de commande
├── requirements.txt            ← Liste des bibliothèques Python nécessaires
└── start.sh                    ← Script de démarrage automatique
```

---

## Le fichier start.sh — Comment le système démarre

Quand on lance le projet, le script `start.sh` fait automatiquement :

1. **Trouve Python** sur le système (cherche dans plusieurs endroits)
2. **Installe les dépendances** (bibliothèques Python : Django, OpenCV, etc.)
3. **Applique les migrations** (crée ou met à jour les tables de la base de données)
4. **Crée un compte administrateur** par défaut (login: `admin`, mot de passe: `admin123`) si aucun n'existe
5. **Démarre le serveur** Django sur le port configuré

---

## Le fichier settings.py — Configuration centrale

Ce fichier est le cerveau de la configuration. Les paramètres importants :

| Paramètre | Valeur | Signification |
|-----------|--------|---------------|
| `SECRET_KEY` | Variable d'environnement | Clé de sécurité unique du site |
| `DEBUG` | True | Mode développement (affiche les erreurs détaillées) |
| `DATABASES` | SQLite | Type de base de données |
| `TIME_ZONE` | Africa/Lubumbashi | Fuseau horaire (Lubumbashi, RDC) |
| `LANGUAGE_CODE` | fr-fr | Langue française |
| `MEDIA_ROOT` | media/ | Dossier de stockage des fichiers uploadés |
| `LOGIN_URL` | /facial/login/ | Page de connexion |

---

*Continuez avec `02_RECONNAISSANCE_FACIALE.md` pour comprendre comment l'IA reconnaît les visages.*
