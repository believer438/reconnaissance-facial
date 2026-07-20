# Technologies Utilisées — Les Outils et Pourquoi Ce Choix

## Introduction

Construire une application, c'est comme construire une maison : on choisit les matériaux en fonction de ce qu'on veut construire. Ce document explique chaque outil utilisé dans le projet et la raison de son choix.

---

## Langage principal : Python

### C'est quoi ?
Python est un langage de programmation créé en 1991. C'est l'un des langages les plus populaires au monde.

### Pourquoi Python ?
- **Lisibilité** : Le code Python ressemble presque à du français ou de l'anglais. Exemple : `if student.is_active:` se lit « si l'élève est actif »
- **Bibliothèques** : Python possède des milliers de bibliothèques toutes prêtes pour la vision par ordinateur, le web, la science des données...
- **Communauté** : Des millions de développeurs utilisent Python → beaucoup de documentation et d'aide disponible
- **Gratuit et open source** : Aucune licence à payer

### Utilisation dans ce projet
Python est utilisé pour TOUT le côté serveur : gestion des données, reconnaissance faciale, logique métier, export CSV...

---

## Framework web : Django 5

### C'est quoi ?
Django est un « framework » Python pour créer des applications web. Un framework, c'est une boîte à outils avec des règles et des conventions.

### Composants Django utilisés dans ce projet

**ORM (Object-Relational Mapping)**
L'ORM traduit les tables de la base de données en objets Python. Au lieu d'écrire du SQL brut :
```sql
SELECT * FROM attendance_student WHERE is_active = True
```
On écrit du Python :
```python
Student.objects.filter(is_active=True)
```
C'est plus lisible et protège des injections SQL.

**Système de templates**
Les templates sont des fichiers HTML avec des variables Python. Django injecte les données dans le HTML avant de l'envoyer au navigateur.

**Système d'authentification**
Django intègre nativement : comptes utilisateurs, mots de passe sécurisés (hachage bcrypt), sessions, permissions.

**Interface d'administration**
Django génère automatiquement une interface d'administration complète à partir des modèles de données.

**Migrations**
Gestion automatique de l'évolution de la structure de la base de données.

**Middleware**
Filtres qui s'appliquent à toutes les requêtes. Dans ce projet : vérification que l'utilisateur est connecté avant d'accéder à n'importe quelle page.

