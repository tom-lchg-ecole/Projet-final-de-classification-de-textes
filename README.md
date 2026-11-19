# Classification de textes

Interface Python avec Streamlit, en français. Elle permet de saisir un texte ou d'importer un fichier `.txt`, d'en consulter le contenu et de préparer la saisie.

Aucun modèle, API ou dataset n'est connecté. Le bouton « Préparer le texte » valide la saisie sans produire de prédiction. Les emplacements de la classe binaire et de sa probabilité restent vides. Le sens de 0 et 1 sera défini avec le dataset.

## Installation et lancement

Python 3.12 recommandé.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Déploiement sur Streamlit Community Cloud

Publier ces fichiers dans un dépôt GitHub, sélectionner ce dépôt dans Streamlit Community Cloud et choisir `app.py` comme point d'entrée. `requirements.txt` contient la dépendance nécessaire. Aucun secret n'est requis à cette étape.

## Saisie et import

- Le sélecteur détermine la source utilisée. Le texte saisi est conservé lors du passage à l'import.
- Fichiers `.txt` de 2 Mo maximum, en UTF-8 avec ou sans BOM, ou UTF-16 avec BOM.
- Limite de 100 000 caractères pour la saisie et l'import.
- Les fichiers vides, les données binaires et les encodages non reconnus affichent un message d'erreur.
- Aucun fichier importé n'est écrit sur disque par le code de l'application. Streamlit reçoit le fichier en mémoire pour l'afficher.

## Suite du projet

Brancher le modèle sur le texte de la source active, puis afficher la classe et la probabilité renvoyées. La connexion au modèle et l'entraînement sont hors du périmètre de cette interface.
