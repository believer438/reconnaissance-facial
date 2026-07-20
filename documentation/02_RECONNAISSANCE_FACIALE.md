# La Reconnaissance Faciale — Comment l'IA reconnaît les visages

## Introduction — Qu'est-ce que la reconnaissance faciale ?

La reconnaissance faciale, c'est la capacité d'un ordinateur à dire « ce visage appartient à Jean Dupont » en analysant une photo. L'ordinateur ne « voit » pas comme un humain — il voit des millions de nombres (les valeurs des pixels) et cherche des patterns (schémas) mathématiques.

---

## Étape 1 : La détection de visages (Haar Cascade)

Avant de reconnaître un visage, l'ordinateur doit d'abord **trouver où sont les visages** dans l'image. C'est le rôle de l'algorithme **Haar Cascade**.

### Comment fonctionne Haar Cascade ?

Imaginez que vous cherchez un visage dans une photo. Un humain regarde globalement. L'ordinateur, lui, procède différemment :

1. Il découpe l'image en une grille de petites zones
2. Pour chaque zone, il applique des filtres (des « questions ») :
   - « Est-ce que cette zone a une partie sombre en haut et claire en bas ? » (comme les yeux vs le nez)
   - « Est-ce que le centre est plus clair que les bords ? » (comme un visage éclairé)
3. Si une zone passe tous les filtres → c'est probablement un visage
4. Il marque la zone comme « visage détecté » avec ses coordonnées (x, y, largeur, hauteur)

### Paramètres utilisés dans le projet

```
scaleFactor = 1.1      → L'image est réduite de 10% à chaque passage (pour détecter les visages de toutes tailles)
minNeighbors = 5       → Un visage doit être confirmé par 5 zones voisines (réduit les faux positifs)
minSize = (80, 80)     → La plus petite taille de visage détectée (80x80 pixels)
```

**Pourquoi minSize = 80 ?** Un visage plus petit que 80x80 pixels est trop flou pour être reconnu avec fiabilité.

### Ce que fait le système après la détection

Pour chaque visage détecté, le système :
- Récupère la zone de l'image correspondant au visage
- Convertit en **niveaux de gris** (noir et blanc) — cela simplifie le calcul
- Passe à l'étape suivante : la reconnaissance

---

## Étape 2 : L'équialisation d'histogramme

Avant d'analyser le visage, le système applique une **égalisation d'histogramme**. Voici pourquoi :

### Le problème de l'éclairage

Imaginez un élève photographié le matin sous une lumière fluorescente. La même photo prise le soir sous une lampe orangée donnerait des pixels complètement différents. L'IA naïve penserait que c'est une autre personne.

### La solution : equalizeHist

L'égalisation d'histogramme **redistribue les valeurs des pixels** de façon à ce que toutes les plages de luminosité soient utilisées uniformément. Résultat : la structure du visage (forme du nez, des yeux, des joues) ressort mieux, indépendamment de l'éclairage.

**Analogie** : C'est comme si vous ajustiez le contraste d'une photo pour mieux voir les détails, quelle que soit la lumière d'origine.

**⚠️ Important** : Cette transformation est appliquée **à l'identique** pendant l'entraînement ET pendant la reconnaissance. Si elles diffèrent, les résultats s'effondrent.

---

## Étape 3 : L'algorithme LBPH — Le cœur de la reconnaissance

**LBPH** signifie **Local Binary Pattern Histogram** (Histogramme de Motifs Binaires Locaux).

### Explication simple

Imaginez que vous regardez un visage et que vous décrivez chaque petite zone : « ici, c'est une zone claire entourée de zones sombres », « là, c'est une transition du clair vers le sombre de gauche à droite »... C'est exactement ce que fait LBPH, mais en mathématiques.

### Étape par étape

**1. Pour chaque pixel, regarder ses voisins**

Pour chaque pixel de l'image, LBPH regarde les 8 pixels voisins qui l'entourent (comme les 8 cases autour d'une case d'échiquier). Pour chacun de ces voisins, on pose une question simple :
- Ce voisin est-il **plus sombre** que le pixel central ? → on note **0**
- Ce voisin est-il **plus clair** que le pixel central ? → on note **1**