### Pourquoi Django plutôt que Flask, FastAPI, ou autre ?
- **Django inclut tout** : authentification, ORM, admin, migrations, formulaires — tout est intégré. Flask nécessiterait d'assembler des dizaines de bibliothèques séparées.
- **Batterie incluses** : Django suit le principe « batteries included » — tout ce dont on a besoin est déjà là.
- **Sécurité** : Django protège par défaut contre les attaques CSRF, XSS, injections SQL.
- **Maturité** : Django est en production depuis 2005 (Instagram, Pinterest, et des milliers d'autres utilisent Django).

---

## Vision par ordinateur : OpenCV

### C'est quoi ?
OpenCV (Open Computer Vision) est la bibliothèque de vision par ordinateur la plus utilisée au monde. Elle permet à l'ordinateur de « voir » et d'analyser des images.

### Fonctions d'OpenCV utilisées dans ce projet

**cv2.CascadeClassifier** (Haar Cascade)
```python
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)
```
Détecte les visages dans une image.

**cv2.equalizeHist**
```python
equalized = cv2.equalizeHist(gray_image)
```
Normalise l'éclairage d'une image.

**cv2.face.LBPHFaceRecognizer**
```python
recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8)
recognizer.train(faces, labels)
label, distance = recognizer.predict(test_face)
```
L'algorithme de reconnaissance faciale LBPH.

**cv2.Laplacian**
```python
score = cv2.Laplacian(face, cv2.CV_64F).var()
```
Mesure la netteté d'une image.

### Pourquoi OpenCV ?
- **Gratuit et open source** : Pas de coût de licence
- **LBPH intégré** : cv2.face.LBPHFaceRecognizer est directement disponible
- **Performant** : OpenCV est optimisé en C++ → très rapide même sur Python
- **Pas besoin de GPU** : Tourne sur n'importe quel ordinateur
- **Pas d'internet requis** : Fonctionne hors ligne

### Pourquoi LBPH plutôt que Deep Learning (réseaux de neurones) ?
| Critère | LBPH | Deep Learning |
|---------|------|---------------|
| Précision | Bonne (suffisante pour ce projet) | Très haute |
| Matériel requis | CPU standard | GPU puissant (souvent) |
| Données nécessaires | 5-15 photos/personne | Des milliers de photos |
| Complexité | Faible | Très haute |
| Interprétabilité | Compréhensible (histogrammes) | Boîte noire |
| Coût | Gratuit | Parfois payant (cloud) |

Pour un projet académique avec peu de données par élève et un matériel standard, LBPH est le choix rationnel.

---

## Base de données : SQLite

### C'est quoi ?
SQLite est un moteur de base de données stocké dans un seul fichier. Il ne nécessite pas de serveur séparé.

### Le fichier de base de données : db.sqlite3
Tout le contenu de la base de données (tous les élèves, toutes les présences, toutes les configurations) est dans un seul fichier `db.sqlite3`. Pour sauvegarder la base de données, il suffit de copier ce fichier.

### Pourquoi SQLite ?
- **Zéro configuration** : Pas de serveur à installer et maintenir
- **Portabilité** : Le fichier peut être déplacé sur n'importe quelle machine
- **Fiabilité** : SQLite est utilisé par des milliards d'appareils (Android, iOS, Firefox...)
- **Suffisant** : Pour quelques centaines à quelques milliers d'élèves et un nombre limité d'utilisateurs simultanés, SQLite est parfaitement adapté

### Limites de SQLite
- Pas conçu pour des milliers de connexions simultanées
- Pas de réplication native (sauvegarde manuelle nécessaire)

Si l'école grandit beaucoup, on pourrait migrer vers PostgreSQL — Django rend cette migration simple car le code Python ne change pas, seule la configuration `settings.py` change.

---

## Traitement d'images : Pillow (PIL)

### C'est quoi ?
Pillow est la bibliothèque Python de référence pour manipuler les images (ouvrir, redimensionner, convertir, sauvegarder...).

### Utilisation dans ce projet
- Ouvrir les photos d'entraînement dans différents formats (JPEG, PNG...)
- Convertir les images en format numpy pour OpenCV
- Sauvegarder les visages rognés des inconnus

---

## Calcul scientifique : NumPy

### C'est quoi ?
NumPy est la bibliothèque de calcul numérique de Python. Elle permet de manipuler des tableaux de nombres (matrices, vecteurs) très efficacement.

### Utilisation dans ce projet
- Les images sont représentées comme des tableaux NumPy (tableau de pixels)
- Les histogrammes LBPH sont des tableaux NumPy
- OpenCV et NumPy travaillent ensemble en permanence

---

## Interface web : HTML, CSS, JavaScript pur

### Pas de framework JavaScript
L'interface utilise du **JavaScript pur** (sans React, Vue, Angular...). Pourquoi ?
- Moins de dépendances à maintenir
- Chargement plus rapide
- Suffisant pour les besoins de l'application

### La webcam en JavaScript
```javascript
// Demande l'accès à la caméra du navigateur
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => { videoElement.srcObject = stream; })

// Toutes les X secondes, capture une image et l'envoie au serveur
setInterval(() => {
    canvas.drawImage(videoElement, 0, 0);
    const imageBase64 = canvas.toDataURL('image/jpeg', 0.8);
    fetch('/facial/api/recognize-frame/', {
        method: 'POST',
        body: JSON.stringify({ image: imageBase64 })
    })
    .then(response => response.json())
    .then(data => drawBoxes(data.results));
}, intervalMs);
```

### Le CSS personnalisé
L'interface utilise un CSS écrit entièrement à la main (fichier `static/css/app.css`). Pas de Bootstrap ou Tailwind. Cela donne un design unique et précis, sans dépendance externe.

---

## Sécurité : Sessions Django + Middleware personnalisé

### Authentification
Django gère les sessions utilisateurs. Quand un utilisateur se connecte :
1. Un cookie de session est créé dans le navigateur
2. Le serveur associe ce cookie à l'utilisateur connecté
3. Chaque requête vérifie ce cookie

### Middleware de protection
```python
class LoginRequiredMiddleware:
    EXEMPT_PREFIXES = (
        "/facial/login/",    # Page de connexion elle-même
        "/facial/logout/",   # Déconnexion
        "/facial/admin/",    # Django admin (a sa propre auth)
        "/facial/api/",      # API (utilisée par la caméra sans session)
    )
    def __call__(self, request):
        if not request.user.is_authenticated:
            if not any(request.path.startswith(p) for p in self.EXEMPT_PREFIXES):
                return redirect(f"/facial/login/?next={request.path}")
        return self.get_response(request)
```

Ce middleware intercepte CHAQUE requête et vérifie que l'utilisateur est connecté. Si non, redirection vers la page de login.

### Protection CSRF
Django intègre une protection contre les attaques CSRF (Cross-Site Request Forgery). Chaque formulaire contient un jeton secret unique. Si le jeton manque ou est invalide → la requête est rejetée.

---

## Déploiement : Replit

### C'est quoi Replit ?
Replit est une plateforme de développement et d'hébergement en ligne. Le projet est hébergé sur Replit, ce qui signifie qu'il est accessible depuis n'importe quel navigateur sans installation locale.

### Configuration pour Replit
- **PORT** : variable d'environnement fournie par Replit pour le port du serveur
- **SESSION_SECRET** : clé secrète Django stockée en variable d'environnement sécurisée
- **CSRF_TRUSTED_ORIGINS** : liste des domaines Replit autorisés pour les formulaires
- **ALLOWED_HOSTS = ["*"]** : accepte les connexions de toutes les origines (environnement de développement)

---

## Résumé des versions et dépendances

```
django >= 5.0             ← Framework web principal
opencv-contrib-python     ← Vision par ordinateur + LBPH
Pillow                    ← Manipulation d'images
numpy                     ← Calcul numérique (implicitement requis par OpenCV)
```

Ces dépendances sont listées dans le fichier `requirements.txt` et sont installées automatiquement au démarrage via `start.sh`.

---

*Continuez avec `06_WORKFLOW_UTILISATION.md` pour voir comment utiliser l'application au quotidien.*
