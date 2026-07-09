# UniPresence — Documentation Technique Complète

> Système universitaire de présence par reconnaissance faciale
> Stack : Django 5 · OpenCV LBPH · SQLite · HTML/CSS/JS pur

---

## 1. Architecture générale

```
navigateur (PC/Tablette)
       │
       │  HTTP (port 80 proxy Replit)
       ▼
  Django 5 — /facial/
       │
       ├── Base de données : SQLite (db.sqlite3)
       ├── Modèle LBPH     : media/models/trainer.yml
       ├── Labels          : media/models/labels.json
       ├── Photos élèves   : media/students/
       └── Inconnus        : media/unknown_faces/
```

### Flux de reconnaissance (photo upload)

```
Photo → Django → OpenCV (Haar Cascade) → Détection visages
                          │
              ┌───────────┘
              ▼
     LBPH.predict(visage_gris) → (label_id, distance)
              │
     distance < seuil (60) ?
       OUI → Étudiant identifié → AttendanceRecord créé
       NON → VisageInconnu → UnknownFaceLog créé
```

### Flux de reconnaissance live (webcam navigateur)

```
Navigateur
  getUserMedia() → <video> element
       │
  setInterval() → canvas.toDataURL('image/jpeg')
       │
  fetch POST → /facial/api/recognize-frame/  (JSON, base64)
       │
  Django → même pipeline LBPH
       │
  JSON réponse → { results: [{name, bbox, confidence...}] }
       │
  canvas overlay → drawRect() avec coordonnées bbox
```

---

## 2. Modèles de données

### Student (Étudiant)
| Champ | Type | Description |
|---|---|---|
| full_name | CharField | Nom complet (unique) |
| student_code | CharField | Matricule (unique) |
| classroom | CharField | Classe / Groupe |
| faculty | CharField | Faculté (choix) |
| email | EmailField | Email |
| phone | CharField | Téléphone |
| date_of_birth | DateField | Date de naissance |
| is_active | BooleanField | Actif dans le système |

### TrainingPhoto (Photo d'entraînement)
| Champ | Type | Description |
|---|---|---|
| student | FK → Student | Propriétaire |
| image | ImageField | Fichier photo (upload_to='students/') |
| trained_at | DateTimeField | NULL = pas encore entraîné · valeur = date d'entraînement |
| face_detected | BooleanField | False si aucun visage trouvé à l'entraînement |

**Comment distinguer photos entraînées vs nouvelles :**
- `trained_at IS NULL` → photo ajoutée APRÈS le dernier entraînement → ré-entraînement recommandé
- `trained_at IS NOT NULL` → photo incluse dans le modèle actuel
- `face_detected = False` → photo présente mais aucun visage détectable (floue, de dos, etc.)

### Camera
| Champ | Type | Description |
|---|---|---|
| name | CharField | Nom affiché |
| location | CharField | Emplacement physique |
| camera_type | CharField | webcam / usb / rtsp |
| source | CharField | Vide=webcam, '0'/'1'=USB index, 'rtsp://...'=IP |
| resolution_w/h | PositiveIntegerField | Résolution cible |
| is_active | BooleanField | Active ou non |

### Course / Enrollment / CourseSession
- **Course** → Cours (code, nom, faculté, professeur, crédits)
- **Enrollment** → Inscription d'un étudiant à un cours (unique par paire student+course)
- **CourseSession** → Séance de cours (date, heure début/fin, salle, tolérance retard, fermée?)

### AttendanceRecord
| Champ | Type | Description |
|---|---|---|
| student | FK → Student | Étudiant (peut être null si supprimé) |
| course_session | FK → CourseSession | Séance concernée |
| camera | FK → Camera | Caméra utilisée |
| student_name_snapshot | CharField | Nom au moment de l'enregistrement (snapshot) |
| recognized_at | DateTimeField | Horodatage exact |
| confidence_score | FloatField | Score de confiance 0-100 (100 = parfait) |
| status | CharField | present / late / absent |
| source | CharField | photo / live / manuel |

