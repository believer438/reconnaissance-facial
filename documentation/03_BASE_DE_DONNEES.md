# La Base de Données — Comment les données sont stockées

## Qu'est-ce qu'une base de données ?

Une base de données, c'est un système de classement ultra-organisé pour stocker et retrouver des informations. Imaginez une armoire à tiroirs géante :
- Chaque tiroir est une **table** (ex: la table des élèves, la table des cours)
- Chaque tiroir contient des fiches → ce sont les **enregistrements** (ex: fiche de Jean Dupont)
- Chaque fiche a des rubriques → ce sont les **colonnes** (ex: Nom, Matricule, Date de naissance)

---

## Quelle base de données est utilisée ?

Le projet utilise **SQLite**. C'est une base de données stockée dans un seul fichier : `db.sqlite3`.

**Avantages de SQLite :**
- Un seul fichier → facile à sauvegarder et transporter
- Pas de serveur séparé → s'installe et fonctionne immédiatement
- Gratuit et open source
- Largement utilisé (des milliards d'appareils l'utilisent, dont les iPhones)

**Inconvénients :**
- Pas conçu pour des milliers d'utilisateurs simultanés (mais parfait pour une école)
- Pas de réplication ou de haute disponibilité

---

## Django et les migrations — Comment la base de données évolue

En programmation, quand on veut changer la structure de la base de données (ajouter une colonne, créer une table), on ne le fait pas directement. On crée une **migration**.

Une migration est comme un journal de bord :
```
Migration 0001 : Créer les tables Student, TrainingPhoto, Camera...
Migration 0002 : Ajouter les colonnes date_of_birth, Course, UnknownFaceLog...
Migration 0003 : Ajouter camera_type, face_detected...
...
Migration 0013 : Désactiver l'interface checkout
```

Django applique ces migrations dans l'ordre pour s'assurer que la base de données est toujours à jour. On peut voir toutes les migrations dans le dossier `apps/attendance/migrations/`.

---

## Les tables (entités) principales

### 1. Student (Élève)

C'est la table centrale. Elle stocke toutes les informations sur chaque élève.

| Colonne | Ce que c'est | Exemple |
|---------|--------------|---------|
| full_name | Nom complet (unique) | « Bahati Joseph » |
| nom | Nom de famille | « Bahati » |
| post_nom | Post-nom | « Kalinda » |
| prenom | Prénom | « Joseph » |
| student_code | Matricule (unique) | « UNI-2024-001 » |
| classe | Lien vers sa classe | (voir Classe) |
| faculty | Faculté | « info » (Informatique) |
| date_of_birth | Date de naissance | 2001-05-14 |
| email | Adresse email | bahati@ecole.cd |
| phone | Numéro de téléphone | +243 XXX XXX |
| statut | État actuel | « actif », « suspendu », « diplômé »... |
| is_active | Actif ou non | Oui/Non |
| photo_profil | Photo officielle | (image) |

