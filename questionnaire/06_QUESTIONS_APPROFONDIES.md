# Questions Techniques Avancées — Pour un Jury Exigeant

---

## Q1 : Quelle est la complexité algorithmique de LBPH ? Est-il rapide ?

**Réponse :**
**Entraînement :**
- Pour N photos de P élèves, l'entraînement est O(N × pixels_par_visage)
- Avec augmentation (flip), c'est O(2N × pixels)
- Sur 100 élèves × 10 photos = 1000 photos, l'entraînement prend quelques secondes sur un CPU standard

**Reconnaissance :**
- Pour 1 visage inconnu, on calcule sa signature LBPH : O(pixels_du_visage)
- On compare avec les signatures de tous les élèves connus : O(P × longueur_histogramme)
- Avec P = 1000 élèves et histogramme de 16 384 valeurs → environ 16 millions d'opérations
- En pratique, moins d'une milliseconde sur un CPU moderne

**Comparaison avec Deep Learning :**
- FaceNet : encodage en 128 dimensions via réseau de neurones → plus lent à calculer mais signature plus compacte
- LBPH a une signature de 16 384 valeurs vs 128 pour FaceNet → LBPH fait plus de calculs à la comparaison, mais moins à l'encodage

---

## Q2 : Comment fonctionne exactement la distance chi-carré utilisée par LBPH ?

**Réponse :**
La distance chi-carré (χ²) est une mesure statistique de différence entre deux distributions (deux histogrammes).

**Formule :**
```
χ²(H1, H2) = Σ [ (H1[i] - H2[i])² / (H1[i] + H2[i]) ]
```

Où H1 et H2 sont les deux histogrammes à comparer, et i parcourt toutes les valeurs.

**Propriétés :**
- Si H1 = H2 (mêmes histogrammes exactement) → χ² = 0
- Plus les histogrammes diffèrent → plus χ² est grand
- C'est symétrique : χ²(H1, H2) = χ²(H2, H1)

**Pourquoi chi-carré et pas distance euclidienne ?**
La distance euclidienne traite toutes les barres de l'histogramme de la même façon. La distance chi-carré normalise par `(H1[i] + H2[i])`, ce qui donne plus d'importance aux différences dans les zones où les deux histogrammes ont de faibles valeurs — cela rend la comparaison plus robuste aux petites fluctuations dans les zones denses.

---

## Q3 : Qu'est-ce qu'une commande de gestion Django ? Expliquez `auto_daily`.

**Réponse :**
Une commande de gestion Django (`management command`) est un script Python exécutable depuis la ligne de commande via `python manage.py <nom_commande>`.

**Notre commande `auto_daily` :**
```bash
python manage.py auto_daily --generate-absents
python manage.py auto_daily --check-school-day
python manage.py auto_daily --date 2024-11-15
```

**Ce qu'elle fait :**
1. Vérifie si la date cible est un jour de classe (selon SchoolDayConfig)
2. Vérifie si c'est un jour férié (JourFerie)
3. Vérifie si l'heure de fin des cours est passée
4. Si tout est OK : crée un enregistrement DailyAttendance STATUS_ABSENT pour chaque élève actif sans présence ce jour
5. Journalise l'action dans SystemLog

**Automatisation via cron (planificateur Unix) :**
```bash
# Exécuter tous les jours du lundi au vendredi à 16h30
30 16 * * 1-5  cd /chemin/du/projet && python manage.py auto_daily --generate-absents
```

---

## Q4 : Expliquez la gestion des sessions et des cookies dans votre application.

**Réponse :**
**Le flux d'authentification :**
1. L'utilisateur soumet le formulaire de login (POST avec username + password)
2. Django vérifie les credentials contre la table `auth_user` (mot de passe hashé)
3. Si correct → Django crée une session : un enregistrement en base de données dans `django_session` avec un ID aléatoire
4. Django envoie un cookie `sessionid` au navigateur contenant cet ID
5. Pour chaque requête suivante, le navigateur envoie automatiquement le cookie
6. Django retrouve la session grâce à l'ID → identifie l'utilisateur

