# Questions sur la Base de Données — Questionnaire Jury

---

## Q1 : Quelle base de données utilisez-vous et pourquoi ?

**Réponse :**
Nous utilisons **SQLite**, une base de données qui stocke toutes les données dans un seul fichier (`db.sqlite3`). 

**Pourquoi SQLite ?**
- **Simplicité** : Pas de serveur séparé à installer, configurer, et maintenir
- **Portabilité** : Le fichier peut être copié et déplacé facilement (pour sauvegarde ou migration)
- **Suffisant** : Pour une école avec quelques centaines à quelques milliers d'élèves et quelques utilisateurs simultanés, SQLite est parfaitement adapté
- **Fiabilité** : SQLite est utilisé dans des milliards d'appareils (Android, iOS, Firefox, Chrome...) — c'est l'un des logiciels les plus testés au monde

**Limite principale :** SQLite n'est pas conçu pour des milliers d'utilisateurs simultanés. Pour une très grande université avec des dizaines de secrétaires travaillant en même temps, il faudrait migrer vers PostgreSQL.

---

## Q2 : Qu'est-ce qu'un modèle de données ? Expliquez les modèles principaux.

**Réponse :**
Un modèle de données définit la **structure** d'une table dans la base de données : quelles colonnes elle contient, quels types de données, et quelles relations avec d'autres tables.

Dans Django, les modèles sont écrits en Python et Django les traduit automatiquement en tables SQL.

**Les modèles principaux de notre projet :**

**Student (Élève)** : Contient toutes les informations sur chaque élève : nom complet, matricule (unique), classe, date de naissance, statut (actif/suspendu/diplômé...). C'est la table centrale du système.

**TrainingPhoto (Photo d'entraînement)** : Chaque photo soumise pour entraîner l'IA. Contient le lien vers l'élève, le fichier image, et la date d'entraînement (vide = pas encore entraîné).

**AttendanceRecord (Présence cours)** : Chaque présence enregistrée à une session de cours. Contient l'élève, la session, l'heure de détection, le score de confiance, et le statut (présent/retard/absent).

**DailyAttendance (Présence journalière)** : Pour les écoles secondaires, un enregistrement par élève par jour avec l'heure d'arrivée.

**SystemConfig** : Une seule ligne contenant tous les paramètres configurables du système (seuils de confiance, tolérance de retard, etc.).

---

## Q3 : Qu'est-ce qu'une clé étrangère (Foreign Key) ? Donnez un exemple.

**Réponse :**
Une clé étrangère est un lien entre deux tables. Elle dit : « cette colonne fait référence à un enregistrement dans une autre table ».

**Exemple dans notre projet :**
La table `AttendanceRecord` contient une colonne `student` qui est une clé étrangère vers la table `Student`. Ça veut dire : « Chaque enregistrement de présence appartient à un élève spécifique ».

```python
class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # Traduit en SQL : student_id INTEGER REFERENCES attendance_student(id)
```

**Le paramètre `on_delete=models.CASCADE`** signifie : « Si l'élève est supprimé, supprimer aussi tous ses enregistrements de présence ». C'est la règle de cascade.

D'autres comportements possibles :
- `SET_NULL` : Si l'objet référencé est supprimé, mettre la colonne à NULL (garder l'enregistrement)
- `PROTECT` : Interdire la suppression si des enregistrements liés existent

---

## Q4 : Qu'est-ce qu'une migration ? Pourquoi est-ce important ?

**Réponse :**
Une migration est un **fichier qui décrit un changement dans la structure de la base de données** : ajouter une table, ajouter une colonne, supprimer une colonne, modifier un type...

**Pourquoi c'est important ?**
Imaginez une application en production depuis 6 mois. La base de données contient déjà des milliers d'enregistrements. Si on veut ajouter une nouvelle colonne, on ne peut pas simplement recréer la base de données (on perdrait toutes les données). La migration permet de modifier la structure sans perdre les données.

**Dans notre projet :**
Il y a 13 migrations (de `0001_initial.py` à `0013_...`). Chacune correspond à une évolution du projet :
- `0001` : Création initiale des tables (Student, TrainingPhoto, Camera...)
- `0002` : Ajout du champ `date_of_birth`, de la table `Course`, de `UnknownFaceLog`
- `0005` : Ajout du journal d'audit, des jours fériés, des salles
- `0009` : Ajout de la file de revue et des niveaux de confiance
- ...etc

**Commande pour appliquer les migrations :**
```bash
python manage.py migrate
```
Django vérifie quelles migrations ont déjà été appliquées (grâce à une table interne `django_migrations`) et n'applique que les nouvelles.

---

## Q5 : Qu'est-ce qu'une contrainte d'unicité ? Donnez des exemples.

**Réponse :**
Une contrainte d'unicité garantit qu'une valeur (ou combinaison de valeurs) ne peut apparaître qu'une seule fois dans la table. Si on essaie d'insérer un doublon, la base de données rejette l'insertion.

**Exemples dans notre projet :**

```python
# Le matricule est unique : deux élèves ne peuvent pas avoir le même matricule
student_code = models.CharField(unique=True)

# Un élève ne peut être inscrit qu'une fois à un cours
class Enrollment(models.Model):
    class Meta:
        unique_together = [("student", "course")]

# Un élève ne peut avoir qu'un seul enregistrement de présence par jour
class DailyAttendance(models.Model):
    class Meta:
        unique_together = [("student", "date")]
```