### UnknownFaceLog
Chaque visage non reconnu est sauvegardé ici avec sa photo JPEG rognée, l'horodatage, la source et la caméra.

---

## 3. Algorithme LBPH — Comment ça marche

### LBPH = Local Binary Pattern Histogram

1. **Encodage LBP** : Pour chaque pixel d'une image en niveaux de gris, on compare sa valeur avec ses N voisins sur un rayon R. On obtient un code binaire (0 ou 1) pour chaque voisin.
2. **Histogramme** : L'image est découpée en grille (grid_x × grid_y cellules). Pour chaque cellule, on calcule l'histogramme des codes LBP.
3. **Vecteur final** : Tous les histogrammes sont concaténés → vecteur de features.
4. **Reconnaissance** : Distance χ² (chi-carré) entre le vecteur test et tous les vecteurs d'entraînement. Plus la distance est faible, meilleure est la correspondance.

### Paramètres utilisés

```python
cv2.face.LBPHFaceRecognizer_create(
    radius=2,      # rayon LBP (1 = immédiat, 2 = plus large → moins sensible au bruit)
    neighbors=8,   # nombre de voisins comparés (standard)
    grid_x=8,      # cellules horizontales (plus élevé = plus fin = plus discriminant)
    grid_y=8,      # cellules verticales
)
```

**Pourquoi radius=2 ?** Le radius=1 (défaut) est trop sensible aux variations de lumière pixel à pixel. Le radius=2 capture des structures plus larges du visage (pores, textures).

### Seuil de distance (threshold)

```
distance = 0        → correspondance parfaite (même photo)
distance < 60       → bon match (seuil par défaut)
distance 60-80      → match incertain
distance > 80       → visage non reconnu → "Inconnu"
```

