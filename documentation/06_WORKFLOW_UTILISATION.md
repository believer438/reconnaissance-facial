# Workflow d'utilisation — Comment utiliser l'application au quotidien

## Introduction

Ce document explique pas à pas comment utiliser l'application dans une situation réelle d'école ou d'université. Il est organisé en phases : la configuration initiale (faite une seule fois), puis l'utilisation quotidienne.

---

## Phase 1 : Configuration initiale (à faire une seule fois)

### Étape 1.1 : Se connecter

Lors du premier démarrage, le système crée automatiquement un compte administrateur :
- **Identifiant** : `admin`
- **Mot de passe** : `admin123`

⚠️ **Important** : Changer ce mot de passe immédiatement après la première connexion !

### Étape 1.2 : Configurer les paramètres du système

Aller dans **Administration → Configuration système** et vérifier/ajuster :
- Les seuils de confiance LBPH (par défaut : 58 pour haute confiance, 75 pour limite)
- La tolérance de retard (par défaut : 15 minutes)
- La fenêtre pré-cours (par défaut : 10 minutes avant le début)
- Le seuil d'alerte absences (par défaut : 3 absences)

### Étape 1.3 : Configurer la journée scolaire (École secondaire uniquement)

Aller dans **Administration → Configuration journée scolaire** :
- Heure d'ouverture du portail
- Heure de début des cours
- Heure limite d'arrivée (après cette heure = retard)
- Heure de fin des cours
- Cocher les jours de classe (lundi au samedi)

### Étape 1.4 : Créer les salles de classe

Aller dans **Administration → Salles** :
- Cliquer « Ajouter une salle »
- Renseigner le nom, le bâtiment, la capacité
- Exemple : « Amphi B », bâtiment « Bloc Scientifique », capacité 120

### Étape 1.5 : Créer les classes

Aller dans **Élèves → Classes** :
- Cliquer « Nouvelle classe »
- Renseigner le nom (ex: « L3 Informatique »), le niveau (ex: « L3 »), l'option, l'année académique

### Étape 1.6 : Créer les cours (Université uniquement)

Aller dans **Cours** :
- Cliquer « Nouveau cours »
- Renseigner le code (ex: « INFO401 »), l'intitulé, le professeur, les crédits, la faculté

### Étape 1.7 : Configurer les caméras

Aller dans **Caméras** :
- Cliquer « Ajouter une caméra »
- Choisir le type :
  - **Webcam navigateur** : la plus simple, fonctionne depuis n'importe quel ordinateur avec webcam
  - **USB** : source = « 0 » pour la première caméra USB, « 1 » pour la deuxième
  - **IP/RTSP** : source = l'URL RTSP de la caméra (ex: `rtsp://admin:password@192.168.1.10:554/stream`)
- Choisir la zone : CHECK-IN (entrée école) ou MONITORING (surveillance)
- Choisir le mode : RECOGNITION (IA active) ou MONITORING ONLY

### Étape 1.8 : Ajouter les jours fériés

Aller dans **Administration → Jours fériés** :
- Ajouter les jours fériés nationaux, les vacances scolaires, les suspensions de cours
- Ces dates seront automatiquement exclues de la génération des absences

### Étape 1.9 : Créer les comptes utilisateurs supplémentaires

Aller dans **Administration → Utilisateurs** :
- Créer un compte pour chaque enseignant (rôle : Enseignant)
- Créer un compte pour chaque agent du secrétariat (rôle : Secrétariat)
- Ne donner le rôle Administrateur qu'au(x) responsable(s) du système

---

## Phase 2 : Enregistrement des élèves (à faire au début de chaque année)

### Étape 2.1 : Créer les fiches élèves

Aller dans **Élèves → Ajouter un élève** :
- Remplir toutes les informations : nom, matricule, classe, date de naissance...
- Le matricule doit être unique — le système le vérifie en temps réel

### Étape 2.2 : Inscrire les élèves aux cours (Université)

Aller dans le détail d'un cours → onglet « Inscrits » :
- Cliquer « Inscrire des élèves »
- Sélectionner les élèves à inscrire

Ou depuis la fiche de l'élève, l'inscrire directement à ses cours.

### Étape 2.3 : Photographier les élèves

C'est l'étape la plus importante pour la qualité de la reconnaissance.

Aller dans la fiche d'un élève → onglet « Photos » → « Ajouter des photos »