**Pourquoi c'est important ?** Sans ces contraintes, on pourrait créer deux élèves avec le même matricule (confusion), ou enregistrer deux fois la présence du même élève le même jour (doublon). Les contraintes garantissent l'intégrité des données.

---

## Q6 : Qu'est-ce qu'un index de base de données ? Pourquoi l'utilisez-vous ?

**Réponse :**
Un index est une structure de données supplémentaire qui accélère les recherches dans une table.

**Analogie :** Imaginez un dictionnaire. Pour trouver le mot « reconnaissance », vous ne lisez pas tout le dictionnaire depuis la première page. Vous utilisez l'index alphabétique pour aller directement à la bonne page. C'est exactement ce que fait un index de base de données.

**Exemple dans notre projet :**
```python
class Student(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["student_code"]),  # Recherche rapide par matricule
            models.Index(fields=["classe"]),         # Filtrage rapide par classe
            models.Index(fields=["is_active"]),      # Filtrage rapide par statut actif
        ]
```

**Sans index :** Pour trouver un élève par son matricule parmi 10 000 élèves, la base de données parcourt les 10 000 enregistrements un par un.

**Avec index :** La base de données saute directement au bon enregistrement en quelques millisecondes.

**Inconvénient :** Les index prennent de l'espace disque et ralentissent légèrement les insertions (l'index doit être mis à jour). On les crée donc sur les colonnes les plus souvent utilisées dans les recherches.

---

## Q7 : Qu'est-ce qu'un singleton en base de données ? Pourquoi l'utilisez-vous ?

**Réponse :**
Un singleton est une table qui ne contient toujours qu'un seul enregistrement. C'est utile pour les configurations globales du système.

**Exemple dans notre projet :**
```python
class SystemConfig(models.Model):
    seuil_confiance_haute = models.FloatField(default=58.0)
    retard_minutes = models.PositiveIntegerField(default=15)
    ...
    
    def save(self, *args, **kwargs):
        self.pk = 1  # Force toujours l'ID à 1 → un seul enregistrement possible
        super().save(*args, **kwargs)
    
    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)  # Crée si n'existe pas
        return obj
```

**Utilisation :**
```python
config = SystemConfig.get()
seuil = config.seuil_confiance_haute  # Toujours la configuration courante
```

**Pourquoi pas juste un fichier de configuration ?** Un singleton en base de données permet de modifier la configuration depuis l'interface web, et les changements sont effectifs immédiatement sans redémarrer le serveur.

---

## Q8 : Qu'est-ce qu'un snapshot dans votre base de données ?

**Réponse :**
Un snapshot (instantané) est une copie d'une valeur au moment où un enregistrement est créé.

**Le problème :** L'`AttendanceRecord` stocke une clé étrangère vers l'élève. Si l'élève change de nom (correction d'une faute), les anciens enregistrements de présence afficheraient automatiquement le nouveau nom — ce qui pourrait créer de la confusion dans les archives.

**La solution — le snapshot :**
```python
class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, ...)         # Lien actuel
    student_name_snapshot = models.CharField(...)     # Copie du nom au moment de l'enregistrement
    classroom_snapshot = models.CharField(...)        # Copie de la classe au moment de l'enregistrement
```

Quand une présence est créée, on copie immédiatement le nom et la classe de l'élève dans les champs snapshot. Même si l'élève change de nom ou de classe ensuite, l'archive de présence conserve les informations telles qu'elles étaient à ce moment.

---

## Q9 : Comment assurez-vous la traçabilité des modifications de présence ?

**Réponse :**
Toute modification manuelle d'une présence est tracée dans la table `AttendanceAuditLog`.

**Structure du journal d'audit :**
```python
class AttendanceAuditLog(models.Model):
    attendance_record  → la présence modifiée
    modifie_par        → qui a fait la modification (nom d'utilisateur)
    ancienne_valeur    → ancien statut (ex: "absent")
    nouvelle_valeur    → nouveau statut (ex: "excuse")
    raison             → justification de la modification
    date_modification  → horodatage exact
```

**Exemple :**
```
Le 15/11/2024 à 09:32, "secretariat_marie" a changé 
la présence de "Bahati Joseph" de "absent" → "excuse" 
Raison: "Certificat médical présenté"
```

Cette table est **immuable** : les utilisateurs peuvent créer des entrées mais pas les modifier ou les supprimer. Elle garantit l'intégrité des archives.

---

## Q10 : Qu'est-ce que l'ORM de Django ? Pourquoi ne pas écrire directement du SQL ?

**Réponse :**
**ORM** = Object-Relational Mapping = Mapping Objet-Relationnel.

C'est un système qui traduit les tables de la base de données en objets Python. Au lieu d'écrire :
```sql
SELECT * FROM attendance_student 
WHERE is_active = TRUE 
ORDER BY full_name;
```

On écrit :
```python
Student.objects.filter(is_active=True).order_by("full_name")
```

**Avantages :**
1. **Plus lisible** : Le code Python est plus clair que le SQL pour un développeur Python
2. **Portable** : Si on change de base de données (SQLite → PostgreSQL), le code Python ne change pas
3. **Protection** : L'ORM protège automatiquement contre les injections SQL
4. **Puissant** : Les relations entre tables sont gérées automatiquement

**Inconvénient :** Parfois moins performant que du SQL écrit à la main pour des requêtes très complexes.

---

*Voir aussi : `04_QUESTIONS_CONCEPTION.md` pour les questions sur les choix de conception.*
