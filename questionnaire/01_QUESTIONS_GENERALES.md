# Questions Générales sur le Projet — Questionnaire Jury

> Ce fichier contient les questions générales que le jury peut poser sur votre projet.
> Chaque question est suivie d'une réponse détaillée, expliquée simplement.

---

## Q1 : Pouvez-vous nous présenter votre projet en quelques phrases ?

**Réponse :**
Notre projet s'appelle UniPresence. C'est une application web qui permet à une école ou une université de gérer automatiquement les présences des élèves grâce à la reconnaissance faciale. Au lieu de faire l'appel manuellement, la caméra identifie les visages des élèves et enregistre automatiquement qui est présent, qui est en retard, et qui est absent. Le système génère également des rapports et des statistiques de présence exportables vers Excel.

---

## Q2 : Quel est le problème concret que votre projet résout ?

**Réponse :**
Dans les écoles et universités, la gestion des présences est souvent manuelle : l'enseignant fait l'appel verbal, les élèves signent une feuille, ou on distribue des formulaires. Ces méthodes posent plusieurs problèmes :
- **Temps perdu** : l'appel prend 10 à 15 minutes par cours
- **Erreurs** : oubli d'un nom, confusion entre élèves aux noms similaires
- **Fraude** : un élève peut répondre pour un absent
- **Archivage difficile** : les feuilles papier se perdent ou se détériorent
- **Analyse impossible** : calculer les taux de présence sur plusieurs mois demande des heures

Notre système automatise tout cela et élimine ces problèmes.

---

## Q3 : À qui est destiné ce projet ? Qui sont les utilisateurs ?

**Réponse :**
Le projet cible deux types d'établissements :
1. **Les universités** : pour le suivi des présences aux cours (le professeur ouvre une session, les étudiants passent devant la caméra)
2. **Les écoles secondaires** : pour le contrôle d'entrée le matin (les élèves passent à l'entrée, leur arrivée est enregistrée automatiquement)

Les utilisateurs du système sont :
- Les **administrateurs** (directeurs, responsables informatiques) : gestion complète
- Les **enseignants** : consultation des présences de leurs cours
- Le **secrétariat** : gestion des élèves, modification des présences, export des rapports

---

## Q4 : Quelle est la différence entre votre projet et une feuille d'appel numérique classique ?

**Réponse :**
Une feuille d'appel numérique (type formulaire ou tableur) requiert encore une action humaine : quelqu'un doit cocher chaque nom manuellement. Notre système est **entièrement automatique** : la caméra reconnaît les visages et enregistre les présences sans aucune intervention humaine. La seule action manuelle possible est la correction d'erreurs ou l'ajout de justificatifs.

