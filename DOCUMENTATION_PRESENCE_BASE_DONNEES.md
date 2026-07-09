# Documentation presence et base de donnees

Ce document decrit la logique metier actuelle de SecPresence: eleves, classes,
journee scolaire, reconnaissance faciale, presences, retards, absences,
sorties et justifications.

## Objectif fonctionnel

Le systeme doit gerer une ecole secondaire avec:

- des classes contenant des eleves actifs;
- une journee scolaire configurable;
- des jours feries ou jours suspendus;
- une reconnaissance faciale pour l'entree et la sortie;
- une presence journaliere par eleve et par date;
- des retards calcules selon l'heure limite d'arrivee;
- des absences generees en fin de journee;
- des justifications modifiables manuellement;
- des statistiques par classe ouvrant le detail de la classe.

## Tables principales

### `Classe`

Represente une classe scolaire.

Champs importants:

- `nom`: nom complet de la classe.
- `niveau`: niveau scolaire.
- `option`: option ou specialite.
- `annee_academique`: annee scolaire.
- `is_active`: classe active ou non.

Relations:

- `Classe` possede plusieurs `Student`.
- `Classe` possede plusieurs `Schedule`.

### `Student`

Represente un eleve.

Champs importants:

- `full_name`, `nom`, `post_nom`, `prenom`: identite.
- `student_code`: matricule unique.
- `classe`: lien vers `Classe`.
- `statut`: actif, transfere, suspendu, exclu, diplome, inactif.
- `is_active`: calcule depuis `statut == actif`.
- `photo_profil`: photo officielle.

Regle importante:

- Un vrai visage doit correspondre a un seul eleve actif.
- Si le meme visage existe dans plusieurs eleves actifs, le moteur facial refuse
  la presence automatique car la marge entre candidats devient insuffisante.

### `TrainingPhoto`

Photo d'entrainement d'un eleve.

Champs importants:

- `student`: eleve source.
- `image`: image stockee.
- `angle_tag`: face, gauche, droite, incline, autre.
- `trained_at`: date d'utilisation dans le modele.
- `face_detected`: indique si un visage exploitable a ete trouve.

### `FaceEmbedding`

Empreinte faciale calculee depuis une photo.

Champs importants:

- `student`: eleve.
- `photo`: photo source.
- `vector`: vecteur binaire SFace.
- `score_qualite`: qualite/detection.

Moteur actuel:

- Detection: OpenCV YuNet.
- Reconnaissance: OpenCV SFace.
- Les anciens champs et noms LBPH peuvent encore exister pour compatibilite,
  mais le moteur principal est SFace si les fichiers ONNX sont presents.

### `SchoolDayConfig`

Configuration singleton de la journee scolaire.

Champs importants:

- `heure_ouverture`: debut autorise des passages.
- `heure_debut_cours`: heure normale de debut.
- `heure_limite_arrivee`: apres cette heure, l'eleve est en retard.
- `heure_fin_cours`: fin normale des cours.
- `heure_sortie_precoce`: sortie avant cette heure = sortie precoce.
- `heure_fermeture`: apres cette heure, la camera refuse l'enregistrement.
- `lundi` a `samedi`: jours scolaires actifs.

Regles:

- Pas d'enregistrement automatique un jour non scolaire.
- Pas d'enregistrement automatique un jour ferie.
- Pas d'entree avant `heure_ouverture`.
- Pas d'entree ou sortie apres `heure_fermeture`.

### `JourFerie`

Jour non ouvrable ou suspendu.

Champs importants:

- `nom`: motif.
- `date`: date unique.
- `type_jour`: ferie, vacances, suspension.

Effet metier:

- Bloque la generation automatique d'absences.
- Bloque les enregistrements automatiques par camera.

### `DailyAttendance`

Presence journaliere d'un eleve.

Un seul enregistrement par eleve et par date.

Champs importants:

- `student`: eleve.
- `date`: date de presence.
- `heure_entree`: heure d'arrivee.
- `heure_sortie`: heure de sortie.
- `status`: statut courant.
- `camera_entree`: camera d'entree.
- `camera_sortie`: camera de sortie.
- `excuse_reason`: type de justification.
- `excuse_notes`: notes de justification.
- `modified_by`: personne ayant modifie manuellement.

Statuts:

