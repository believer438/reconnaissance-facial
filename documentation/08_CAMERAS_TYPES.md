# Les Caméras — Types, Fonctionnement et Déploiement

## Introduction

UniPresence supporte trois types de caméras très différents dans leur fonctionnement. Ce document explique chacun en détail, avec leurs avantages, inconvénients, et cas d'usage recommandés.

---

## Type 1 : Webcam Navigateur (Recommandé pour commencer)

### Comment ça fonctionne

C'est la solution la plus simple. La caméra ne communique pas directement avec le serveur Django — elle communique avec le navigateur de l'utilisateur.

```
Cycle de fonctionnement (toutes les X secondes) :

1. Le navigateur accède à la webcam du PC via l'API getUserMedia()
2. Le flux vidéo s'affiche dans un élément <video> de la page
3. Un script JavaScript capture une image du flux vidéo
4. L'image est convertie en base64 (format texte encodé)
5. L'image est envoyée au serveur via une requête HTTP POST (fetch)
6. Le serveur Django traite l'image avec OpenCV + LBPH
7. Le serveur retourne un JSON avec les résultats
8. Le JavaScript dessine des rectangles sur la vidéo en temps réel
```

### Ce qu'est le base64

Le base64 est une façon de convertir des données binaires (une image) en texte. Au lieu d'envoyer les octets bruts de l'image, on envoie une longue chaîne de caractères comme :
```
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcG...
```
C'est comme encoder l'image en Morse : le résultat est plus long, mais peut être transmis dans un simple champ texte.

