# Index du Questionnaire — Guide de Préparation pour le Jury

## Comment utiliser ce dossier

Ce dossier contient TOUTES les questions possibles que votre jury peut vous poser, organisées par thème. Chaque fichier contient les questions avec des réponses détaillées, expliquées simplement.

**Conseil** : Ne mémorisez pas les réponses mot pour mot. Comprenez les concepts, et reformulez avec vos propres mots.

---

## Fichiers disponibles

### 📄 `01_QUESTIONS_GENERALES.md`
Questions sur le projet dans son ensemble :
- Présentation du projet
- Problème résolu
- Pour qui est-il destiné
- Limites du projet
- Comparaison avec d'autres approches
- Déploiement en contexte africain
- Gestion des pannes

**Niveau :** Accessible à tous. Commencez par là.

---

### 📄 `02_QUESTIONS_TECHNIQUE_IA.md`
Questions sur l'intelligence artificielle et la reconnaissance faciale :
- Comment fonctionne LBPH (expliqué simplement)
- Qu'est-ce que Haar Cascade
- Les seuils de confiance
- L'égalisation d'histogramme
- Le score Laplacian (détection de flou)
- L'augmentation de données
- La file de revue
- Reconnaissance simultanée de plusieurs visages
- Anti-doublon

**Niveau :** Intermédiaire. Important pour convaincre le jury de votre maîtrise technique.

---

### 📄 `03_QUESTIONS_BASE_DE_DONNEES.md`
Questions sur la base de données et la modélisation :
- Pourquoi SQLite
- Les modèles de données principaux
- Clés étrangères et relations
- Migrations
- Contraintes d'unicité
- Index de performance
- Le pattern Singleton
- Les snapshots
- L'audit des modifications
- L'ORM Django

**Niveau :** Intermédiaire. Crucial pour un jury technique.

---

### 📄 `04_QUESTIONS_CONCEPTION.md`
Questions sur les choix d'architecture et de conception :
- Pourquoi Django
- Le pattern MVT
- Gestion des erreurs
- Maintenabilité du code
- Sécurité
- Middleware
- Scalabilité
- Tests
- Améliorations futures
- Performance temps réel

**Niveau :** Avancé. Pour montrer votre réflexion sur les choix de design.

---

### 📄 `05_QUESTIONS_ETHIQUE_JURIDIQUE.md`
Questions sur l'éthique et la conformité légale :
- Éthique de la reconnaissance faciale dans les écoles
- Protection des données personnelles
- Conformité RGPD
- Biais algorithmiques
- Données des mineurs
- Consentement
- Responsabilité en cas d'erreur

**Niveau :** Important — Les jurys posent souvent des questions sur l'éthique de l'IA.

---

### 📄 `06_QUESTIONS_APPROFONDIES.md`
Questions très techniques pour un jury d'experts :
- Complexité algorithmique de LBPH
- La distance chi-carré en détail
- Les commandes de gestion Django
- Sessions et cookies
- Migrations en détail
- Context processors
- Structure de l'API JSON
- Pattern Singleton en Python
- Validation des chevauchements d'horaire
- Stratégie d'indexation

**Niveau :** Expert. Préparez-vous si votre jury inclut des informaticiens spécialisés.

---

## Questions les plus probables (top 10)

D'après l'expérience de présentations similaires, voici les 10 questions les plus susceptibles d'être posées :

1. **"Présentez votre projet"** → `01_Q1`
2. **"Comment fonctionne la reconnaissance faciale ?"** → `02_Q1`
3. **"C'est quoi LBPH ?"** → `02_Q2`
4. **"Pourquoi pas le Deep Learning ?"** → `02_Q3`
5. **"Quelle base de données et pourquoi ?"** → `03_Q1`
6. **"Quelles sont les limites de votre projet ?"** → `01_Q5`
7. **"Comment gérez-vous la sécurité ?"** → `04_Q5`
8. **"Est-ce éthique ?"** → `05_Q1`
9. **"Qu'est-ce qu'une migration ?"** → `03_Q4`
10. **"Quelles améliorations futures ?"** → `04_Q9`

---

## Terminologie à maîtriser

Assurez-vous de pouvoir expliquer simplement ces termes :

| Terme | Explication simple |
|-------|-------------------|
| LBPH | Algorithme de reconnaissance faciale basé sur les textures locales des visages |
| Haar Cascade | Algorithme de détection de visages dans une image |
| Histogramme | Graphique montrant la distribution des valeurs (ici : des pixels) |
| Distance chi-carré | Mesure mathématique de différence entre deux histogrammes |
| Seuil de confiance | Valeur limite qui décide si une correspondance est acceptée |
| Égalisation d'histogramme | Technique pour normaliser l'éclairage d'une image |
| Score Laplacian | Mesure de la netteté d'une image |
| Migration (BDD) | Fichier décrivant un changement de structure de la base de données |
| ORM | Système qui traduit les tables SQL en objets Python |
| Middleware | Filtre qui s'applique à toutes les requêtes HTTP |
| Singleton | Classe qui n'a qu'une seule instance dans tout le programme |
| Clé étrangère | Lien entre deux tables de base de données |
| Index (BDD) | Structure accélérant les recherches dans une table |
| CSRF | Attaque web — le token CSRF la prévient |
| Base64 | Format encodant des données binaires en texte |
| RTSP | Protocole de streaming vidéo des caméras IP |
| Augmentation de données | Créer des exemples supplémentaires en transformant les données existantes |

---

## Conseils pour la présentation orale

1. **Commencez par le concret** : « Notre système permet à un professeur de... » avant d'expliquer le technique
2. **Utilisez des analogies** : Comparez les concepts abstraits à des choses du quotidien
3. **Admettez les limites** : Le jury apprécie l'honnêteté. Connaître les limites montre la maîtrise
4. **Expliquez les choix** : « Nous avons choisi X parce que... » vaut mieux que « nous avons utilisé X »
5. **Ne paniquez pas sur les questions inattendues** : « C'est une bonne question, je vais y réfléchir... » est acceptable

---

*Bonne chance pour votre présentation ! Ce projet est solide — faites confiance à votre travail.*