**Configuration spéciale pour Replit (iframe) :**
Notre application tourne dans un iframe Replit. Les cookies inter-domaines ont des restrictions modernes. D'où :
```python
SESSION_COOKIE_SAMESITE = "None"   # Autoriser les cookies dans les iframes
SESSION_COOKIE_SECURE = True       # Cookies uniquement via HTTPS
CSRF_COOKIE_SAMESITE = "None"      # Même chose pour CSRF
```

**Déconnexion :**
`python manage.py logout` → supprime la session de la base de données → le cookie devient invalide.

---

## Q5 : Comment fonctionne le système de migration Django en détail ?

**Réponse :**
**Processus de migration :**

1. **Création de la migration :**
```bash
python manage.py makemigrations
```
Django compare le modèle actuel (`models.py`) avec la dernière migration existante et génère un fichier Python décrivant les différences.

2. **Structure d'une migration :**
```python
class Migration(migrations.Migration):
    dependencies = [("attendance", "0012_alter_systemconfig_...")]
    
    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="filtrer_par_classe",
            field=models.BooleanField(default=True),
        ),
    ]
```

3. **Application de la migration :**
```bash
python manage.py migrate
```
Django parcourt la table `django_migrations` pour savoir quelles migrations ont déjà été appliquées. Il exécute les nouvelles migrations dans l'ordre des dépendances.

4. **Suivi dans la base de données :**
La table `django_migrations` stocke le nom de chaque migration appliquée. Django ne l'applique jamais deux fois.

5. **Rollback possible :**
```bash
python manage.py migrate attendance 0011  # Revenir à la migration 0011
```

---

## Q6 : Qu'est-ce qu'un context_processor ? Utilisez-vous cela ?

**Réponse :**
Un context processor est une fonction Python qui ajoute automatiquement des variables à TOUS les templates de l'application, sans avoir à les passer explicitement depuis chaque vue.

**Exemple standard Django (déjà configuré) :**
```python
"context_processors": [
    "django.template.context_processors.request",   # Ajoute "request" à tous les templates
    "django.contrib.auth.context_processors.auth",  # Ajoute "user" à tous les templates
    "django.contrib.messages.context_processors.messages",  # Ajoute "messages" (notifications flash)
]
```

Grâce au context processor d'auth, dans n'importe quel template on peut écrire :
```html
{% if user.is_authenticated %}
    Bonjour, {{ user.username }} !
{% endif %}
```