**Conseils pour de bonnes photos :**
- Prendre **5 à 15 photos** par élève
- Varier les **angles** : de face, légèrement à gauche, légèrement à droite
- Varier les **éclairages** : lumière naturelle, lumière artificielle
- Éviter les photos **floues** (l'IA les ignorera automatiquement)
- Visage **clairement visible** : pas de chapeau couvrant le front, pas de lunettes de soleil
- Si l'élève porte des lunettes ou un uniforme → prendre des photos AVEC ces accessoires
- Résolution minimale recommandée : 640×480 pixels

### Étape 2.4 : Entraîner le modèle IA

Après avoir ajouté les photos, aller dans **Administration → Entraînement** (ou depuis le tableau de bord) :
- Cliquer « Lancer l'entraînement »
- Attendre la fin (quelques secondes à quelques minutes selon le nombre d'élèves)
- Vérifier le rapport : nombre d'élèves traités, photos utilisées, photos ignorées

**Quand réentraîner ?** Le tableau de bord affiche le nombre de « Photos non entraînées ». Si ce nombre est > 0, un réentraînement est recommandé.

---

## Phase 3 : Utilisation quotidienne — Mode Université (par cours)

### Avant chaque cours

**Option A : Créer une session manuellement**
- Aller dans **Cours** → Cliquer sur le cours concerné → « Nouvelle session »
- Renseigner la date, l'heure, la salle, la tolérance de retard
- Cliquer « Ouvrir » pour activer la session

**Option B : Utiliser l'horaire automatique** (si l'emploi du temps est configuré)
- Les sessions peuvent être créées à partir des horaires définis dans le planning

### Pendant le cours — Reconnaissance en direct

Aller dans **Caméras** → Cliquer « Ouvrir » sur la caméra souhaitée → Page « Live »

1. Sélectionner la session de cours active dans le menu déroulant
2. Autoriser l'accès à la webcam (si demandé par le navigateur)
3. Les élèves passent devant la caméra
4. La reconnaissance se fait automatiquement :
   - Rectangle **vert** + nom affiché : élève reconnu → présence enregistrée
   - Rectangle **rouge** : visage inconnu (non inscrit ou non reconnu)
   - Rectangle **jaune** : élève déjà marqué aujourd'hui (doublon évité)

### Après le cours — Clôture de session

Aller dans le détail de la session → Bouton « Marquer absents et fermer » :
1. Le système génère automatiquement les enregistrements « absent » pour les élèves non détectés
2. La session est fermée (les enregistrements manuels sont encore possibles)

### Alternative : Reconnaissance par photo de groupe

- Aller dans **Reconnaissance → Uploader une photo**
- Uploader une photo prise pendant le cours
- Le système détecte tous les visages dans la photo et enregistre les présences

---

## Phase 4 : Utilisation quotidienne — Mode École Secondaire (présence du matin)

### Chaque matin — Accueil des élèves

1. La caméra CHECK-IN est active (configurée en mode RECOGNITION)
2. Les élèves passent à l'entrée : leur visage est reconnu
3. La présence est enregistrée automatiquement avec l'heure
4. L'élève arrivé avant l'heure limite → « Présent »
5. L'élève arrivé après l'heure limite → « En retard »

### En fin de journée — Génération des absences

**Automatiquement** : Si la commande `auto_daily` est programmée (cron), les absences sont générées automatiquement après l'heure de fin des cours.

**Manuellement** : Aller dans **Présences journalières** → « Générer les absences ».

### Consultation des présences du jour

- Tableau de bord → Section présences du jour (présents / retards / absents)
- **Élèves → Classes** → Cliquer sur une classe → Voir la présence de chaque élève du jour
- Navigation jour par jour avec les flèches ◀ ▶

---

## Phase 5 : Gestion des cas particuliers

### Un élève n'est pas reconnu mais est présent

1. L'enseignant note l'absence sur la liste
2. Aller dans **Présences** → Trouver la session → Modifier la présence manuellement
3. Changer le statut de « absent » à « présent » ou « retard »
4. La modification est tracée dans le journal d'audit

### Un élève est absent pour raison valable

1. Modifier la présence → Statut « excusé »
2. Choisir le type de justificatif (maladie, mission officielle, deuil, autorisation...)
3. Ajouter des notes explicatives

### La file de revue — Reconnaissances incertaines

Aller dans **File de revue** :
- La liste des reconnaissances douteuses s'affiche avec la photo du visage
- Pour chaque ticket : lire le nom proposé, voir le score, regarder la photo
- Cliquer « Valider » si c'est bien cet élève → présence enregistrée
- Cliquer « Rejeter » si ce n'est pas cet élève → aucune présence

---

## Phase 6 : Rapports et analyses

### Générer un rapport de présence

Aller dans **Rapports** :
1. Sélectionner le cours (ou tous les cours)
2. Choisir la période (date de début → date de fin)
3. Cliquer « Générer »

Le rapport affiche pour chaque élève :
- Nombre de sessions totales
- Nombre de sessions présent
- Nombre d'absences
- Taux de présence en pourcentage

### Exporter vers Excel

Depuis le rapport → Cliquer « Exporter CSV »
- Ouvrir le fichier `.csv` dans Excel
- Le fichier est encodé en UTF-8 avec BOM pour éviter les problèmes d'accents
- Le séparateur est le point-virgule (standard français)

---

## Phase 7 : Maintenance

### Sauvegarder le système

Sauvegarder régulièrement :
1. Le fichier `db.sqlite3` (toutes les données)
2. Le dossier `media/` (photos et modèle IA)

Ces deux éléments suffisent à restaurer complètement le système.

### Réentraîner le modèle

Nécessaire après :
- L'ajout de nouvelles photos d'élèves
- L'ajout de nouveaux élèves
- Une dégradation des performances de reconnaissance

---

*Continuez avec `07_SECURITE_ROLES.md` pour comprendre la gestion de la sécurité et des accès.*