La conversion en score de confiance : `confiance = 100 - distance` (affiché dans l'interface).

---

## 4. Entraînement — Pipeline complet

```python
def train_model():
    pour chaque étudiant actif:
        pour chaque photo:
            1. Charger en niveaux de gris (PIL → numpy)
            2. Égalisation d'histogramme (equalizeHist)
                → normalise la luminosité, réduit l'effet éclairage
            3. Haar Cascade détection
                → scaleFactor=1.1, minNeighbors=5, minSize=(80,80)
            4. Vérification qualité (Laplacian variance)
                score = cv2.Laplacian(visage, CV_64F).var()
                si score < 50 → photo FLOUE → ignorée (skipped_blurry++)
            5. Augmentation : flip horizontal
                → double les données d'entraînement
                → rend le modèle robuste aux visages légèrement tournés
            6. Stocker face + label

    recognizer.train(faces, labels)
    recognizer.save('media/models/trainer.yml')
    labels.json → { student_id: {full_name, student_code, classroom} }

    Marquer TrainingPhoto.trained_at = now() pour toutes les photos utilisées
```

### Pourquoi l'égalisation d'histogramme ?

Sans égalisation : un étudiant entraîné sous un éclairage fluorescent sera mal reconnu sous la lumière naturelle.
Avec `cv2.equalizeHist()` : les valeurs de pixels sont redistribuées uniformément → le modèle apprend la structure du visage, pas la luminosité.

**Important** : la même transformation est appliquée à l'entraînement ET à la reconnaissance. Si elles diffèrent, les performances s'effondrent.

### Pourquoi le flip augmentation ?

Un étudiant peut se présenter légèrement tourné vers la gauche ou la droite. En ajoutant la version miroir horizontale de chaque photo, on entraîne le modèle sur les deux orientations → meilleure robustesse.

---

## 5. Reconnaissance — Pipeline complet

```python
def recognize_from_image_bytes(image_bytes, threshold=60.0, session=None):
    1. Décoder image bytes → numpy array (BGR)
    2. Convertir en niveaux de gris
    3. Égalisation d'histogramme (IDENTIQUE à l'entraînement !)
    4. Haar Cascade détection → liste de (x, y, w, h)
    
    pour chaque visage détecté:
        5. Rogner → visage_gris
        6. recognizer.predict(visage_gris) → (label_id, distance)
        7. Convertir distance en score : score = 100 - distance
        8. distance > threshold → statut = "unknown"
           distance ≤ threshold → chercher Student par label_id
        9. Vérifier si déjà marqué (same session or today)
        10. Calculer bbox en pourcentage (pour overlay canvas)
        11. Retourner FaceResult(status, student, confidence, bbox, ...)
```

### FaceResult — structure retournée

```python
@dataclass
class FaceResult:
    status: str           # "recognized" | "unknown"
    student: Student | None
    confidence: float     # 0-100 (plus élevé = meilleur)
    already_marked: bool  # True si déjà présent aujourd'hui / dans la session
    face_bytes: bytes     # JPEG du visage rogné (pour les inconnus)
    bbox_x_pct: float     # coordonnée X du visage en % de la largeur image
    bbox_y_pct: float     # coordonnée Y du visage en % de la hauteur image
    bbox_w_pct: float     # largeur du visage en % de la largeur image
    bbox_h_pct: float     # hauteur du visage en % de la hauteur image
```

Les coordonnées bbox en pourcentage permettent au JavaScript de dessiner les rectangles peu importe la résolution de l'écran ou la taille de la vidéo affichée.

---

## 6. Types de caméras

### Webcam navigateur (TYPE_WEBCAM) ✅ Recommandé sur Replit

```
Navigateur ──getUserMedia()──► <video>
                │
           canvas.toDataURL()
                │
     fetch POST /facial/api/recognize-frame/
                │
          Django LBPH pipeline
```

- Fonctionne sur tout appareil avec caméra intégrée ou USB
- Aucune configuration serveur requise
- Fonctionne sur Replit (le serveur n'a pas besoin d'accéder à la caméra)
- La caméra reste dans le navigateur, seules les frames JPEG sont envoyées

### Caméra USB (TYPE_USB)

```
Caméra USB ──(câble)──► PC serveur
                │
     cv2.VideoCapture(0)  # index 0 ou 1
                │
          traitement LBPH
```

- Requiert que le serveur Django tourne sur le PC auquel la caméra est branchée
- Index 0 = première caméra, index 1 = deuxième, etc.
- Non disponible sur Replit (serveur cloud sans périphérique physique)

### Caméra IP / RTSP (TYPE_RTSP) — Usage universitaire recommandé

```
Caméra IP ──(WiFi/Ethernet)──► Réseau local
                │
     cv2.VideoCapture("rtsp://192.168.1.10:554/stream")
                │
          traitement LBPH
```

- Caméra réseau professionnelle (Hikvision, Dahua, Axis...)
- Connectée au réseau via WiFi ou câble Ethernet (pas USB)
- Le serveur Django doit être sur le même réseau
- URL typique : `rtsp://admin:password@192.168.1.10:554/Streaming/Channels/101`
- Supporte des dizaines de caméras simultanées (via threads)

### Architecture recommandée pour une université

```
Amphi A        Salle 101      Couloir        Entrée
  [Cam IP] ──► [Cam IP] ──► [Cam IP] ──► [Cam IP]
       │              │             │           │
       └──────────────┴─────────────┴───────────┘
                             │
                    Réseau local université
                             │
                    Serveur central (PC puissant)
                    Django + LBPH
                             │
                    Interface web → n'importe quel PC
```

---

## 7. API de reconnaissance live

### Endpoint : POST /facial/api/recognize-frame/

**Requête (JSON) :**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgAB...",
  "session_id": "42",
  "camera_id": "3"
}
```

**Réponse (JSON) :**
```json
{
  "results": [
    {
      "status": "recognized",
      "name": "Bahati Joseph",
      "student_code": "UNI-001",
      "classroom": "L3 Info",
      "confidence": 87.3,
      "already_marked": false,
      "bbox": [15.2, 10.5, 22.1, 29.3]
    },
    {
      "status": "unknown",
      "name": "Inconnu",
      "student_code": "",
      "confidence": 0,
      "already_marked": false,
      "bbox": [55.0, 8.0, 20.0, 26.7]
    }
  ],
  "saved": 1,
  "error": null
}
```

**`bbox` format :** `[x%, y%, w%, h%]` — coordonnées du visage en pourcentage des dimensions de l'image. Utilisées par le JavaScript pour dessiner les rectangles sur le canvas overlay.

### Dessin des bounding boxes (JavaScript)

```javascript
function drawBoxes(results, imgW, imgH) {
    const ctx = overlay.getContext('2d');
    const scaleX = overlay.width / imgW;
    const scaleY = overlay.height / imgH;
    
    for (const r of results) {
        const [bxPct, byPct, bwPct, bhPct] = r.bbox;
        const x = (bxPct / 100) * imgW * scaleX;
        const y = (byPct / 100) * imgH * scaleY;
        const w = (bwPct / 100) * imgW * scaleX;
        const h = (bhPct / 100) * imgH * scaleY;
        
        ctx.strokeStyle = r.status === 'recognized' ? '#16a34a' : '#dc2626';
        ctx.strokeRect(x, y, w, h);
        // Afficher le nom au-dessus du rectangle...
    }
}
```

---

## 8. Gestion des présences

### Détermination du statut (present / late / absent)

```
Session définie ?
  OUI → datetime_seance + tolerence_retard_minutes
          avant OU pile → "present"
          après         → "late" (retard)
  NON → Chercher ClassroomSchedule pour la classe de l'étudiant
          Même logique avec l'horaire configuré
          Pas d'horaire → "present" par défaut
