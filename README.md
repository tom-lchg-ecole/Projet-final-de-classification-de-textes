# Classification de toxicité - chat League of Legends

Le projet comporte une interface Streamlit en français et un notebook de modélisation : [notebooks/analyse_et_modelisation_toxicite_lol.ipynb](notebooks/analyse_et_modelisation_toxicite_lol.ipynb). Le notebook charge `Juchen/league-toxicity-chat`, analyse les deux splits officiels et compare des modèles de classification, dont un BiLSTM.

L'application charge directement `artifacts/toxicity_bilstm.keras` avec TensorFlow et conserve le modèle en cache. Elle remplace les URL et mentions puis compacte les espaces, comme à l'entraînement. Le modèle contient sa propre vectorisation du texte. L'application affiche « toxique » lorsque le score atteint 0,5, le seuil utilisé pour évaluer le BiLSTM dans le notebook, sinon « non toxique ». Ce seuil n'a pas été optimisé pour ce modèle. Aucun service HTTP n'est nécessaire.

## Installation et lancement

Python 3.12 recommandé.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Les artefacts sont déjà présents : il n'est pas nécessaire de relancer l'entraînement pour utiliser l'application. Pour les régénérer, lancer `python -m jupyter lab`, puis ouvrir et exécuter intégralement `notebooks/analyse_et_modelisation_toxicite_lol.ipynb`. Il télécharge le dataset Hugging Face et produit les artefacts suivants :

- `artifacts/toxicity_bilstm.keras` : modèle BiLSTM utilisé par l'application, avec la vectorisation du texte brut intégrée ;
- `artifacts/toxicity_pipeline.joblib` et `artifacts/toxicity_metadata.json` : artefacts du modèle TF-IDF et du classifieur classique, non utilisés par l'interface BiLSTM.

Ne jamais charger un fichier `.joblib` provenant d'une source non fiable.

Le BiLSTM ne traite que les 16 premiers tokens après sa normalisation intégrée. Il a été entraîné sur des messages de chat liés à League of Legends. Ses résultats sur des phrases françaises générales ne sont pas établis.

## Déploiement sur Streamlit Community Cloud

Publier ces fichiers dans un dépôt GitHub, sélectionner ce dépôt dans Streamlit Community Cloud et choisir `app.py` comme point d'entrée. `requirements.txt` contient TensorFlow. Aucun secret n'est requis.

## Saisie et import

- Le sélecteur détermine la source utilisée. Le texte saisi est conservé lors du passage à l'import.
- Formats autorisés : `.docx`, `.txt` et `.md`, de 2 Mo maximum. Les autres extensions sont bloquées par le sélecteur et par la validation côté Python.
- Fichiers `.txt` et `.md` en UTF-8 avec ou sans BOM, ou UTF-16 avec BOM. Le Markdown est analysé comme du texte brut.
- Pour Word, extraction des paragraphes et du texte des tableaux du corps du document. Les fichiers `.docx` invalides sont rejetés ; la taille du XML décompressé est limitée à 20 Mo.
- Limite de 100 000 caractères pour la saisie et l'import.
- Les fichiers vides, les données binaires et les encodages non reconnus affichent un message d'erreur.
- Aucun fichier importé n'est écrit sur disque par le code de l'application. Streamlit reçoit le fichier en mémoire pour l'afficher.

La classification se lance avec le bouton de l'interface. Une saisie ou un document importé est traité comme un seul texte et donne une seule prédiction.
