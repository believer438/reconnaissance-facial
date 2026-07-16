# Système local de présence par reconnaissance faciale

Application Django locale avec:

- interface web simple et professionnelle
- base SQLite locale
- entrainement LBPH avec OpenCV
- reconnaissance par webcam
- aucune utilisation de `face_recognition`

## Lancement rapide

1. Créer ou activer l'environnement virtuel
2. Installer les dépendances

```bash
pip install -r requirements.txt
```

3. Lancer l'application

```bash
python launch.py
```

Cette commande:

- applique les migrations
- initialise quelques horaires par defaut
- demarre Django sur `http://127.0.0.1:8000/`

## Flux recommande

1. Ajouter un eleve depuis le tableau de bord
2. Importer plusieurs photos nettes du visage
3. Cliquer sur `Entrainer le modele`
4. Cliquer sur `Lancer la reconnaissance`
5. Regarder la webcam locale et fermer avec `Echap`

## Structure

```text
reconnaissance_facial/
|-- apps/
|   `-- attendance/
|       |-- management/
|       |-- services/
|       |-- models.py
|       |-- views.py
|       `-- urls.py
|-- config/
|-- media/
|-- static/
|-- templates/
|-- launch.py
|-- manage.py
`-- requirements.txt
```

## Notes techniques

- Le modele est sauvegarde dans `media/models/`
- Les photos d'entrainement sont sauvegardees dans `media/students/`
- Les presences sont enregistrees dans `db.sqlite3`
- Pour la partie webcam, la machine qui lance Django doit avoir acces a la camera locale
