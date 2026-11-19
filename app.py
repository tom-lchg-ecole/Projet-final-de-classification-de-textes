"""Interface Streamlit seule. Aucune prédiction ni connexion à un modèle."""

import streamlit as st

from live_text_area import live_text_area


MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TEXT_CHARS = 100_000


def decode_document(data: bytes) -> str:
    """Accepte UTF-8 et les fichiers UTF-16 portant une marque d'encodage."""
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("Le fichier dépasse 2 Mo. Choisissez un fichier plus petit.")
    try:
        encoding = "utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        text = data.decode(encoding)
    except UnicodeError as exc:
        raise ValueError("Encodage non reconnu. Enregistrez votre fichier en UTF-8 puis réessayez.") from exc
    if any(ord(char) < 32 and char not in "\n\r\t" for char in text):
        raise ValueError("Ce fichier contient des données non textuelles. Choisissez un fichier texte brut.")
    if not text.strip():
        raise ValueError("Le fichier est vide. Choisissez un fichier contenant du texte.")
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError("Le texte dépasse 100 000 caractères. Réduisez sa longueur puis réessayez.")
    return text


def main() -> None:
    st.set_page_config(page_title="Classification de textes", page_icon=":material/text_snippet:", layout="centered")

    st.title("À quelle catégorie appartient ce texte ?")
    st.write("Saisissez un texte ou importez un document pour préparer sa classification.")
    st.info("Le modèle n'est pas encore disponible. Aucune prédiction n'est effectuée pour le moment.", icon=":material/info:")

    source = st.radio("Comment souhaitez-vous ajouter votre texte ?", ["Saisir un texte", "Importer un fichier .txt"], horizontal=True)
    text = ""
    if source == "Saisir un texte":
        saved_text = st.session_state.get("saved_text", "")
        result = live_text_area(
            key="manual_text",
            data={"value": saved_text, "maxChars": MAX_TEXT_CHARS},
            default={"text": saved_text},
            on_text_change=lambda: None,
        )
        text = result.text
        st.session_state.saved_text = text
        st.caption(f"{len(text):,} caractères · {len(text.split()):,} mots".replace(",", " "))
    else:
        document = st.file_uploader("Choisir un document texte", type=["txt"], max_upload_size=2, help="Fichier .txt de 2 Mo maximum, encodé en UTF-8 ou UTF-16 avec marque d'encodage.")
        st.caption("Format .txt · 2 Mo maximum · 100 000 caractères maximum")
        if document is not None:
            if not document.name.lower().endswith(".txt"):
                st.error("Format non accepté. Choisissez un fichier .txt.")
            else:
                try:
                    text = decode_document(document.getvalue())
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.text_area("Aperçu du document", value=text, height=260, disabled=True)
                    st.caption(f"{len(text):,} caractères · {len(text.split()):,} mots".replace(",", " "))

    # L'action valide uniquement la saisie ; le modèle sera branché plus tard.
    if st.button("Préparer le texte", type="primary", disabled=not text.strip(), width="stretch"):
        st.success("Texte prêt. La classification sera disponible lorsque le modèle sera connecté.", icon=":material/check_circle:")

    st.divider()
    st.subheader("Résultat de la classification")
    st.caption("En attente du modèle")
    category, probability = st.columns(2)
    category.metric("Classe prédite", "—", help="Le modèle renverra 0 ou 1. Le sens des classes sera défini avec le jeu de données.")
    probability.metric("Probabilité associée", "—", help="Cette valeur sera fournie avec la prédiction du modèle.")
    st.caption("Les classes 0 et 1 seront définies une fois le jeu de données choisi.")


if __name__ == "__main__":
    main()
