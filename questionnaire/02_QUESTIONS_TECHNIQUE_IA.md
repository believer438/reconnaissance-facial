# Questions Techniques sur l'IA et la Reconnaissance Faciale — Questionnaire Jury

---

## Q1 : Expliquez-nous comment fonctionne la reconnaissance faciale dans votre système.

**Réponse :**
Notre système utilise l'algorithme **LBPH (Local Binary Pattern Histogram)**. Voici comment il fonctionne de façon simple :

**Phase d'apprentissage (entraînement) :**
1. On charge les photos de chaque élève
2. Chaque photo est convertie en niveaux de gris (noir et blanc)
3. On normalise l'éclairage (équialisation d'histogramme)
4. On détecte le visage dans la photo (algorithme Haar Cascade)
5. Pour chaque visage, on calcule une « empreinte numérique » : un vecteur de 256 nombres représentant les textures du visage
6. On associe cette empreinte à l'identifiant de l'élève
7. Le modèle est sauvegardé dans un fichier (trainer.yml)

**Phase de reconnaissance (en direct) :**
1. Une image est capturée (webcam ou photo uploadée)
2. On détecte les visages dans l'image
3. Pour chaque visage, on calcule son empreinte numérique
4. On compare cette empreinte avec toutes les empreintes connues
5. On retourne l'élève dont l'empreinte est la plus proche, si la distance est inférieure au seuil configuré

---

## Q2 : Qu'est-ce que LBPH ? Expliquez l'algorithme.

**Réponse :**
LBPH signifie **Local Binary Pattern Histogram** = Histogramme de Motifs Binaires Locaux.

**L (Local)** : On travaille localement, pixel par pixel, pas sur l'image entière à la fois.

**B (Binary Pattern) — Le motif binaire :**
Pour chaque pixel de l'image, on regarde ses 8 voisins qui l'entourent (comme les 8 cases autour d'une case d'échiquier). Pour chaque voisin, on pose la question : « Ce voisin est-il plus sombre (0) ou plus clair (1) que le pixel central ? ». On obtient 8 bits (0 ou 1), soit un nombre entre 0 et 255.

**H (Histogram) — L'histogramme :**
L'image est découpée en 64 petits carrés (grille 8×8). Pour chaque carré, on compte combien de pixels ont le code 0, le code 1, le code 180, etc. On obtient 64 histogrammes de 256 valeurs chacun.

**Le vecteur final :**
Les 64 histogrammes sont mis bout à bout → un grand vecteur de 64 × 256 = 16 384 valeurs. C'est la « signature » du visage.

**La comparaison :**
On mesure la distance chi-carré (χ²) entre la signature du visage inconnu et celles de tous les élèves connus. Plus la distance est petite, plus les visages sont similaires.

---

## Q3 : Pourquoi avez-vous choisi LBPH plutôt que Deep Learning ?

**Réponse :**
C'est une question de compromis. Voici notre raisonnement :

| Critère | LBPH | Deep Learning |
|---------|------|---------------|
| Données nécessaires | 5-15 photos/personne | Des milliers |
| Matériel | CPU standard | GPU puissant (souvent) |
| Précision | Bonne (70-90%) | Excellente (95-99%) |
| Expliquabilité | Mathématiquement compréhensible | « Boîte noire » |
| Coût | 0€ | Peut être élevé |
| Internet requis | Non | Non (si modèle local) |

Pour notre contexte (école, peu de photos par élève, PC standard, budget limité), LBPH est le choix rationnel. Le Deep Learning serait une amélioration future possible.

---

## Q4 : Qu'est-ce que le Haar Cascade ? Comment détecte-t-il les visages ?

**Réponse :**
Le Haar Cascade est un algorithme de **détection d'objets** dans une image, développé par Paul Viola et Michael Jones en 2001. Il est très efficace pour détecter les visages de face.

