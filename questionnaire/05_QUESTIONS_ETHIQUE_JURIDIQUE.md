# Questions Éthiques et Juridiques — Questionnaire Jury

---

## Q1 : La reconnaissance faciale dans les écoles, est-ce éthique ?

**Réponse :**
C'est une question importante et légitime. La reconnaissance faciale dans les écoles soulève des préoccupations éthiques réelles :

**Arguments en faveur :**
- Améliore l'efficacité administrative (pas de temps perdu à faire l'appel)
- Réduit la fraude aux présences (impossible de répondre pour un absent)
- Facilite le suivi des élèves à risque (absences répétées détectées automatiquement)
- Données stockées localement, pas transmises à des tiers

**Arguments contre :**
- Collecte de données biométriques sur des mineurs (données très sensibles)
- Risque de surveillance excessive et de « normalisation de la surveillance »
- Possible biais de reconnaissance selon l'origine ethnique (LBPH peut être moins précis pour certains groupes)
- Sentiment d'être constamment surveillé, impact psychologique sur les élèves

**Notre position :**
Notre système est conçu comme un **outil d'assistance**, pas de surveillance totale. La file de revue et les corrections manuelles maintiennent l'humain dans la boucle décisionnelle. Le consentement éclairé des élèves et parents est indispensable pour un déploiement éthique.

---

## Q2 : Quels sont les risques liés à la protection des données personnelles ?

**Réponse :**
Notre système traite plusieurs catégories de données personnelles :

**Données ordinaires :**
- Nom, prénom, matricule, date de naissance
- Historique de présence

**Données biométriques (catégorie spéciale — très sensibles) :**
- Photos du visage
- Le modèle LBPH (dérivé des photos)

**Risques principaux :**

1. **Vol de la base de données** : Si quelqu'un accède au fichier `db.sqlite3`, il obtient toutes les données personnelles des élèves. Protection : chiffrement du disque, accès physique limité au serveur.

2. **Accès non autorisé** : Si un utilisateur non autorisé se connecte à l'interface. Protection : authentification obligatoire, rôles granulaires.

3. **Fuite des photos** : Le dossier `media/students/` contient les photos. Protection : le serveur web ne sert pas ces fichiers directement ; ils passent par Django qui vérifie l'authentification.

4. **Utilisation détournée** : Le modèle entraîné pourrait théoriquement être utilisé pour reconnaître les élèves dans d'autres contextes. Protection : le modèle reste sur le serveur local, inaccessible de l'extérieur.

---

## Q3 : Votre système est-il conforme au RGPD (ou aux lois équivalentes) ?

**Réponse :**
Le RGPD (Règlement Général sur la Protection des Données) est une loi européenne de 2018. Des lois similaires existent dans de nombreux pays africains.

**Ce que le RGPD impose pour des données biométriques :**
1. **Consentement explicite** : L'élève (ou son parent s'il est mineur) doit consentir expressément à la collecte et l'utilisation de ses données biométriques
2. **Finalité limitée** : Les données ne peuvent être utilisées que pour la gestion des présences, pas d'autre usage
3. **Minimisation des données** : Ne collecter que ce qui est nécessaire
4. **Droit à l'effacement** : Un élève peut demander la suppression de ses données
5. **Sécurité appropriée** : Mesures techniques pour protéger les données

**Ce que notre système respecte déjà :**
- Stockage local (pas dans le cloud)
- Accès authentifié
- Suppression possible des photos et des élèves
- Journal d'audit

**Ce qui manquerait pour un déploiement conforme :**
- Formulaire de consentement formel
- Procédure documentée pour le droit à l'oubli
- Analyse d'impact (DPIA) préalable
- Désignation d'un DPO (Délégué à la Protection des Données)

---

## Q4 : Votre système peut-il être biaisé selon l'ethnicité ou d'autres facteurs ?

**Réponse :**
C'est une question fondamentale en IA éthique. 