- `present`: arrive avant ou a l'heure limite.
- `retard`: arrive apres l'heure limite.
- `absent`: absence generee ou saisie manuellement.
- `sorti`: sortie normale.
- `sortie_precoce`: sortie avant le seuil de sortie precoce.
- `excuse`: absence ou situation justifiee manuellement.

## Flux de presence journaliere

### Entree

1. La camera detecte un visage.
2. Le moteur SFace cherche l'eleve.
3. Si le visage est reconnu sans ambiguite, le systeme verifie:
   - jour scolaire;
   - absence de jour ferie;
   - heure entre ouverture et fermeture.
4. Si aucune presence n'existe pour l'eleve ce jour:
   - `heure_entree` est enregistree;
   - statut = `present` si l'heure est avant ou egale a `heure_limite_arrivee`;
   - statut = `retard` si l'heure est apres `heure_limite_arrivee`.
5. Si une entree existe deja, le systeme renvoie doublon.

### Sortie

1. La camera de sortie reconnait l'eleve.
2. Le systeme verifie jour scolaire, jour ferie et plage horaire.
3. Si aucune entree n'existe, la sortie est refusee.
4. Si une sortie existe deja, le systeme renvoie doublon.
5. Sinon:
   - `heure_sortie` est enregistree;
   - statut = `sortie_precoce` si sortie avant `heure_sortie_precoce`;
   - statut = `sorti` sinon.

### Absences

La generation des absences se fait depuis la liste journaliere.

Regles:

- Impossible un jour ferie.
- Impossible un jour non scolaire.
- Pour chaque eleve actif sans `DailyAttendance` a la date du jour:
  - creation d'un enregistrement `absent`;
  - `modified_by = Systeme (generation auto)`.

### Justifications

Les justifications sont manuelles.

Depuis la page de modification d'une presence journaliere, l'utilisateur peut:

- changer le statut;
- renseigner une heure d'entree;
- renseigner une heure de sortie;
- choisir un type de justificatif;
- saisir des notes;
- renseigner le nom de la personne qui modifie.

Types de justification:

- maladie;
- mission;
- deuil;
- autorisation parentale;
- autre.

## Statistiques par classe

La page `Stats par classe` utilise `DailyAttendance` pour une date donnee.

Calcul par classe:

- `nb_students`: eleves actifs dans la classe.
- `nb_present`: statut `present`.
- `nb_retard`: statut `retard`.
- `nb_excuse`: statut `excuse`.
- `nb_sorti`: statuts `sorti` et `sortie_precoce`.
- `nb_absent`: absences explicites + eleves sans enregistrement.
- `rate`: `(present + retard + excuse + sorti) / eleves actifs`.

Le bouton de detail ouvre maintenant:

```text
/facial/classes/<id>/?date=YYYY-MM-DD
```

et non plus le rapport global.

## Detail d'une classe

La page detail classe affiche:

- statistiques du jour;
- liste des eleves actifs de la classe;
- statut journalier de chaque eleve;
- heures d'entree et sortie;
- nombre d'empreintes faciales;
- horaires lies a la classe;
- derniers mouvements de presence.

## Donnees historiques

Deux systemes coexistent dans la base:

- `AttendanceRecord`: ancien modele oriente cours/session.
- `DailyAttendance`: modele principal pour l'ecole secondaire et la presence journaliere.

Pour la logique actuelle demandee, `DailyAttendance` est la source prioritaire.
`AttendanceRecord` peut rester utile pour des rapports universitaires ou
presences par cours, mais ne doit pas piloter les statistiques de presence
journaliere par classe.

## Recommandations d'exploitation

- Creer les classes avant les eleves.
- Associer chaque eleve a une classe.
- Garder un seul compte actif par vraie personne.
- Ajouter plusieurs photos nettes par eleve.
- Recalculer les embeddings apres de gros imports de photos.
- Configurer correctement `SchoolDayConfig`.
- Ajouter les jours feries avant de generer les absences.
- Generer les absences seulement apres la fin de la plage d'arrivee.

## Evolution possible

SQLite suffit pour un poste local ou une petite installation.

PostgreSQL ou Supabase devient utile si:

- plusieurs ordinateurs doivent partager les donnees;
- l'application est hebergee en ligne;
- il faut des sauvegardes automatiques;
- plusieurs secretariats utilisent le systeme en meme temps;
- le volume de photos, presences et logs devient important.
