# UniPresence — Vue d'ensemble du projet

## Qu'est-ce que ce projet ?

**UniPresence** est une application web qui permet à une école ou une université de gérer automatiquement les présences des élèves grâce à la **reconnaissance faciale**.

Au lieu de faire l'appel à la main (l'enseignant dit chaque nom, les élèves répondent « présent »), la caméra regarde les visages des élèves et le système enregistre automatiquement qui est présent, qui est en retard, et qui est absent.

---

## Quel problème résout-il ?

Dans une école classique :
- L'appel prend du temps (parfois 10-15 minutes par séance)
- Des erreurs se glissent facilement (oubli d'un nom, confusion entre deux élèves)
- Les feuilles de présence papier se perdent ou sont mal archivées
- Analyser les taux de présence sur plusieurs mois demande beaucoup de travail manuel

**UniPresence** automatise tout cela :
- La présence est enregistrée en quelques secondes dès que l'élève passe devant la caméra
- Les données sont sauvegardées automatiquement dans une base de données
- On peut générer des rapports et des statistiques en un clic

---

## Pour qui est-il conçu ?

- **Les écoles secondaires** (lycées, collèges) pour le contrôle d'entrée chaque matin
- **Les universités** pour suivre les présences aux cours

Le système peut gérer les deux modes simultanément.

---

## Comment ça marche en résumé ?

```
Étape 1 : PRÉPARER
   → Enregistrer les élèves dans le système
   → Prendre plusieurs photos de chaque élève
   → « Entraîner » l'intelligence artificielle avec ces photos

Étape 2 : UTILISER CHAQUE JOUR
   → Un élève passe devant la caméra
   → Le système reconnaît son visage en quelques millisecondes
   → Sa présence est enregistrée automatiquement

Étape 3 : CONSULTER LES RÉSULTATS
   → Voir qui est présent/absent aujourd'hui
   → Générer des rapports sur plusieurs semaines ou mois
   → Exporter les données vers Excel (fichier CSV)
```

---

## Qui peut utiliser le système ?

Le système a trois types d'utilisateurs avec des droits différents :

| Rôle | Qui c'est | Ce qu'il peut faire |
|------|-----------|---------------------|
| **Administrateur** | Directeur, responsable informatique | Tout : configurer le système, entraîner l'IA, gérer les utilisateurs |
| **Enseignant** | Professeur | Consulter les présences de ses cours |
| **Secrétariat** | Agent administratif | Gérer les élèves, modifier les présences, exporter les rapports |

---

## Ce que le système NE fait PAS

- Il ne stocke **pas** les photos des élèves sur un serveur distant (tout reste local)
- Il ne fait **pas** de reconnaissance en temps réel sur de longues vidéos (il analyse des images ponctuelles)
- Il ne remplace **pas** un système de vidéosurveillance (ce n'est pas son but)
- Il ne transmet **pas** les données à l'extérieur (pas de cloud, pas d'internet requis pour fonctionner)

---

## Chiffres clés du projet

- **Langage principal** : Python (Django)
- **Algorithme IA** : LBPH (Local Binary Pattern Histogram) via OpenCV
- **Base de données** : SQLite (fichier local)
- **Interface** : Web (accessible depuis n'importe quel navigateur)
- **Caméras supportées** : Webcam du navigateur, caméra USB, caméra IP/réseau (RTSP)
- **Précision** : Bonne si 5-15 photos par élève, sous bonne lumière

---

## Schéma simplifié du système

```
┌────────────────────────────────────────────────────────────┐
│                        NAVIGATEUR WEB                      │
│   (PC du professeur, tablette, téléphone)                  │
│                                                            │
│   ┌─────────────┐    ┌─────────────┐    ┌──────────────┐  │
│   │   Tableau   │    │  Gestion    │    │   Caméra     │  │
│   │  de bord    │    │  élèves     │    │   en direct  │  │
│   └─────────────┘    └─────────────┘    └──────────────┘  │
└───────────────────────────┬────────────────────────────────┘
                            │ Internet / Réseau local
                            ▼
┌────────────────────────────────────────────────────────────┐
│                    SERVEUR DJANGO                           │
│                                                            │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐  │
│  │  Logique    │   │  Moteur IA  │   │  Base de données │  │
│  │  métier     │   │  (LBPH)     │   │  (SQLite)        │  │
│  └─────────────┘   └─────────────┘   └─────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

*Ce document est la première lecture recommandée. Continuez avec `01_ARCHITECTURE.md` pour comprendre comment les pièces s'assemblent.*
