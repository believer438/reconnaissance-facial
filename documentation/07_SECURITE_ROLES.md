# Sécurité et Rôles — Qui peut faire quoi

## Introduction

La sécurité d'un système de présence scolaire est critique. Les données de présence sont des données personnelles des élèves. Ce document explique comment le système gère les accès et protège les données.

---

## Les trois rôles d'utilisateurs

### Administrateur

**Qui c'est** : Le directeur, le responsable informatique, ou toute personne ayant la responsabilité du système.

**Ce qu'il peut faire** : Tout, sans restriction.
- Gérer les élèves (créer, modifier, supprimer)
- Gérer les cours, classes, salles
- **Entraîner le modèle IA** (fonctionnalité réservée)
- **Gérer la configuration système** (seuils, paramètres)
- **Gérer les utilisateurs** (créer des comptes, changer les rôles, réinitialiser les mots de passe)
- Valider/rejeter les tickets de revue
- Accéder au journal d'activité complet
- Exporter les rapports

### Enseignant

**Qui c'est** : Les professeurs, les chargés de cours.

**Ce qu'il peut faire** :
- Voir les présences de tous les cours
- Voir les rapports
- Ouvrir la caméra live pendant ses cours
- Voir les fiches des élèves

**Ce qu'il NE peut PAS faire** :
- Modifier les présences
- Ajouter ou supprimer des élèves
- Entraîner le modèle
- Modifier la configuration
- Gérer les utilisateurs

### Secrétariat

**Qui c'est** : Les agents administratifs, les secrétaires académiques.

