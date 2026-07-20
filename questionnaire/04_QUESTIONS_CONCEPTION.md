# Questions sur la Conception et les Choix Techniques — Questionnaire Jury

---

## Q1 : Pourquoi avoir choisi Django comme framework et pas un autre ?

**Réponse :**
Django a été choisi pour plusieurs raisons solides :

**1. « Batteries incluses »** : Django intègre nativement tout ce dont on a besoin : système d'authentification, ORM (accès base de données), templates HTML, formulaires avec validation, interface d'administration, migrations, protection CSRF. D'autres frameworks comme Flask nécessiteraient d'assembler 10-15 bibliothèques séparées.

**2. Adapté au modèle de notre application** : Notre application est principalement une application de gestion de données (CRUD : Créer, Lire, Modifier, Supprimer). Django est précisément conçu pour ce type d'application.

**3. Sécurité par défaut** : Django protège automatiquement contre les attaques les plus courantes (injections SQL via l'ORM, CSRF via les tokens, XSS via l'échappement automatique des templates).

**4. Popularité et maturité** : Django existe depuis 2005, est utilisé par Instagram, Pinterest, Mozilla, et des milliers d'autres projets. La documentation est excellente.

**5. Python** : Django est en Python, qui est le langage standard pour la vision par ordinateur (OpenCV, NumPy, Pillow). Tout le projet est dans un seul langage.

---

## Q2 : Comment avez-vous conçu l'architecture de votre application ? Quels patterns avez-vous utilisés ?

**Réponse :**
Notre application suit le pattern **MVT (Model-View-Template)**, qui est la variante Django du pattern MVC (Model-View-Controller) :

**M — Model (Modèle)** : Les classes Python dans `models.py`. Elles définissent la structure des données et contiennent la logique métier (calcul du taux de présence, vérification des contraintes horaires...).

**V — View (Vue)** : Les fonctions dans `views.py`. Elles reçoivent les requêtes HTTP, interrogent les modèles, et retournent une réponse (page HTML ou JSON).

**T — Template** : Les fichiers HTML dans `templates/`. Ils définissent l'affichage final et utilisent les données fournies par les vues.

**Couche Services** : Pour la logique complexe (reconnaissance faciale, entraînement IA, présence journalière), nous avons créé des services séparés dans `apps/attendance/services/`. Cela évite que `views.py` ne devienne trop volumineux.

**Pourquoi cette séparation ?** Le principe de **séparation des responsabilités** (Separation of Concerns) : chaque fichier a une responsabilité claire. Un développeur qui cherche où est gérée la reconnaissance faciale sait qu'il doit aller dans `services/recognition.py`.

---

## Q3 : Comment gérez-vous les erreurs et les cas limites dans votre système ?

**Réponse :**
Notre système gère les erreurs à plusieurs niveaux :

**1. Validation des formulaires (forms.py)**
Chaque formulaire Django valide les données avant de les sauvegarder. Par exemple :
- Le matricule est-il unique ?
- L'heure de début est-elle avant l'heure de fin ?
- Y a-t-il un chevauchement d'horaire pour cette classe, ce professeur, cette salle ?

**2. La file de revue (incertitude)**
Quand la reconnaissance est incertaine (score entre les deux seuils), on ne prend pas de décision automatique — on crée un ticket pour révision humaine.

**3. Vérification avant enregistrement**
Avant d'enregistrer une présence, on vérifie si elle n'existe pas déjà (anti-doublon) et si l'élève est bien de la bonne classe (filtre par classe activable).

**4. Le cooldown anti-doublon**
Un élève détecté plusieurs fois en moins de 5 minutes dans la même session ne génère qu'un seul enregistrement.

**5. Gestion des modèles non entraînés**
Si le modèle IA n'existe pas encore, la page d'accueil affiche un avertissement et toutes les fonctions de reconnaissance retournent une erreur explicite.

**6. Photos floues**
Les photos trop floues (score Laplacian < 50) sont ignorées pendant l'entraînement avec un compteur `skipped_blurry`.

---

## Q4 : Comment avez-vous structuré votre code pour qu'il soit maintenable ?

**Réponse :**
Plusieurs principes de maintenabilité ont guidé notre développement :