On obtient ainsi 8 bits (0 ou 1) pour chaque pixel, soit un nombre entre 0 et 255.

**Exemple** : Si les 8 voisins sont tour à tour plus clairs, plus sombres, etc., on peut obtenir le code binaire `10110100`, qui vaut 180 en décimal.

**2. Découper l'image en grille**

L'image du visage est découpée en une grille de 8×8 = 64 cellules (petits carrés).

**3. Calculer un histogramme pour chaque cellule**

Pour chaque cellule, on compte combien de pixels ont le code 0, combien ont le code 1, combien ont le code 180, etc. On obtient un histogramme (diagramme à barres) de 256 valeurs pour chaque cellule.

**4. Assembler les histogrammes**

Les 64 histogrammes sont mis bout à bout pour former un grand vecteur (tableau de nombres). Ce vecteur est la « signature numérique » du visage — son empreinte digitale mathématique.

### Paramètres du projet

```python
cv2.face.LBPHFaceRecognizer_create(
    radius=2,      # Rayon : on regarde les voisins à 2 pixels de distance (pas juste le pixel immédiat)
    neighbors=8,   # On compare avec 8 voisins
    grid_x=8,      # 8 colonnes dans la grille
    grid_y=8,      # 8 lignes dans la grille
)
```

**Pourquoi radius=2 ?** Avec radius=1, on ne regarde que le pixel juste à côté, ce qui est trop sensible aux petits bruits (grain de la photo). Avec radius=2, on capture des structures plus larges du visage, plus robustes aux variations.

---

## Étape 4 : La comparaison — Reconnaître la personne

Pendant l'entraînement, le système a mémorisé la signature numérique de chaque élève. Pendant la reconnaissance, il :

1. Calcule la signature du visage inconnu
2. La compare avec **toutes les signatures connues** en base de données
3. Calcule la **distance** entre la signature inconnue et chaque signature connue

### C'est quoi une distance ici ?

La distance mesure à quel point deux signatures sont similaires. Plus la distance est petite, plus les visages sont similaires. La formule utilisée est la **distance chi-carré (χ²)**.

**Analogie** : C'est comme comparer deux mélodies. Plus elles se ressemblent, plus la distance entre elles est petite.

### Le seuil de décision

```
Distance 0         → Correspondance parfaite (même photo exacte)
Distance < 58      → RECONNU avec haute confiance → présence enregistrée automatiquement
Distance 58 à 75   → ZONE DE DOUTE → mis en file de revue manuelle
Distance > 75      → INCONNU → photo sauvegardée, présence non enregistrée
```

Ces seuils sont **configurables** par l'administrateur dans les paramètres du système.

### Conversion en score de confiance

Pour afficher un score compréhensible à l'utilisateur, la distance est convertie :

```
Score de confiance = 100 - distance
```

Donc une distance de 45 donne un score de 55/100. Un score de 95/100 signifie que la correspondance est quasi parfaite.

| Score affiché | Qualité |
|---------------|---------|
| 90-100 | Excellent — très haute certitude |
| 75-90 | Bon — match fiable |
| 60-75 | Acceptable — limite du seuil |
| < 60 | Non reconnu → « Inconnu » |

---

## L'entraînement — Comment le système apprend les visages

L'entraînement est le processus par lequel on « enseigne » au système à reconnaître chaque élève.

### Déroulement complet

```
Pour chaque élève actif dans le système :
    Pour chaque photo de cet élève :
        1. Charger la photo
        2. Convertir en niveaux de gris
        3. Égalisation d'histogramme (normaliser l'éclairage)
        4. Détecter le visage avec Haar Cascade
        5. Vérifier la netteté (score Laplacian)
           → Si la photo est trop floue : IGNORER cette photo
        6. Augmentation : créer une version miroir horizontale de la photo
           → Cela double le nombre d'exemples d'apprentissage
        7. Ajouter le visage à la liste d'entraînement avec l'identifiant de l'élève

Entraîner le modèle LBPH avec tous les visages collectés
Sauvegarder le modèle dans media/models/trainer.yml
Sauvegarder le dictionnaire des labels dans media/models/labels.json
Marquer toutes les photos comme « entraînées »
```