**Ce qu'il peut faire** :
- Gérer les élèves (créer, modifier)
- Modifier les présences (avec motif obligatoire, tracé dans l'audit)
- Ajouter des excuses/justificatifs
- Exporter les rapports

**Ce qu'il NE peut PAS faire** :
- Entraîner le modèle IA
- Modifier la configuration système
- Gérer les utilisateurs
- Supprimer des données importantes

---

## Tableau récapitulatif des permissions

| Action | Administrateur | Enseignant | Secrétariat |
|--------|---------------|------------|-------------|
| Voir les présences | ✅ | ✅ | ✅ |
| Modifier une présence | ✅ | ❌ | ✅ |
| Ajouter un élève | ✅ | ❌ | ✅ |
| Supprimer un élève | ✅ | ❌ | ❌ |
| Ajouter des photos | ✅ | ❌ | ✅ |
| Entraîner le modèle | ✅ | ❌ | ❌ |
| Gérer la configuration | ✅ | ❌ | ❌ |
| Gérer les utilisateurs | ✅ | ❌ | ❌ |
| Valider la file de revue | ✅ | ❌ | ❌ |
| Voir le journal système | ✅ | ❌ | ❌ |
| Exporter les rapports | ✅ | ✅ | ✅ |
| Ouvrir la caméra live | ✅ | ✅ | ✅ |

---

## Les mécanismes de sécurité techniques

### 1. Obligation de se connecter (Middleware)

Un middleware est un filtre qui s'applique à TOUTES les requêtes, avant même que la page soit traitée.

```
Utilisateur essaie d'accéder à /facial/students/
         ↓
Middleware vérifie : est-il connecté ?
         ↓
NON → Redirection vers /facial/login/?next=/facial/students/
OUI → La page se charge normalement
```

Seules ces pages sont accessibles sans connexion :
- `/facial/login/` → la page de connexion
- `/facial/logout/` → déconnexion
- `/facial/admin/` → interface Django admin (a sa propre authentification)
- `/facial/api/` → API (utilisée par la caméra, nécessite une clé différente)

### 2. Protection CSRF (Cross-Site Request Forgery)

**Le problème CSRF** : Un site malveillant pourrait tromper un utilisateur connecté pour qu'il effectue une action à son insu (ex: supprimer un élève).

**La protection** : Chaque formulaire Django contient un jeton secret unique et aléatoire. Quand le formulaire est soumis, Django vérifie que le jeton correspond. Un site tiers ne connaît pas ce jeton → sa requête est rejetée.

### 3. Hachage des mots de passe

Django ne stocke JAMAIS les mots de passe en clair dans la base de données. Il applique un algorithme de hachage (PBKDF2 avec SHA256 par défaut). Même si quelqu'un vole la base de données, il ne peut pas lire les mots de passe.

Exemple de ce qui est stocké en base de données :
```
pbkdf2_sha256$600000$randomsalt$hashedpassword
```

C'est un code illisible. Pour vérifier le mot de passe lors de la connexion, Django refait le calcul et compare les codes — jamais les mots de passe en clair.

### 4. Sessions sécurisées

Quand un utilisateur se connecte :
1. Django crée une session (identifiant unique aléatoire)
2. Cet identifiant est stocké dans un cookie du navigateur
3. À chaque requête, Django vérifie que l'identifiant est valide
4. À la déconnexion, la session est invalidée

Configuration spéciale pour Replit (iframe) :
```python
SESSION_COOKIE_SAMESITE = "None"  # Nécessaire car l'app s'exécute dans un iframe
SESSION_COOKIE_SECURE = True      # Cookie uniquement sur HTTPS
```

### 5. Journal d'audit des présences

Chaque modification manuelle d'une présence laisse une trace immuable :
```
Qui : secretariat_marie
Quoi : absent → excusé
Quand : 2024-11-15 09:32
Raison : Certificat médical présenté
```

Cela garantit la traçabilité et évite les falsifications non tracées.

### 6. Journal d'activité système (SystemLog)

Toutes les actions importantes sont journalisées automatiquement :
- Connexions et déconnexions
- Créations, modifications, suppressions
- Entraînements du modèle
- Exports de données
- Erreurs

Ce journal est accessible uniquement aux administrateurs et ne peut pas être modifié par les utilisateurs.

### 7. Variable d'environnement pour la clé secrète

La clé secrète Django (SESSION_SECRET) n'est pas dans le code. Elle est stockée dans une variable d'environnement sécurisée de Replit :
```python
SECRET_KEY = os.environ.get("SESSION_SECRET", "local-dev-secret-key")
```

Cela évite que la clé ne soit exposée si le code est partagé.

---

## Protection des données personnelles

### Données stockées

Le système stocke des données personnelles des élèves :
- Nom, prénom, date de naissance, lieu de naissance
- Informations de contact
- Photos du visage (biométrie)
- Historique de présence

### Qui peut accéder aux photos ?

Les photos d'entraînement des élèves sont stockées dans `media/students/`. L'accès à ces fichiers nécessite une connexion et est protégé par Django. Un utilisateur externe ne peut pas parcourir les photos.

### Le modèle IA ne contient pas de photos

Le fichier `media/models/trainer.yml` contient le modèle LBPH entraîné. Ce fichier contient des matrices de nombres (histogrammes) — pas les photos originales. On ne peut pas « extraire » les photos du modèle.

### Données biométriques

Les photos de visage sont considérées comme des données biométriques (données sensibles selon le RGPD et équivalents africains). Dans un contexte réel de déploiement, l'école devrait obtenir le **consentement éclairé** des élèves et/ou de leurs parents avant d'utiliser la reconnaissance faciale.

---

## Gestion des mots de passe

### Créer un nouvel utilisateur

Aller dans **Administration → Utilisateurs → Nouvel utilisateur** :
1. Choisir un nom d'utilisateur
2. Définir un mot de passe temporaire
3. Sélectionner le rôle
4. Communiquer le mot de passe à l'utilisateur par un canal sécurisé

### Réinitialiser un mot de passe oublié

Aller dans **Administration → Utilisateurs** → Cliquer sur l'utilisateur → « Réinitialiser le mot de passe » :
1. L'administrateur définit un nouveau mot de passe temporaire
2. L'utilisateur change son mot de passe lors de sa prochaine connexion

---

## Sécurité réseau

### Déploiement actuel (Replit)

Le projet est accessible via HTTPS (chiffrement du trafic). Replit gère automatiquement le certificat SSL.

### Déploiement local (recommandé pour une vraie école)

Pour une vraie école, on recommande :
- Déployer sur un serveur local (réseau interne de l'école)
- Configurer HTTPS avec un certificat SSL
- Restreindre l'accès depuis l'extérieur (pare-feu)
- Sauvegardes régulières de `db.sqlite3` et `media/`

---

*Continuez avec `08_CAMERAS_TYPES.md` pour comprendre en détail le fonctionnement des différents types de caméras.*