**1. Séparation des responsabilités**
- `models.py` : données et logique métier
- `views.py` : traitement des requêtes HTTP
- `services/` : logique complexe (IA, présences)
- `forms.py` : validation des données entrantes

**2. Constants nommées**
```python
# Mauvais : if status == "present"  ← chaîne magique, si on fait une faute de frappe...
# Bon :
class AttendanceRecord(models.Model):
    STATUS_PRESENT = "present"
    STATUS_LATE = "late"
    STATUS_ABSENT = "absent"
    # On utilise : if status == AttendanceRecord.STATUS_PRESENT
```

**3. Méthodes sur les modèles**
La logique métier est dans les modèles :
```python
student.attendance_rate()    # Calcul du taux de présence
session.generate_absents()   # Génération des absences
config = SystemConfig.get()  # Accès singleton
```

**4. Journalisation systématique**
Toutes les actions importantes sont journalisées via `_syslog()`. En cas de bug, on peut retrouver ce qui s'est passé.

**5. Commentaires et docstrings**
Les classes et méthodes importantes sont documentées avec des docstrings Python.

---

## Q5 : Comment gérez-vous la sécurité dans votre application ?

**Réponse :**
La sécurité est assurée à plusieurs niveaux :

**Authentification :**
- Middleware qui force la connexion sur toutes les pages sauf login/logout
- Sessions Django sécurisées (cookies HTTPOnly, Secure, SameSite)
- Mots de passe hachés avec PBKDF2+SHA256 (jamais en clair)

**Autorisation (qui peut faire quoi) :**
- Trois rôles : Admin, Enseignant, Secrétariat
- Les vues vérifient le rôle avant d'autoriser les actions sensibles (entraîner l'IA, gérer les utilisateurs)

**Protection CSRF :**
- Chaque formulaire contient un token unique → les attaques cross-site sont bloquées

**Secrets non exposés :**
- La `SECRET_KEY` Django est dans une variable d'environnement (`SESSION_SECRET`), pas dans le code

**Traçabilité :**
- `SystemLog` : toutes les actions importantes
- `AttendanceAuditLog` : toutes les modifications de présences

**Données personnelles :**
- Les photos sont accessibles uniquement après authentification
- Le modèle IA (trainer.yml) ne contient pas de photos, seulement des nombres

---

## Q6 : Qu'est-ce qu'un middleware ? Comment l'utilisez-vous ?

**Réponse :**
Un middleware est un composant qui s'intercale entre la requête HTTP et la vue Django. Il s'exécute pour CHAQUE requête, avant et/ou après le traitement de la vue.

**Analogie :** C'est comme un gardien à l'entrée d'un immeuble. Chaque personne doit passer devant lui. Il vérifie si elle a le droit d'entrer.

**Notre middleware `LoginRequiredMiddleware` :**
```python
class LoginRequiredMiddleware:
    EXEMPT_PREFIXES = ("/facial/login/", "/facial/api/", ...)
    
    def __call__(self, request):
        if not request.user.is_authenticated:
            if not any(request.path.startswith(p) for p in self.EXEMPT_PREFIXES):
                return redirect(f"/facial/login/?next={request.path}")
        return self.get_response(request)  # Laisse passer
```

**Ce qu'il fait :**
1. Vérifie si l'utilisateur est connecté
2. Si non et si la page n'est pas exemptée (login, api...) → redirige vers la page de connexion
3. Si oui → laisse la requête continuer normalement

**Avantage :** Une seule règle définie une fois qui s'applique à toutes les pages. Sans ce middleware, chaque vue devrait vérifier manuellement si l'utilisateur est connecté.

---

## Q7 : Votre application est-elle scalable ? Peut-elle gérer une très grande université ?

**Réponse :**
Dans son état actuel, l'application a des limites de scalabilité :

**Limites actuelles :**
1. **SQLite** : Performant jusqu'à ~100 connexions simultanées. Pour de très grandes universités avec des centaines d'agents actifs simultanément, il faudrait migrer vers PostgreSQL.

2. **Serveur synchrone Django** : Le serveur Django standard traite les requêtes de façon synchrone. Pour gérer de nombreuses caméras en temps réel simultanément, il faudrait des workers asynchrones (Django Channels, Celery).