**Le problème des biais en reconnaissance faciale :**
Des études ont montré que certains algorithmes de reconnaissance faciale sont moins précis pour les personnes à peau sombre, les femmes, et les personnes âgées. Cela s'explique par un manque de diversité dans les données d'entraînement de ces algorithmes.

**Dans le cas de LBPH :**
LBPH n'est pas entraîné sur un grand dataset universel — il est entraîné UNIQUEMENT sur les photos des élèves de votre école. Si vos élèves sont majoritairement d'une même origine, le modèle sera entraîné sur ces visages et devrait bien les reconnaître.

**Notre approche pour minimiser les biais :**
- Plus de photos par élève (5-15) pour capturer la diversité d'apparence d'une même personne
- Diversité d'angles et d'éclairages dans les photos d'entraînement
- La file de revue permet une validation humaine des cas douteux
- Les résultats peuvent être corrigés manuellement

**Biais en faveur de l'équité :**
Notre système ne peut pas prendre de décisions de type « cet élève mérite d'être exclu » — il ne fait que noter une présence ou une absence. La décision finale reste humaine.

---

## Q5 : Que se passe-t-il avec les données d'un élève quand il quitte l'école ?

**Réponse :**
Bonne question de conformité aux principes de protection des données.

**Actuellement dans notre système :**
Quand un élève termine ses études ou quitte l'école :
1. Son statut peut être changé en « diplômé » ou « inactif »
2. Il n'apparaît plus dans les listes actives
3. Mais ses données restent dans la base de données (historique d'archive)
4. Ses photos d'entraînement restent sur le serveur
5. Son empreinte reste dans le modèle LBPH

**Ce qui devrait être fait pour une conformité complète :**
Mettre en place une procédure d'archivage et d'anonymisation :
1. Après X années suivant le départ, anonymiser les données (remplacer le nom par un ID)
2. Supprimer les photos d'entraînement
3. Réentraîner le modèle sans les données de cet élève
4. Conserver uniquement les statistiques agrégées (% de présence)

**En pratique :**
La fonctionnalité de suppression d'un élève existe déjà (avec confirmation). Elle supprime aussi toutes ses photos. Un administrateur peut donc appliquer manuellement le droit à l'effacement quand un élève le demande.

---

## Q6 : Si la caméra se trompe et marque un élève présent par erreur, qui est responsable ?

**Réponse :**
C'est une question de gouvernance et de responsabilité importante.

**Position de notre système :**
Notre système est un **outil d'aide à la décision**, pas un système décisionnel autonome. Il n'y a pas de registre officiel qui se met à jour sans possibilité de correction.

**Mécanismes de correction :**
1. **File de revue** : Les reconnaissances incertaines ne sont pas automatiquement validées
2. **Correction manuelle** : N'importe quelle présence peut être corrigée par le secrétariat
3. **Journal d'audit** : Chaque correction est tracée avec le nom de la personne qui l'a faite et la raison

**Responsabilité :**
La responsabilité reste avec l'institution (l'école) et ses agents. L'IA fournit une assistance, mais la décision finale d'accepter ou de modifier une présence appartient aux humains. C'est pourquoi nous avons préservé les outils de correction manuelle et l'audit trail.

---

## Q7 : Comment abordez-vous la question du consentement des mineurs ?

**Réponse :**
Les mineurs ne peuvent pas consentir eux-mêmes à la collecte de données biométriques dans la plupart des cadres juridiques. C'est le parent ou tuteur légal qui doit consentir.

**Démarche recommandée pour un déploiement éthique :**
1. **Informer** les parents lors de l'inscription : expliquer ce qu'est la reconnaissance faciale, comment les données seront utilisées, qui y aura accès, combien de temps elles seront conservées
2. **Obtenir le consentement** par écrit (formulaire signé)
3. **Respecter le refus** : prévoir une alternative pour les élèves dont les parents refusent (présence manuelle)
4. **Permettre le retrait** : un parent peut retirer son consentement à tout moment

---

*Voir aussi : `06_QUESTIONS_APPROFONDIES.md` pour des questions techniques très avancées.*