**Point important** : Quand `statut` change (ex: l'élève est exclu), `is_active` est automatiquement mis à jour. Un élève inactif n'apparaît plus dans les listes de présence.

---

### 2. Classe

| Colonne | Ce que c'est | Exemple |
|---------|--------------|---------|
| nom | Nom de la classe | « L3 Informatique » |
| niveau | Niveau académique | « L3 », « M1 », « G2 » |
| option | Spécialité | « Réseaux », « IA » |
| annee_academique | Année scolaire | « 2025-2026 » |
| is_active | Classe active ou non | Oui/Non |

Une classe peut avoir plusieurs élèves. Un élève appartient à une seule classe.

---

### 3. TrainingPhoto (Photo d'entraînement)

Chaque photo soumise pour entraîner l'IA est enregistrée ici.

| Colonne | Ce que c'est | Exemple |
|---------|--------------|---------|
| student | Lien vers l'élève | (vers Student) |
| image | Le fichier photo | students/photo_001.jpg |
| angle_tag | Angle de la photo | « face », « gauche », « droite » |
| trained_at | Date d'entraînement | 2024-03-15 10:30 (ou vide si pas encore entraîné) |
| face_detected | Un visage a été trouvé ? | Oui/Non |

**Comment savoir si un entraînement est nécessaire ?**
- Si `trained_at` est vide → cette photo n'est pas encore dans le modèle → réentraînement recommandé
- Si `face_detected = Non` → la photo ne contient pas de visage reconnaissable → à remplacer

---

### 4. FaceEmbedding (Empreinte faciale)

Pour chaque photo entraînée, le système stocke le vecteur mathématique du visage.

| Colonne | Ce que c'est |
|---------|--------------|
| student | L'élève concerné |
| photo | La photo source |
| vector | Les 256 nombres qui représentent le visage (stockés en binaire) |
| score_qualite | Score de netteté de la photo (Laplacian) |

---

### 5. Camera (Caméra)

| Colonne | Ce que c'est | Exemple |
|---------|--------------|---------|
| name | Nom de la caméra | « Caméra Entrée Principale » |
| location | Emplacement | « Couloir Bâtiment A » |
| camera_type | Type | « webcam », « usb », « rtsp » |
| source | Adresse de la caméra | Vide (webcam), « 0 » (USB), « rtsp://192.168.1.10/... » (IP) |
| zone_type | Rôle de la caméra | « check_in » (entrée école) ou « monitoring » (surveillance) |
| detection_mode | Mode actif | « recognition » (IA active), « monitoring_only » (vidéo sans IA), « off » |
| is_online | En ce moment : connectée ? | Oui/Non |
| fps_estimate | Images par seconde | 5.2 |
| frames_processed | Total d'images analysées | 14523 |

---

### 6. Course (Cours)

| Colonne | Ce que c'est | Exemple |
|---------|--------------|---------|
| code | Code du cours | « INFO401 » |
| name | Intitulé | « Bases de données avancées » |
| professor | Nom du professeur | « Prof. Mutombo » |
| faculty | Faculté | « info » |
| credits | Nombre de crédits | 3 |

---

### 7. Enrollment (Inscription)

Cette table fait le lien entre un élève et un cours. Elle dit « cet élève est inscrit à ce cours ».

| Colonne | Ce que c'est |
|---------|--------------|
| student | Lien vers l'élève |
| course | Lien vers le cours |
| enrolled_at | Date d'inscription |

**Contrainte** : Un élève ne peut être inscrit qu'une seule fois par cours (unicité de la paire student + course).

---

### 8. Schedule (Horaire)

Les horaires hebdomadaires de chaque cours pour chaque classe.

| Colonne | Ce que c'est | Exemple |
|---------|--------------|---------|
| classe | Quelle classe | L3 Info |
| course | Quel cours | INFO401 |
| salle | Quelle salle | Amphi B |
| jour_semaine | Quel jour | Lundi (0), Mardi (1)... |
| heure_debut | À quelle heure | 08:00 |
| heure_fin | Jusqu'à quand | 10:00 |
| tolerance_retard_minutes | Minutes de grâce | 15 |
| minutes_avant_cours | Fenêtre pré-cours | 10 (détection possible 10 min avant le cours) |

**Validation automatique** : Le système empêche les chevauchements d'horaires pour la même classe, le même professeur, ou la même salle. Si on essaie de créer un horaire qui entre en conflit, un message d'erreur s'affiche.

---

### 9. CourseSession (Séance de cours)

Une séance est une occurrence précise d'un cours (une date spécifique).

| Colonne | Ce que c'est | Exemple |
|---------|--------------|---------|
| course | Le cours | INFO401 |
| date | La date | 2024-11-15 |
| start_time | Heure de début | 08:00 |
| room | Salle | Amphi B |
| late_after_minutes | Retard après | 15 minutes |
| status | État de la séance | « en_attente », « ouvert », « ferme », « annule » |

---

### 10. AttendanceRecord (Enregistrement de présence)

Chaque présence enregistrée (automatiquement ou manuellement) crée un enregistrement ici.

| Colonne | Ce que c'est | Exemple |
|---------|--------------|---------|
| student | L'élève | Bahati Joseph |
| course_session | La séance | INFO401 - 15/11/2024 |
| recognized_at | Heure exacte | 08:07:32 |
| confidence_score | Score de confiance | 87.3 |
| status | Statut | « present », « late », « absent », « excuse » |
| source | Comment enregistré | « live » (caméra), « photo » (upload), « manuel » |

---

### 11. DailyAttendance (Présence journalière — École secondaire)

Pour le mode école secondaire (une seule présence par jour), cette table enregistre l'arrivée quotidienne de chaque élève.

| Colonne | Ce que c'est |
|---------|--------------|
| student | L'élève |
| date | La date |
| heure_entree | Heure d'arrivée enregistrée |
| status | « present », « retard », « absent », « excuse » |
| camera_entree | Quelle caméra a enregistré l'arrivée |

**Contrainte** : Un élève ne peut avoir qu'un seul enregistrement par jour (`unique_together = student + date`).

---

### 12. RecognitionReviewQueue (File de revue)

Tickets de validation manuelle pour les reconnaissances incertaines.

| Colonne | Ce que c'est |
|---------|--------------|
| student_proposed | Élève proposé par l'IA |
| confidence_proposed | Score de confiance de la proposition |
| distance_lbph | Distance brute LBPH (technique) |
| second_candidate | Deuxième candidat possible |
| technical_status | Raison du doute : « low_confidence » ou « multiple_match » |
| face_image | Photo du visage détecté |
| status | « pending » (à traiter), « validated », « rejected » |
| reviewed_by | Qui a validé/rejeté |

---

### 13. UnknownFaceLog (Visages inconnus)

Chaque visage non reconnu est sauvegardé ici avec sa photo.

---

### 14. AttendanceAuditLog (Journal d'audit des présences)

Chaque modification manuelle d'une présence est tracée ici : qui a modifié, l'ancienne valeur, la nouvelle valeur, et la raison.

---

### 15. SystemConfig (Configuration système)

Une seule ligne (singleton pk=1) qui stocke toutes les règles configurables du système.

| Paramètre | Valeur par défaut | Signification |
|-----------|-------------------|---------------|
| seuil_confiance_haute | 58.0 | En dessous : reconnaissance directe |
| seuil_distance_lbph | 75.0 | Entre 58 et 75 : file de revue. Au-delà : inconnu |
| retard_minutes | 15 | Minutes avant d'être marqué en retard |
| ouverture_avant_minutes | 10 | Minutes avant le cours où la détection est acceptée |
| filtrer_par_classe | True | N'accepter que les élèves de la classe en session |
| seuil_alerte_absences | 3 | Nombre d'absences déclenchant une alerte sur le tableau de bord |

---

### 16. SystemLog (Journal d'activité système)

Toutes les actions importantes laissent une trace ici : connexions, ajouts d'élèves, entraînements IA, exports...

| Colonne | Ce que c'est |
|---------|--------------|
| user | Qui a fait l'action |
| action | Quel type d'action (login, create, delete, train...) |
| object_type | Sur quoi (étudiant, caméra, cours...) |
| ip_address | Adresse IP de l'utilisateur |
| success | Action réussie ou non |

---

### 17. TrainingHistory (Historique d'entraînement)

Chaque session d'entraînement du modèle IA est enregistrée.

| Colonne | Ce que c'est |
|---------|--------------|
| triggered_by | Qui a déclenché l'entraînement |
| started_at / completed_at | Début et fin |
| nb_students | Nombre d'élèves traités |
| nb_photos | Photos utilisées |
| nb_skipped_blurry | Photos ignorées car trop floues |
| duration_seconds | Durée de l'entraînement |

---

### 18. UserProfile (Profil utilisateur)

Étend le compte utilisateur Django avec un rôle (Admin, Enseignant, Secrétariat).

---

## Schéma des relations

```
Classe ──────── Student ──────── TrainingPhoto ── FaceEmbedding
  │                │
  │                ├── Enrollment ─── Course ─── CourseSession
  │                │                                  │
  │                └── DailyAttendance           AttendanceRecord
  │                                                   │
Schedule ──────────────────────────────────────── Camera
```

**Légende des relations :**
- Une Classe a plusieurs Students
- Un Student a plusieurs TrainingPhotos et DailyAttendances
- Un Course peut avoir plusieurs Enrollments et CourseSession
- Un CourseSession produit plusieurs AttendanceRecords
- Une Camera est liée à plusieurs AttendanceRecords

---

## La notion de « snapshot » (instantané)

Vous remarquez des colonnes comme `student_name_snapshot` dans AttendanceRecord. Pourquoi ?

**Problème** : Si l'élève change de nom après que sa présence a été enregistrée, la présence devrait-elle afficher l'ancien ou le nouveau nom ?

**Solution** : Au moment de l'enregistrement, on copie le nom de l'élève dans `student_name_snapshot`. Même si le nom change ensuite dans la table Student, le snapshot garde l'historique exact.

---

*Continuez avec `04_FONCTIONNALITES.md` pour découvrir toutes les fonctionnalités de l'application.*