**Fonctionnement simplifié :**
L'algorithme utilise des « features Haar » — des filtres qui cherchent des patterns visuels caractéristiques d'un visage :
- Les yeux sont généralement plus sombres que les joues
- Le milieu du visage (nez) est souvent plus clair que les côtés
- La bouche a une ligne horizontale sombre

L'algorithme parcourt l'image avec une fenêtre de détection de différentes tailles, et pour chaque position, demande : « Cette zone ressemble-t-elle à un visage ? ». Il utilise une cascade de classificateurs de plus en plus stricts — si une zone échoue un test précoce, elle est immédiatement rejetée (d'où le mot « cascade »), ce qui rend l'algorithme très rapide.

**Limites :**
- Ne détecte que les visages de face (frontal)
- Peut avoir des faux positifs (objet ressemblant vaguement à un visage)
- Moins précis que les méthodes Deep Learning modernes

---

## Q5 : Qu'est-ce qu'un seuil de confiance ? Comment fonctionne-t-il ?

**Réponse :**
Le seuil de confiance est une valeur limite qui détermine si une correspondance est acceptée ou rejetée.

**La distance LBPH :**
Quand on compare le visage inconnu avec les visages connus, on obtient une distance (nombre). Plus la distance est petite, plus les visages sont similaires.

```
Distance 0    = correspondance parfaite (même photo exacte)
Distance 45   = bonne correspondance → élève reconnu
Distance 65   = correspondance douteuse → file de revue
Distance 90   = pas de correspondance → visage inconnu
```

**Les seuils configurables dans notre système :**
- **Seuil haute confiance** (défaut : 58) : en dessous → reconnaissance automatique, présence enregistrée
- **Seuil limite** (défaut : 75) : entre 58 et 75 → file de revue manuelle. Au-delà de 75 → inconnu

**Pourquoi deux seuils ?** Pour gérer l'incertitude. Mieux vaut mettre en doute et demander une vérification humaine plutôt que d'enregistrer une mauvaise présence.

**Conversion en score de confiance :**
Pour afficher un score compréhensible, on fait : Score = 100 - distance.
Donc distance 45 → score 55/100. Distance 20 → score 80/100.

---

## Q6 : Pourquoi utilisez-vous l'égalisation d'histogramme ? Qu'est-ce que c'est ?

**Réponse :**
**Le problème :** Un élève photographié le matin sous une lumière fluorescente sera différent du même élève photographié le soir. Les pixels seront différents, et l'algorithme pourrait ne pas le reconnaître.

**L'égalisation d'histogramme** est une technique qui redistribue les valeurs de luminosité d'une image de façon à utiliser toute la plage disponible (de 0 à 255). Résultat : quelle que soit la luminosité d'origine, l'image normalisée mettra en valeur les structures (contours, textures du visage) plutôt que la luminosité globale.

**Analogie :** C'est comme si vous régliez le « contraste automatique » d'une photo — l'image ressort mieux quel que soit l'éclairage d'origine.

**Point critique :** La même transformation est appliquée lors de l'entraînement ET lors de la reconnaissance. Si elles diffèrent, les résultats sont catastrophiques. C'est une source courante d'erreurs dans les projets de reconnaissance faciale.

---

## Q7 : Qu'est-ce que le Laplacian Variance et pourquoi l'utilisez-vous ?

**Réponse :**
Le Laplacien est un opérateur mathématique qui mesure les **variations rapides de luminosité** dans une image. En d'autres termes, il détecte les bords et les détails fins.

- Une image **nette** a beaucoup de bords francs → Laplacien élevé → variance élevée
- Une image **floue** a des bords doux → Laplacien faible → variance faible

Dans notre système, si `cv2.Laplacian(image).var() < 50`, la photo est considérée trop floue et est **ignorée** lors de l'entraînement. Entraîner l'IA avec des photos floues dégrade la qualité du modèle.

---

## Q8 : Qu'est-ce que l'augmentation de données (data augmentation) ? Pourquoi l'utilisez-vous ?

**Réponse :**
L'augmentation de données est une technique qui consiste à **créer artificiellement de nouveaux exemples** d'entraînement à partir des données existantes.

Dans notre cas, pour chaque photo d'élève, nous créons aussi une version **miroir horizontal** (retournée de gauche à droite). Résultat : 10 photos → 20 exemples d'entraînement.

**Pourquoi ?** Un élève peut se présenter légèrement tourné vers la gauche ou la droite. Si le modèle n'a été entraîné que sur des photos de face, il peut avoir du mal à reconnaître un visage légèrement tourné. En ajoutant les versions miroirs, on entraîne le modèle sur les deux orientations, le rendant plus robuste.

---

## Q9 : Comment fonctionne la file de revue ? Pourquoi est-elle importante ?

**Réponse :**
La file de revue est un mécanisme de sécurité pour les reconnaissances incertaines.

**Quand est-elle déclenchée ?** Quand la distance LBPH se situe dans la « zone de doute » : pas assez proche pour être automatiquement acceptée, pas assez loin pour être rejetée comme inconnu.

**Contenu d'un ticket de revue :**
- La photo du visage détecté
- Le nom proposé par l'IA
- Le score de confiance
- S'il y a un second candidat possible (MULTIPLE_MATCH)

**Décision administrative :**
- **Valider** : c'est bien cet élève → présence enregistrée rétroactivement
- **Rejeter** : ce n'est pas cet élève → aucune présence

**Pourquoi est-ce important ?** La règle d'or est : « Mieux vaut rater une présence (faux négatif) que d'enregistrer la présence du mauvais élève (faux positif). » Un faux positif crée un problème administratif grave : un élève absent est marqué présent.

---

## Q10 : Votre système peut-il reconnaître plusieurs visages simultanément ?

**Réponse :**
Oui. L'algorithme Haar Cascade peut détecter plusieurs visages dans une seule image. Pour chaque visage détecté, LBPH est appliqué indépendamment. Une photo de groupe peut donc produire plusieurs enregistrements de présence en une seule analyse.

Le résultat JSON retourné par l'API contient un tableau (liste) de résultats, un par visage :
```json
{
  "results": [
    { "name": "Bahati Joseph", "status": "recognized", "confidence": 87 },
    { "name": "Mukendi Marie", "status": "recognized", "confidence": 92 },
    { "name": "Inconnu",       "status": "unknown",    "confidence": 0  }
  ]
}
```

---

## Q11 : Comment votre système évite-t-il d'enregistrer la même présence deux fois ?

**Réponse :**
Le système vérifie **avant d'enregistrer** si cet élève a déjà une présence pour cette session (ou ce jour). Si oui, la présence n'est pas créée en double et la réponse contient `"already_marked": true`.

Pour la session de cours : vérification de `(student, course_session, status=present/late)`.
Pour la présence journalière : vérification de `(student, date)` → contrainte `unique_together` dans la base de données.

De plus, un **cooldown anti-doublon** est configurable (par défaut 5 minutes) : si le même élève est détecté plusieurs fois en moins de 5 minutes dans la même session, les détections suivantes sont ignorées.

---

## Q12 : Que se passe-t-il si deux élèves se ressemblent physiquement ?

**Réponse :**
C'est un cas difficile pour tout algorithme de reconnaissance. Voici comment notre système le gère :

1. Si les deux signatures LBPH sont proches, le système peut déclencher un statut `MULTIPLE_MATCH` (correspondance ambiguë)
2. Un ticket de revue est créé avec les deux candidats et leurs scores respectifs
3. Un administrateur humain fait la vérification manuelle

Pour minimiser ce risque :
- Ajouter plus de photos par élève (plus de variété)
- S'assurer que les photos sont de qualité (nettes, bien éclairées)
- Ajuster le seuil de confiance haute pour être plus strict

---

*Voir aussi : `03_QUESTIONS_BASE_DE_DONNEES.md` pour les questions sur la base de données.*