```

### Vérification de double-marquage

Avant de créer un AttendanceRecord, on vérifie :
- Si session définie : existe-t-il déjà un enregistrement pour (student, session, status=present/late) ?
- Si pas de session : existe-t-il déjà un enregistrement pour (student, aujourd'hui, status=present/late) ?

Si oui → `already_marked = True` → l'enregistrement n'est PAS créé en double.

### Clôture de session

Bouton "Marquer absents et fermer" :
1. Récupère tous les inscrits au cours de la session
2. Pour chaque inscrit sans présence enregistrée → crée un AttendanceRecord(status="absent", source="manuel")
3. Passe `session.closed = True`

---

## 9. Calcul du taux de présence

```python
def attendance_rate(self) -> float:
    total = self.attendance_records.filter(
        status__in=["present", "late", "absent"]
    ).count()
    absent = self.attendance_records.filter(status="absent").count()
    if total == 0:
        return 0.0
    return round((total - absent) / total * 100, 1)
```

Note : "present" + "late" comptent comme présent. "absent" baisse le taux.

---

## 10. Rapport & Export CSV

Le rapport agrège pour chaque étudiant :
- `total` = sessions avec statut (present + late + absent)
- `present` = sessions où statut est present ou late
- `absent` = sessions marquées absent
- `rate` = present / total × 100

L'export CSV utilise `;` comme séparateur et inclut un BOM UTF-8 (`\ufeff`) pour la compatibilité Excel.

---

## 11. Précision du modèle — Guide pratique

### Pour de meilleurs résultats

| Facteur | Recommandation |
|---|---|
| Nombre de photos | 5-15 photos par étudiant |
| Variété | Différents éclairages, légèrement différents angles |
| Qualité | Nettes, visage bien visible, face (pas de profil) |
| Résolution | 640×480 minimum, idéalement 1280×720 |
| Seuil (threshold) | 60 = standard, 50 = strict (moins de faux positifs), 70 = permissif |

### Indicateurs de confiance

| Score | Qualité |
|---|---|
| 90-100 | Excellent — très haute certitude |
| 75-90  | Bon — match fiable |
| 60-75  | Acceptable — limite du seuil |
| < 60   | Non reconnu → "Inconnu" |

### Causes fréquentes d'erreurs

1. **Photo floue** → rejetée à l'entraînement (score Laplacian < 50)
2. **Éclairage très différent** → égalisation d'histogramme atténue mais ne résout pas tout
3. **Lunettes / masque / barbe** → ajouter des photos avec ces variations
4. **Profil vs face** → Haar Cascade frontal ne détecte que les visages de face
5. **Pas assez de photos** → 1-2 photos suffit rarement, visez 5+

---

## 12. Structure des fichiers

```
artifacts/reconnaissance_facial/
├── manage.py
├── start.sh                    # Script de démarrage (migrate + runserver)
├── db.sqlite3                  # Base de données SQLite
├── SYSTEME.md                  # Cette documentation
├── config/
│   ├── settings.py             # Configuration Django (MEDIA_ROOT, STATIC, LOGIN_URL...)
│   └── urls.py                 # Routes racines (/facial/ → attendance.urls)
├── apps/attendance/
│   ├── models.py               # Student, TrainingPhoto, Camera, Course, Session...
│   ├── views.py                # Toutes les vues + API JSON
│   ├── urls.py                 # Routes de l'app
│   ├── forms.py                # StudentForm, CameraForm, CourseForm...
│   ├── admin.py                # Interface Django admin
│   ├── migrations/             # Migrations base de données
│   └── services/
│       ├── training.py         # train_model() — entraînement LBPH
│       ├── recognition.py      # recognize_from_image_bytes() — reconnaissance
│       ├── paths.py            # Chemins MODEL_FILE, LABEL_FILE
│       └── vision.py           # build_detector(), ensure_opencv_face_available()
├── templates/
│   ├── base.html               # Template de base (sidebar, topbar)
│   └── attendance/
│       ├── dashboard.html      # Tableau de bord
│       ├── student_list.html   # Liste étudiants
│       ├── student_detail.html # Fiche étudiant + photos
│       ├── camera_list.html    # Gestion caméras
│       ├── camera_live.html    # Page live webcam + reconnaissance temps réel
│       ├── course_list.html    # Cours & création
│       ├── course_detail.html  # Détail cours + inscrits + sessions
│       ├── session_detail.html # Détail séance + présences
│       ├── reports.html        # Rapport + export CSV
│       ├── unknown_faces.html  # Galerie visages inconnus
│       └── ...
└── static/css/
    └── app.css                 # UI flat PC-style, pas de framework externe
```

---

## 13. Déploiement et configuration

### Variables d'environnement
- `SESSION_SECRET` → clé secrète Django (SECRET_KEY)
- `PORT` → port du serveur (8091 sur Replit)

### start.sh
```bash
python manage.py migrate --run-syncdb
python manage.py runserver 0.0.0.0:$PORT
```

### Dépendances Python
```
django>=5.0
opencv-contrib-python  # contient cv2.face (LBPH)
Pillow                 # lecture images
numpy                  # calculs matriciels
```

---

## 14. Workflow type — Utilisation quotidienne

```
1. SETUP (une fois)
   Créer cours → Inscrire étudiants → Ajouter photos → Entraîner modèle

2. CHAQUE SÉANCE
   Créer session (date, heure, salle) → Ouvrir page Live cam
   → Étudiants passent devant la caméra → Présences automatiques
   
   OU : Uploader une photo de groupe → Plusieurs présences en un clic

3. FIN DE SÉANCE
   Session detail → "Marquer absents et fermer" → Rapport instantané

4. RAPPORTS
   Filtrer par cours/date → Voir taux → Exporter CSV → Excel
```

---

*Documentation générée automatiquement — UniPresence v2.0*