### Avantages
- ✅ Fonctionne sur TOUT appareil avec webcam (PC, Mac, tablette, téléphone)
- ✅ Aucune configuration matérielle sur le serveur
- ✅ Fonctionne sur Replit (le serveur n'a pas accès à la caméra physique — c'est le navigateur qui s'en charge)
- ✅ Plusieurs professeurs peuvent utiliser leurs propres webcams simultanément
- ✅ Pas de câbles réseau supplémentaires

### Inconvénients
- ❌ Dépend de la qualité de la webcam du PC (variable selon le matériel)
- ❌ Un onglet navigateur doit rester ouvert pendant toute la session
- ❌ Non adapté pour surveiller automatiquement une entrée sans surveillance humaine

### Configuration
Dans l'interface, créer une caméra de type « Webcam navigateur », laisser le champ « Source » vide.

---

## Type 2 : Caméra USB

### Comment ça fonctionne

La caméra est physiquement branchée (câble USB) sur l'ordinateur qui héberge le serveur Django. OpenCV y accède directement avec `cv2.VideoCapture()`.

```
Caméra USB ──câble USB──► PC Serveur
                         │
                    cv2.VideoCapture(0)
                         │
                   Capture d'images
                         │
                   Pipeline LBPH
                         │
                   Stockage présences
```

### Le concept d'index

`cv2.VideoCapture(0)` ouvre la première caméra USB.  
`cv2.VideoCapture(1)` ouvre la deuxième caméra USB.

Si l'ordinateur a une webcam intégrée, elle est souvent l'index 0, et la première caméra USB branchée devient l'index 1.

### Avantages
- ✅ Qualité d'image généralement bonne
- ✅ Latence très faible (la caméra est sur la même machine)
- ✅ Fonctionne même sans réseau (en local)

### Inconvénients
- ❌ La caméra doit être physiquement branchée au serveur
- ❌ Distance limitée par la longueur du câble USB (typiquement 3-5 mètres)
- ❌ Non disponible sur Replit (le serveur Replit est dans le cloud, sans périphérique physique)
- ❌ Peu adapté pour plusieurs salles (faudrait un serveur par salle)

### Configuration
Dans l'interface, créer une caméra de type « USB », source = « 0 » pour la première, « 1 » pour la deuxième.

---

## Type 3 : Caméra IP / RTSP (Recommandé pour un vrai déploiement universitaire)

### Qu'est-ce qu'une caméra IP ?

Une caméra IP est une caméra qui se connecte au réseau (WiFi ou câble Ethernet) et diffuse son flux vidéo via le protocole réseau. Elle ressemble à une caméra de surveillance classique.

**Exemples de marques** : Hikvision, Dahua, Axis, Bosch, Hanwha.

### Qu'est-ce que RTSP ?

RTSP (Real Time Streaming Protocol) est le protocole utilisé par les caméras IP pour diffuser leur flux vidéo. C'est comme une « adresse URL » de la vidéo.

**Format typique d'une URL RTSP :**
```
rtsp://admin:password@192.168.1.10:554/Streaming/Channels/101
```
Décomposition :
- `rtsp://` : protocole
- `admin:password` : identifiants de la caméra
- `192.168.1.10` : adresse IP de la caméra sur le réseau local
- `:554` : port (port standard RTSP)
- `/Streaming/Channels/101` : chemin du flux (varie selon le fabricant)

### Comment ça fonctionne dans le système

```
Caméra IP ──WiFi/Ethernet──► Réseau local
                              │
                    cv2.VideoCapture("rtsp://...")
                              │
                         Django (serveur)
                              │
                        Pipeline LBPH
```

OpenCV se connecte à la caméra via l'URL RTSP et lit les images comme si c'était une vidéo locale.

### Architecture recommandée pour une université

```
Amphi A          Salle 101       Couloir          Entrée principale
[Cam IP]         [Cam IP]        [Cam IP]         [Cam IP]
192.168.1.10     192.168.1.11    192.168.1.12     192.168.1.13
    │                │               │                │
    └────────────────┴───────────────┴────────────────┘
                             │
                    Switch réseau de l'université
                             │
                    Serveur central
                    (PC puissant, 8-16 Go RAM)
                    Django + OpenCV + LBPH
                             │
                    Interface web accessib
                    depuis n'importe quel PC du réseau
```

### Avantages
- ✅ Distance illimitée (tout le réseau local de l'université)
- ✅ Pas de câble USB à tirer entre les salles et le serveur
- ✅ Dizaines de caméras simultanées possibles
- ✅ Caméras hautes définition disponibles
- ✅ Enregistrement vidéo intégré (certaines caméras)
- ✅ Caméras robustes (conçues pour fonctionner 24h/24)

### Inconvénients
- ❌ Coût matériel plus élevé (caméra IP + switch réseau)
- ❌ Configuration réseau nécessaire
- ❌ Le serveur doit être sur le même réseau que les caméras

---

## Modes de détection

Indépendamment du type de caméra, chaque caméra peut fonctionner dans l'un de ces modes :

### Mode RECOGNITION (Reconnaissance active)
- L'IA analyse chaque image
- Les présences sont enregistrées automatiquement
- Consomme plus de ressources CPU

### Mode MONITORING ONLY (Surveillance seulement)
- Le flux vidéo est affiché mais non analysé
- Utile pour surveiller sans enregistrer les présences (couloir, cantine...)
- Consomme moins de ressources

### Mode OFF (Désactivé)
- La caméra est marquée comme inactive
- N'est pas accessible depuis l'interface live

---

## Zones de caméra

### Zone CHECK-IN (Entrée école)
- Enregistre les arrivées des élèves
- Détermine le statut : « présent » ou « en retard » selon l'heure
- Utilisée pour la présence journalière (école secondaire)

### Zone MONITORING (Surveillance)
- Enregistre les présences en cours (mode université)
- Peut aussi être pure surveillance sans enregistrement

---

## Suivi de l'état des caméras

Le système maintient en temps réel l'état de chaque caméra :

| Information | Description |
|-------------|-------------|
| En ligne / Hors ligne | La caméra répond-elle ? |
| FPS estimé | Images par seconde analysées |
| Frames traitées | Total depuis le démarrage |
| Dernière erreur | Si la caméra a eu un problème |
| Dernier contact | Horodatage de la dernière image reçue |

Ces informations sont mises à jour automatiquement (« heartbeat »). Si une caméra ne répond plus pendant un certain temps, elle passe automatiquement en état « hors ligne ».

---

## Recommandation selon le contexte

| Contexte | Caméra recommandée | Raison |
|----------|--------------------|--------|
| Test / démonstration sur Replit | Webcam navigateur | Fonctionne sans configuration |
| Classe unique avec PC enseignant | Webcam navigateur | Simple et suffisant |
| École secondaire entrée principale | Caméra IP à l'entrée | Fixe, robuste, longue durée |
| Université multi-salles | Réseau de caméras IP | Scalable, centralisé |
| Salle sans internet | Caméra USB + serveur local | Fonctionne en réseau local |

---

*Documentation complète des fonctionnalités. Consultez le dossier `questionnaire/` pour vous préparer aux questions du jury.*
