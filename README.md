# Classification de toxicité - chat League of Legends

Le projet comporte déjà une interface Streamlit en français et un notebook de modélisation : [notebooks/analyse_et_modelisation_toxicite_lol.ipynb](notebooks/analyse_et_modelisation_toxicite_lol.ipynb). Le notebook charge `Juchen/league-toxicity-chat`, analyse les deux splits officiels, compare des modèles ML et un BiLSTM, puis exporte le meilleur pipeline ML et ses métadonnées pour l'API.

L'interface est volontairement encore découplée du modèle : elle reste utilisable pour saisir ou importer un texte sans demander le téléchargement des bibliothèques ML. Le notebook est la source de vérité pour le prétraitement et la convention de classes.

## Installation et lancement

Python 3.12 recommandé.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyter lab
python -m streamlit run app.py
```

Dans Jupyter, ouvrir et exécuter intégralement `notebooks/analyse_et_modelisation_toxicite_lol.ipynb`. Il télécharge le dataset Hugging Face et écrit ensuite :

- `artifacts/toxicity_pipeline.joblib` : pipeline TF-IDF + classifieur, prêt à charger côté API ;
- `artifacts/toxicity_metadata.json` : seuil retenu, métriques et libellés.
- `artifacts/toxicity_bilstm.keras` : modèle BiLSTM complet, incluant la vectorisation du texte brut.

Ne jamais charger un fichier `.joblib` provenant d'une source non fiable.

## Déploiement sur Streamlit Community Cloud

Publier ces fichiers dans un dépôt GitHub, sélectionner ce dépôt dans Streamlit Community Cloud et choisir `app.py` comme point d'entrée. `requirements.txt` contient la dépendance nécessaire. Aucun secret n'est requis à cette étape.

## Saisie et import

- Le sélecteur détermine la source utilisée. Le texte saisi est conservé lors du passage à l'import.
- Fichiers `.txt` de 2 Mo maximum, en UTF-8 avec ou sans BOM, ou UTF-16 avec BOM.
- Limite de 100 000 caractères pour la saisie et l'import.
- Les fichiers vides, les données binaires et les encodages non reconnus affichent un message d'erreur.
- Aucun fichier importé n'est écrit sur disque par le code de l'application. Streamlit reçoit le fichier en mémoire pour l'afficher.

## Contrat prévu avec l'API

L'API reçoit un objet contenant `message` et renvoie `label`, `category`, `probability_toxic` et `threshold`. Le `label` vaut `1` si la probabilité est au moins égale au seuil choisi dans le notebook; `category` vaut alors `toxique`, sinon `non toxique`. Pour un import `.txt`, une ligne non vide correspond à un message à classifier.

La future connexion de l'interface doit appeler cette API, et non réimplémenter TF-IDF ou le seuil dans `app.py`.
