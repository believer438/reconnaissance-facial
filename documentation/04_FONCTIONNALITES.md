# Fonctionnalités de l'Application — Ce que l'on peut faire

## Vue d'ensemble

L'application UniPresence propose **plus de 30 fonctionnalités** organisées autour de 8 grands modules. Ce document les décrit toutes en langage simple.

---

## Module 1 : Tableau de bord

### Ce que c'est
La page d'accueil du système. Elle donne une vue globale de la situation en temps réel.

### Ce qu'elle affiche
- **Compteurs globaux** : nombre total d'élèves, de classes, de salles, de photos, de caméras actives
- **Présence du jour** : combien d'élèves sont présents, en retard, absents, ou excusés aujourd'hui
- **Taux de présence du jour** : affiché en pourcentage
- **Alertes** : liste des élèves ayant dépassé le seuil d'absences configuré
- **Arrivées récentes** : les derniers élèves arrivés (avec l'heure)
- **Visages inconnus récents** : les 4 dernières détections de visages non reconnus
- **État du modèle IA** : le modèle est-il entraîné et prêt à fonctionner ?
- **Photos non entraînées** : nombre de photos ajoutées depuis le dernier entraînement
- **Prochain jour férié** : si un jour férié approche

---

## Module 2 : Gestion des élèves

### Lister les élèves
- Affichage de tous les élèves actifs
- Recherche par nom ou matricule
- Filtrage par faculté ou par classe
- Affichage du nombre de photos par élève

### Ajouter un élève
Formulaire complet avec :
- Nom, post-nom, prénom, sexe
- Matricule (unique, vérifié en temps réel lors de la saisie)
- Classe, section, année scolaire
- Date et lieu de naissance
- Adresse
- Informations du parent/tuteur (nom + téléphone)
- Email, téléphone de l'élève
- Statut (actif, transféré, suspendu, exclu, diplômé, inactif)
- Photo de profil officielle

### Fiche détaillée d'un élève
- Toutes ses informations personnelles
- Ses photos d'entraînement (avec statut : entraîné ou non)
- Possibilité d'ajouter des photos directement depuis la fiche
- Son historique de présence (journalier)
- Son taux de présence calculé automatiquement
- Nombre d'absences

### Modifier / Supprimer un élève
- Modification de toutes les informations
- Suppression avec confirmation (pour éviter les suppressions accidentelles)

### Vérification du matricule en temps réel
Quand on saisit un matricule dans le formulaire, le système vérifie immédiatement si ce matricule est déjà utilisé, sans recharger la page.

---

## Module 3 : Gestion des photos et entraînement IA

### Ajouter des photos à un élève
- Upload multiple (plusieurs photos à la fois)
- L'angle peut être précisé (face, gauche, droite, incliné)
- Chaque photo est analysée immédiatement : est-ce qu'un visage est détecté ?

### Supprimer une photo
- Suppression avec confirmation

### Entraîner le modèle IA
- Bouton « Lancer l'entraînement » dans l'interface
- Le système traite toutes les photos non encore entraînées
- Rapport final : nombre d'élèves traités, photos utilisées, photos ignorées (floues), durée
- L'historique de chaque entraînement est conservé

### Reconnaître depuis une photo uploadée
- Uploader une photo de groupe
- Le système détecte tous les visages dans la photo
- Pour chaque visage reconnu : enregistrement de présence
- Pour chaque visage inconnu : sauvegarde dans la galerie des inconnus

---

## Module 4 : Gestion des caméras

### Types de caméras supportées
1. **Webcam navigateur** : la caméra de l'ordinateur ou de la tablette depuis laquelle on utilise l'application
2. **Caméra USB** : branchée directement au serveur
3. **Caméra IP (RTSP)** : caméra réseau professionnelle (Hikvision, Dahua, Axis...)

### Modes de fonctionnement
- **RECOGNITION** : IA active, reconnaît les visages et enregistre les présences
- **MONITORING ONLY** : affiche le flux vidéo sans traitement IA
- **OFF** : caméra désactivée

### Zones de caméra
- **CHECK-IN** : caméra à l'entrée de l'école, enregistre l'arrivée des élèves
- **MONITORING** : surveillance sans enregistrement de présence

### Page caméra en direct (Live)
- Affichage du flux vidéo en temps réel
- Rectangles colorés autour des visages détectés :
  - **Vert** : élève reconnu → nom affiché
  - **Rouge** : visage inconnu
  - **Jaune** : déjà marqué aujourd'hui
- Score de confiance affiché
- Liste des présences enregistrées pendant la session
- Sélection de la session de cours active

### Tableau de bord des caméras
- État en temps réel de chaque caméra (en ligne / hors ligne)
- FPS estimé
- Nombre d'images traitées
- Dernière erreur

---

## Module 5 : Gestion des cours et séances

### Cours
- Créer un cours (code, nom, faculté, professeur, crédits)
- Inscrire des élèves à un cours
- Voir tous les inscrits
- Gérer les sessions (séances)

### Horaires hebdomadaires
- Définir l'emploi du temps de chaque classe (quel cours, quel jour, quelle heure, quelle salle)
- Validation automatique : le système empêche les chevauchements d'horaires pour la même classe, le même professeur, ou la même salle

### Sessions de cours (séances)
- Créer une séance (date, heure, salle)
- La séance peut avoir les statuts : En attente → Ouvert → Fermé (ou Annulé)
- Ouvrir/fermer manuellement une séance
- Annuler une séance avec motif

### Clôture de session
Le bouton « Marquer absents et fermer » :
1. Récupère tous les élèves inscrits au cours
2. Pour ceux sans présence enregistrée → crée un enregistrement « absent »
3. Ferme la session

---

## Module 6 : Présence journalière (Mode École Secondaire)

Ce module est conçu pour les écoles secondaires qui veulent juste savoir qui est arrivé le matin, sans gestion de cours.

### Configuration de la journée scolaire
- Heure d'ouverture du portail
- Heure de début des cours (arrivée = « présent »)
- Heure limite d'arrivée (après = « en retard »)
- Heure de fin des cours
- Jours de classe (lundi à samedi)

### Fonctionnement
- Quand un élève passe devant la caméra CHECK-IN :
  - Avant l'heure limite → « Présent »
  - Après l'heure limite → « En retard »
- À la fin de la journée → génération automatique des absents pour les élèves non vus

### Génération automatique des absences
La commande `auto_daily` peut être programmée pour s'exécuter automatiquement à l'heure de fin des cours. Elle génère les enregistrements « absent » pour tous les élèves sans présence ce jour-là. Elle vérifie :
- Que c'est un jour de classe
- Que ce n'est pas un jour férié
- Que l'heure de fin des cours est passée

### Vue par classe
- Voir la présence d'une classe entière pour une date donnée
- Navigation jour par jour (◀ ▶)
- Taux de présence de la classe

---

## Module 7 : Rapports et statistiques

### Rapport de présence
- Filtrage par cours, date de début, date de fin
- Pour chaque élève : nombre de sessions, présences, absences, taux de présence
- Calcul automatique : présent + retard = présent, absent = baisse du taux

### Export CSV
- Export compatible Excel (séparateur point-virgule, encodage UTF-8 avec BOM)
- Colonnes : nom, matricule, classe, total sessions, présents, absents, taux

### Statistiques par classe
- Taux de présence global de la classe
- Évolution dans le temps

---

## Module 8 : Administration et configuration

### Gestion des utilisateurs
- Créer des comptes (Admin, Enseignant, Secrétariat)
- Modifier les informations et le rôle
- Réinitialiser le mot de passe
- Désactiver/réactiver un compte

### Gestion des salles
- Créer des salles avec bâtiment et capacité
- Lier des caméras à des salles
- Lier des horaires à des salles

### Gestion des classes
- Créer des classes avec niveau et option
- Voir les élèves de chaque classe
- Voir les horaires de chaque classe

### Calendrier scolaire (Jours fériés)
- Ajouter des jours fériés, vacances, ou suspensions de cours
- Ces dates sont automatiquement exclues des présences et de la génération des absences

### Configuration système
Tous les paramètres du système en un seul endroit :
- Seuils de confiance LBPH (haute confiance, zone de doute)
- Tolérance de retard (minutes)
- Fenêtre pré-cours (minutes avant le cours)
- Cooldown anti-doublon
- Activer/désactiver le filtre par classe
- Activer/désactiver l'archivage des événements bruts
- Seuil d'alerte d'absences

### Journal d'activité système
- Historique complet de toutes les actions : qui, quoi, quand, depuis quelle adresse IP
- Types : connexions, créations, modifications, suppressions, entraînements IA, exports...
- Immuable (les utilisateurs ne peuvent pas le modifier)

### Journal d'audit des présences
- Chaque modification manuelle d'une présence est tracée
- Affiche : qui a modifié, l'ancien statut, le nouveau statut, la raison

### Diagnostic système
- Page de vérification de l'état du système
- Vérifie si OpenCV et le module LBPH sont disponibles
- Affiche la version du modèle entraîné

### File de revue
- Liste des reconnaissances incertaines en attente
- L'administrateur peut valider (présence enregistrée) ou rejeter
- Affiche la photo du visage, le nom proposé, le score

### Galerie des visages inconnus
- Photos de tous les visages non reconnus
- Permet d'identifier des personnes non inscrites
- Possibilité d'ajouter des notes

### Événements de détection bruts
- Historique complet de chaque tentative de reconnaissance
- États : détecté → reconnu → enregistré / refusé / hors classe / inconnu / doublon

---

*Continuez avec `05_TECHNOLOGIES.md` pour comprendre les outils utilisés et pourquoi ils ont été choisis.*