3. **Reconnaissance faciale single-thread** : L'algorithme LBPH tourne sur un seul thread CPU. Pour analyser des dizaines de caméras simultanément, il faudrait paralléliser avec multiprocessing.

**Évolutions possibles pour scaler :**
- Migrer SQLite → PostgreSQL (changement de 3 lignes dans settings.py)
- Ajouter Redis + Celery pour les tâches en arrière-plan
- Utiliser Django Channels pour le WebSocket temps réel
- Passer à Deep Learning pour une meilleure précision à grande échelle

**Pour l'usage actuel (école de quelques centaines à quelques milliers d'élèves) :** L'application est parfaitement adaptée dans son état actuel.

---

## Q8 : Comment avez-vous testé votre application ?

**Réponse :**
*(Adaptez selon votre expérience réelle de test)*

Le projet a été testé de plusieurs façons :

**Tests fonctionnels manuels :**
- Ajout d'élèves avec différents cas (matricule en double, champs obligatoires manquants)
- Upload de photos et vérification de la détection de visage
- Entraînement du modèle et vérification du rapport
- Test de reconnaissance avec différentes photos et conditions d'éclairage
- Test de la webcam en direct
- Test de la génération des rapports et de l'export CSV

**Tests des cas limites :**
- Photo sans visage → rejetée correctement
- Photo floue → ignorée par l'entraînement
- Double présence → doublon évité
- Accès sans connexion → redirection vers login
- Chevauchement d'horaire → erreur affichée

**Ce qui serait à améliorer :**
Des tests automatisés avec `django.test.TestCase` seraient une amélioration importante pour la maintenabilité à long terme.

---

## Q9 : Quelles seraient les améliorations futures de votre projet ?

**Réponse :**
Plusieurs améliorations seraient envisageables :

**Court terme :**
- Application mobile (Android) pour la reconnaissance avec le téléphone du professeur
- Notifications automatiques aux parents par SMS ou email quand un élève est absent
- Intégration d'un calendrier scolaire partagé (jours fériés nationaux pré-chargés)

**Moyen terme :**
- Migration vers un algorithme Deep Learning (FaceNet ou ArcFace) pour une meilleure précision
- Tableau de bord analytique avancé (graphiques, tendances, comparaisons entre classes)
- Synchronisation en temps réel entre plusieurs PC (WebSocket)
- API REST pour intégration avec d'autres systèmes scolaires existants

**Long terme :**
- Support multi-établissements (un serveur central pour plusieurs écoles)
- Machine Learning pour détecter les patterns d'absentéisme et prévenir les décrochages
- Migration vers PostgreSQL + déploiement cloud robuste
- Mode hors ligne complet avec synchronisation différée

---

## Q10 : Comment avez-vous géré la contrainte de performance en temps réel de la webcam ?

**Réponse :**
La reconnaissance en temps réel pose un défi de performance : si le serveur met 2 secondes à traiter chaque image, l'expérience utilisateur est mauvaise.

**Solutions implémentées :**

**1. Intervalles configurables**
Le JavaScript ne capture pas une image par milliseconde — il attend un délai configurable (par défaut quelques secondes) entre chaque capture. L'utilisateur peut ajuster ce délai dans les paramètres.

**2. Format JPEG compressé**
L'image est envoyée en JPEG avec compression (`canvas.toDataURL('image/jpeg', 0.8)`) plutôt qu'en PNG non compressé. L'image est plus petite → transfert plus rapide.

**3. Coordonnées en pourcentage**
Les bounding boxes (rectangles) sont retournés en pourcentages plutôt qu'en pixels. Le JavaScript peut alors les dessiner immédiatement sur n'importe quelle résolution d'écran sans calcul supplémentaire.

**4. LBPH sur visage rogné**
LBPH ne s'applique pas à l'image entière mais uniquement à la zone du visage détectée (quelques pixels × quelques pixels). C'est beaucoup plus rapide que d'analyser toute l'image.

**5. Vérification anti-doublon en mémoire**
Avant de créer un enregistrement en base de données, une vérification rapide en mémoire évite les requêtes SQL inutiles pour les doublons.

---

*Voir aussi : `05_QUESTIONS_ETHIQUE_JURIDIQUE.md` pour les questions sur l'éthique et le droit.*