### La vérification de netteté (score Laplacian)

Le **Laplacien** est un calcul mathématique qui mesure les variations rapides de luminosité dans une image. Une image nette a beaucoup de transitions franches (bords bien définis) → Laplacien élevé. Une image floue a des transitions douces → Laplacien faible.

```
Score Laplacian < 50 → Photo trop floue → IGNORÉE
Score Laplacian ≥ 50 → Photo acceptable → UTILISÉE
```

### L'augmentation de données (data augmentation)

Pour rendre le modèle plus robuste, chaque photo est accompagnée de sa version **miroir horizontal** (retournée de gauche à droite). Pourquoi ? Parce qu'un élève peut se présenter légèrement tourné à gauche ou à droite. En lui montrant les deux orientations, le modèle apprend à reconnaître les deux.

---

## La file de revue — Gérer l'incertitude

Quand le système n'est pas sûr de lui (distance entre 58 et 75), il ne marque pas la présence automatiquement. Il crée un **ticket de revue** pour que l'administrateur puisse décider.

### Pourquoi cette précaution ?

**Règle d'or** : Mieux vaut rater une présence (faux négatif) que d'enregistrer la présence du mauvais élève (faux positif).

Un faux positif signifie qu'un élève absent est marqué comme présent — c'est une erreur administrative grave. Un faux négatif signifie qu'un élève présent n'est pas reconnu — l'enseignant peut corriger manuellement.

### Comment fonctionne la file de revue ?

1. Une reconnaissance incertaine → un ticket est créé avec : la photo du visage, le nom proposé par l'IA, le score de confiance
2. L'administrateur voit le ticket dans l'interface « File de revue »
3. Il peut :
   - **Valider** : confirmer que c'est bien cet élève → présence enregistrée
   - **Rejeter** : ce n'est pas cet élève → aucune présence

---

## Les visages inconnus

Quand un visage est détecté mais que la distance dépasse le seuil maximum, le système :
1. Sauvegarde une photo rognée du visage dans `media/unknown_faces/`
2. Crée un enregistrement dans `UnknownFaceLog`
3. Affiche le visage dans la galerie « Visages inconnus » de l'interface

Cela permet à l'administrateur de voir si des personnes non inscrites passent devant les caméras, ou si un élève n'a pas encore été enregistré dans le système.

---

## Les empreintes faciales (FaceEmbedding)

En plus du modèle LBPH complet, le système stocke les **vecteurs d'empreinte** de chaque photo individuellement dans la base de données. Chaque vecteur est un tableau de 256 nombres (les histogrammes LBPH). Cela permet :
- De voir combien d'empreintes chaque élève possède
- D'une future amélioration sans réentraîner complètement

---

## Limites de l'algorithme LBPH

LBPH est robuste mais a des limites :

| Situation | Impact |
|-----------|--------|
| Visage de profil | Haar Cascade ne détecte que les visages de face → non reconnu |
| Lunettes ou masque | Peut réduire le score de confiance → ajouter des photos avec accessoires |
| Éclairage très différent | Équialisation d'histogramme atténue mais ne résout pas tout |
| Trop peu de photos (1-2) | Modèle insuffisant → ajouter 5+ photos par élève |
| Mauvaise résolution | En dessous de 640×480, les détails du visage manquent |

---

## Comparaison avec d'autres approches

| Approche | Précision | Nécessite | Coût |
|----------|-----------|-----------|------|
| **LBPH (ce projet)** | Moyenne-Bonne | CPU seulement, local | Gratuit |
| Deep Learning (FaceNet, ArcFace) | Très haute | GPU puissant, données massives | Cher à entraîner |
| API cloud (AWS, Azure, Google) | Très haute | Internet + abonnement | Payant |
| Reconnaissance par empreinte | Bonne | Capteur dédié | Matériel spécifique |

**Le choix de LBPH est délibéré** : il fonctionne sans internet, sans GPU, sur un PC standard, et il est compréhensible mathématiquement — idéal pour un projet académique.

---

*Continuez avec `03_BASE_DE_DONNEES.md` pour comprendre comment les données sont organisées et stockées.*