De plus, notre système offre :
- La **détection automatique des retards** (en comparant l'heure d'arrivée à l'horaire configuré)
- La **génération automatique des absences** en fin de journée
- Des **alertes** quand un élève accumule trop d'absences
- Un **audit complet** de toutes les modifications

---

## Q5 : Quelles sont les limites de votre projet ?

**Réponse :**
Honnêtement, voici les limites principales :

1. **Qualité de la reconnaissance** : L'algorithme LBPH est moins précis que les solutions Deep Learning (réseaux de neurones) utilisées par des entreprises comme Google ou Amazon. Il peut avoir des difficultés avec de mauvaises conditions d'éclairage ou si un élève a changé d'apparence (barbe, lunettes nouvelles).

2. **Nombre de photos nécessaire** : Pour que la reconnaissance soit fiable, il faut entre 5 et 15 photos par élève. C'est un travail initial important pour une grande école.

3. **Performance à grande échelle** : La base de données SQLite et le serveur Django ne sont pas conçus pour des milliers d'utilisateurs simultanés. Pour une très grande université, il faudrait migrer vers PostgreSQL et optimiser le serveur.

4. **Visages de profil** : L'algorithme Haar Cascade ne détecte que les visages de face. Si un élève passe de profil, il ne sera pas reconnu.

5. **Questions éthiques** : La reconnaissance faciale implique la collecte de données biométriques (les photos). Cela nécessite le consentement des élèves et des parents, conformément aux lois sur la protection des données.

---

## Q6 : Quels auraient été les autres approches possibles pour résoudre ce problème ?

**Réponse :**
Il existe d'autres approches pour automatiser la présence :
- **QR codes** : chaque élève scanne son QR code à l'entrée (mais peut être partagé entre élèves)
- **Cartes RFID** : chaque élève a une carte à passer sur un lecteur (mais la carte peut être prêtée)
- **Empreinte digitale** : haute précision, mais nécessite un lecteur d'empreinte pour chaque point d'entrée
- **Reconnaissance vocale** : l'élève dit son nom et le système le vérifie (peu pratique à grande échelle)
- **API de reconnaissance faciale cloud** (AWS Rekognition, Azure Face, Google Cloud Vision) : très précis mais coûteux et nécessite internet en permanence

Notre choix de la reconnaissance faciale locale (LBPH) offre un bon équilibre entre précision, coût zéro de licence, et fonctionnement sans connexion internet.

---

## Q7 : Combien de temps a pris le développement de ce projet ?

**Réponse :**
*(Cette réponse est personnelle — adaptez-la à votre situation réelle)*
Le projet a été développé en plusieurs phases :
- Phase de recherche et choix des technologies : [X semaines]
- Développement du module de reconnaissance faciale : [X semaines]
- Développement de l'interface web : [X semaines]
- Tests et corrections : [X semaines]
- Documentation : [X semaines]

---

## Q8 : Votre système peut-il être utilisé dans une école congolaise ? Quelles adaptations seraient nécessaires ?

**Réponse :**
Oui, le système est conçu avec la réalité africaine en tête. Plusieurs éléments le confirment :
- Le **fuseau horaire est Africa/Lubumbashi** (RDC)
- L'interface est entièrement en **français**
- Il fonctionne sur **SQLite** (pas besoin d'un serveur de base de données séparé)
- Il peut fonctionner en **réseau local** sans internet (sauf pour Replit)

Les adaptations nécessaires pour un déploiement réel :
- Un **PC serveur** (même modeste : 4 Go RAM, processeur dual-core) installé dans l'école
- Des **caméras** (webcam basique à 30-50$, ou caméra IP à 100-200$)
- Un **réseau local** si on veut plusieurs caméras (switch réseau simple)
- Formation du personnel (2-3 heures suffisent)

---

## Q9 : Comment votre système gère-t-il les pannes ou les coupures de courant ?

**Réponse :**
- **Coupure électrique** : Le serveur Django s'arrête. Quand il redémarre, toutes les données sont intactes car la base de données SQLite est un fichier durable. Le script `start.sh` reprend automatiquement les migrations et redémarre le serveur.
- **Panne réseau** : La webcam navigateur ne peut plus envoyer d'images. La présence peut être prise manuellement.
- **Panne de caméra** : Les présences peuvent être saisies manuellement depuis l'interface web.
- **Données corrompues** : Une sauvegarde régulière du fichier `db.sqlite3` permet de restaurer l'état précédent.

---

## Q10 : Ce système est-il déjà en production dans une vraie école ?

**Réponse :**
*(Adaptez selon votre situation réelle)*
Actuellement, le système est un prototype fonctionnel développé dans le cadre de [votre projet académique]. Il a été testé avec [N] élèves et les résultats de reconnaissance sont [satisfaisants / bons]. Pour un déploiement en production dans une vraie école, quelques étapes supplémentaires seraient nécessaires : tests à plus grande échelle, obtention des consentements, et éventuellement migration vers une base de données plus robuste.

---

*Voir aussi : `02_QUESTIONS_TECHNIQUE_IA.md` pour les questions sur l'intelligence artificielle et l'algorithme.*