**Dans notre projet :** Le fichier `context_processors.py` contient potentiellement des variables globales supplémentaires (ex: le profil de l'utilisateur courant, le nombre de tickets de revue en attente) automatiquement disponibles dans tous les templates.

---

## Q7 : Comment votre API JSON de reconnaissance est-elle structurée ? Expliquez le contrat.

**Réponse :**
L'endpoint `POST /facial/api/recognize-frame/` suit un contrat JSON strict :

**Requête (ce que le navigateur envoie) :**
```json
{
    "image": "data:image/jpeg;base64,/9j/4AAQ...",  // Image encodée en base64
    "session_id": "42",                               // ID de la session de cours (optionnel)
    "camera_id": "3"                                  // ID de la caméra (optionnel)
}
```

**Réponse (ce que le serveur retourne) :**
```json
{
    "results": [
        {
            "status": "recognized",           // "recognized" | "unknown"
            "name": "Bahati Joseph",           // Nom de l'élève (ou "Inconnu")
            "student_code": "UNI-001",         // Matricule
            "classroom": "L3 Info",            // Classe
            "confidence": 87.3,               // Score 0-100 (100 = parfait)
            "already_marked": false,           // Déjà présent aujourd'hui ?
            "bbox": [15.2, 10.5, 22.1, 29.3]  // [x%, y%, w%, h%] en pourcentages
        }
    ],
    "saved": 1,     // Nombre de présences enregistrées
    "error": null   // Message d'erreur éventuel
}
```

**Les coordonnées bbox en pourcentages :**
Plutôt que des pixels absolus (qui changeraient selon la résolution d'écran), on utilise des pourcentages de la largeur/hauteur de l'image. Le JavaScript peut alors dessiner les rectangles sur n'importe quelle taille d'affichage.

---

## Q8 : Qu'est-ce que le pattern Singleton ? Comment l'implémentez-vous pour SystemConfig ?

**Réponse :**
Le pattern Singleton est un design pattern qui garantit qu'une classe n'a qu'une seule instance.

**Notre implémentation en Django :**
```python
class SystemConfig(models.Model):
    # ... champs ...
    
    def save(self, *args, **kwargs):
        self.pk = 1       # Force l'ID à toujours être 1
        super().save(*args, **kwargs)  # Django utilise UPDATE si pk=1 existe, INSERT sinon
    
    @classmethod
    def get(cls) -> "SystemConfig":
        obj, created = cls.objects.get_or_create(pk=1)
        # get_or_create : récupère si existe, crée si n'existe pas
        return obj
```

**Comment ça fonctionne :**
- `self.pk = 1` dans `save()` : quelle que soit la façon dont on crée l'objet, il sera toujours l'enregistrement avec l'ID 1
- Si l'enregistrement ID=1 existe déjà → UPDATE (modification)
- Si l'enregistrement ID=1 n'existe pas → INSERT (création)
- Résultat : il ne peut jamais y avoir deux enregistrements

**Utilisation :**
```python
config = SystemConfig.get()  # Toujours le même objet unique
config.seuil_confiance_haute = 55.0
config.save()
```

---

## Q9 : Comment la validation des horaires empêche-t-elle les chevauchements ?

**Réponse :**
La méthode `clean()` de notre modèle `Schedule` vérifie trois types de chevauchements :

**Chevauchement pour la même classe :**
```python
overlapping = Schedule.objects.filter(
    classe=self.classe,
    jour_semaine=self.jour_semaine,
    is_active=True,
).exclude(pk=self.pk)  # Exclure l'horaire en cours de modification

for s in overlapping:
    # Deux intervalles [A, B] et [C, D] se chevauchent si A < D ET C < B
    if self.heure_debut < s.heure_fin and s.heure_debut < self.heure_fin:
        raise ValidationError("Chevauchement détecté !")
```

**Condition de chevauchement :**
Deux intervalles [début1, fin1] et [début2, fin2] se chevauchent si et seulement si `début1 < fin2 ET début2 < fin1`. C'est la formule mathématique standard de détection d'intersection de segments temporels.

**Trois vérifications :**
1. Même classe + même jour → un professeur ne peut pas donner deux cours en même temps à la même classe
2. Même professeur + même jour → un professeur ne peut pas être dans deux endroits à la fois
3. Même salle + même jour → une salle ne peut pas accueillir deux cours en même temps

---

## Q10 : Votre application utilise-t-elle des index de base de données ? Pourquoi ceux-là spécifiquement ?

**Réponse :**
Oui, nous avons défini des index stratégiques sur les colonnes les plus souvent utilisées dans les filtres et recherches.

**Indices sur `Student` :**
```python
indexes = [
    models.Index(fields=["student_code"]),  # Recherche par matricule (très fréquente)
    models.Index(fields=["classe"]),         # Filtrage par classe (fréquent)
    models.Index(fields=["is_active"]),      # Filtrage actifs/inactifs (toujours appliqué)
    models.Index(fields=["statut"]),         # Filtrage par statut
]
```

**Indices sur `AttendanceRecord` :**
```python
indexes = [
    models.Index(fields=["student"]),            # "Toutes les présences de cet élève"
    models.Index(fields=["course_session"]),      # "Toutes les présences de cette session"
    models.Index(fields=["status"]),              # "Tous les absents/présents"
    models.Index(fields=["recognized_at"]),       # "Présences de cette période"
]
```

**Indices sur `DailyAttendance` :**
```python
indexes = [
    models.Index(fields=["date"]),               # "Présences de ce jour" (requête la plus fréquente)
    models.Index(fields=["student", "date"]),     # "Présence de cet élève ce jour" (vérification doublon)
    models.Index(fields=["status"]),              # "Tous les absents de la semaine"
]
```

**Pourquoi ces champs et pas d'autres ?** Les index sont créés sur les colonnes qui apparaissent dans les clauses `WHERE` et `ORDER BY` des requêtes les plus fréquentes. Par exemple, la requête "tous les élèves présents aujourd'hui" (`WHERE date = ? AND status = ?`) bénéficie des index sur `date` et `status`.

---

*Ce questionnaire couvre l'ensemble des aspects du projet. Pour toute question non couverte ici, référez-vous aux fichiers de documentation dans le dossier `documentation/`.*
