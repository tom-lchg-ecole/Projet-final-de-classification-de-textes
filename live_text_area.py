"""Champ multiligne qui transmet les modifications sans attendre la perte de focus."""

import streamlit as st


live_text_area = st.components.v2.component(
    "live_text_area",
    html='<label for="text">Votre texte</label><textarea id="text"></textarea>',
    css="""
        label { display: block; margin-bottom: .5rem; font-size: .875rem; }
        textarea {
            box-sizing: border-box; width: 100%; height: 260px; padding: .75rem;
            font: inherit; color: var(--st-text-color, #172A42);
            background: var(--st-secondary-background-color, #F2F5F9);
            border: 1px solid transparent; border-radius: .5rem; resize: vertical;
        }
        textarea:focus { outline: 2px solid var(--st-primary-color, #2459A6); }
    """,
    js="""
        export default function({ parentElement, data, setStateValue }) {
            const field = parentElement.querySelector('textarea');
            // Un rerun ne doit pas écraser les caractères déjà saisis côté navigateur.
            if (!field.dataset.initialized) {
                field.value = data.value;
                field.dataset.initialized = 'true';
            }
            field.maxLength = data.maxChars;
            field.placeholder = 'Écrivez ou collez votre texte ici…';
            const update = (event) => {
                if (!event.isComposing) setStateValue('text', field.value);
            };
            field.addEventListener('input', update);
            field.addEventListener('compositionend', update);
            return () => {
                field.removeEventListener('input', update);
                field.removeEventListener('compositionend', update);
            };
        }
    """,
)
