"""Inférence locale avec le BiLSTM et le nettoyage du notebook."""

from pathlib import Path
import math
import re

import streamlit as st


MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "toxicity_bilstm.keras"
# Le seuil optimisé dans toxicity_metadata.json appartient à la régression logistique.
THRESHOLD = 0.5


def clean_message(text: str) -> str:
    text = re.sub(r"https?://\S+|www\.\S+", " URL ", text)
    text = re.sub(r"@\w+", " USER ", text)
    return re.sub(r"\s+", " ", text).strip()


@st.cache_resource(show_spinner=False)
def load_model():
    import tensorflow as tf

    return tf.keras.models.load_model(MODEL_PATH, compile=False)


def classify_text(text: str) -> dict:
    prepared = clean_message(text)
    if not prepared:
        raise ValueError("Saisissez un texte contenant au moins un mot.")

    model = load_model()
    import tensorflow as tf

    # Appel direct : aucun serveur, requête HTTP ou pipeline tf.data.
    score = float(model(tf.constant([[prepared]], dtype=tf.string), training=False).numpy()[0, 0])
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError("Le modèle a renvoyé un score invalide.")
    label = int(score >= THRESHOLD)
    return {
        "label": label,
        "category": "toxique" if label else "non toxique",
        "probability_toxic": score,
        "threshold": THRESHOLD,
    }
