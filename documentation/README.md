# Documentation UniPresence — Index général

Bienvenue dans la documentation complète du projet **UniPresence** — système de gestion des présences par reconnaissance faciale.

> **Pour qui ?** Ces fichiers sont rédigés pour une personne qui n'a jamais touché au code. Chaque concept est expliqué depuis la base, avec des analogies du quotidien.

---

## 📚 Fichiers de documentation

| Fichier | Contenu | Temps de lecture |
|---------|---------|-----------------|
| `00_VUE_ENSEMBLE.md` | Introduction générale, à quoi sert le projet, schéma global | 5 min |
| `01_ARCHITECTURE.md` | Comment les pièces s'assemblent, organisation des dossiers | 10 min |
| `02_RECONNAISSANCE_FACIALE.md` | L'IA : LBPH, Haar Cascade, entraînement, reconnaissance | 15 min |
| `03_BASE_DE_DONNEES.md` | Toutes les tables, leurs colonnes, leurs relations | 15 min |
| `04_FONCTIONNALITES.md` | Toutes les fonctionnalités de l'application (plus de 30) | 10 min |
| `05_TECHNOLOGIES.md` | Python, Django, OpenCV, SQLite — pourquoi ces choix | 10 min |
| `06_WORKFLOW_UTILISATION.md` | Guide pas à pas d'utilisation quotidienne | 10 min |
| `07_SECURITE_ROLES.md` | Sécurité, rôles utilisateurs, protection des données | 8 min |
| `08_CAMERAS_TYPES.md` | Webcam, USB, IP/RTSP — fonctionnement et déploiement | 8 min |

**Ordre de lecture recommandé :** `00` → `01` → `02` → `03` → les autres selon vos besoins.

---

## 🎓 Dossier questionnaire (préparation jury)

Le dossier `../questionnaire/` contient les questions-réponses pour votre présentation.

| Fichier | Questions sur |
|---------|--------------|
| `00_INDEX_QUESTIONNAIRE.md` | Guide général + top 10 questions + terminologie |
| `01_QUESTIONS_GENERALES.md` | Le projet, ses objectifs, ses limites |
| `02_QUESTIONS_TECHNIQUE_IA.md` | L'algorithme LBPH, la reconnaissance faciale |
| `03_QUESTIONS_BASE_DE_DONNEES.md` | SQLite, modèles, migrations, index |
| `04_QUESTIONS_CONCEPTION.md` | Architecture, sécurité, scalabilité |
| `05_QUESTIONS_ETHIQUE_JURIDIQUE.md` | Éthique, RGPD, consentement |
| `06_QUESTIONS_APPROFONDIES.md` | Questions très techniques pour jury expert |

---

## 🔑 Résumé en 5 points

1. **Quoi** : Application web Django qui reconnaît les visages des élèves pour enregistrer automatiquement les présences

2. **Comment** : Algorithme LBPH d'OpenCV — chaque visage est représenté par un vecteur mathématique de 256 nombres (histogrammes de textures locales)

3. **Où** : Données stockées localement dans SQLite, photos dans le dossier `media/`, modèle IA dans `media/models/trainer.yml`

4. **Qui** : Trois rôles (Admin, Enseignant, Secrétariat) avec des permissions différentes

5. **Deux modes** : Université (présence par cours/session) + École secondaire (présence journalière à l'entrée)

---

*Documentation créée le 18 juillet 2026 — UniPresence v2.0*
