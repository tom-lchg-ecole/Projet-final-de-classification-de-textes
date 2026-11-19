"""Classification de toxicité avec le BiLSTM chargé localement."""

import logging
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile
import streamlit as st

from live_text_area import live_text_area
from toxicity_model import classify_text


MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TEXT_CHARS = 100_000
ALLOWED_EXTENSIONS = {".docx", ".txt", ".md"}


def decode_document(data: bytes, filename: str = "document.txt") -> str:
    """Extrait le texte des formats autorisés et valide leur contenu."""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Format non accepté. Choisissez un fichier .docx, .txt ou .md.")
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("Le fichier dépasse 2 Mo. Choisissez un fichier plus petit.")
    if extension == ".docx":
        try:
            with ZipFile(BytesIO(data)) as archive:
                # Limite aussi la taille décompressée avant de lire le document XML.
                if archive.getinfo("word/document.xml").file_size > 20 * 1024 * 1024:
                    raise ValueError("Le contenu Word décompressé dépasse 20 Mo. Réduisez le document.")
                root = ElementTree.fromstring(archive.read("word/document.xml"))
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            if root.tag != f'{{{ns["w"]}}}document':
                raise ValueError("Le fichier .docx ne contient pas un document Word valide.")
            paragraphs = []
            for paragraph in root.findall(".//w:body//w:p", ns):
                parts = []
                for node in paragraph.iter():
                    if node.tag == f'{{{ns["w"]}}}t':
                        parts.append(node.text or "")
                    elif node.tag == f'{{{ns["w"]}}}tab':
                        parts.append("\t")
                    elif node.tag in {f'{{{ns["w"]}}}br', f'{{{ns["w"]}}}cr'}:
                        parts.append("\n")
                paragraphs.append("".join(parts))
            text = "\n".join(paragraphs)
        except (BadZipFile, KeyError, ElementTree.ParseError, RuntimeError, NotImplementedError) as exc:
            raise ValueError("Fichier .docx invalide ou illisible. Exportez-le à nouveau depuis Word.") from exc
    else:
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

    st.title("Ce texte est-il toxique ?")
    st.write("Saisissez une phrase ou importez un texte, puis lancez sa classification.")
    st.caption("Modèle BiLSTM entraîné sur des messages de chat League of Legends. Ses résultats ne sont pas validés pour le français généraliste.")

    source = st.radio("Comment souhaitez-vous ajouter votre texte ?", ["Saisir un texte", "Importer un fichier"], horizontal=True)
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
        document = st.file_uploader("Choisir un document", type=["docx", "txt", "md"], max_upload_size=2, help="Formats .docx, .txt et .md uniquement, de 2 Mo maximum. Les fichiers texte doivent être encodés en UTF-8 ou UTF-16 avec marque d'encodage.")
        st.caption("Formats .docx, .txt, .md · 2 Mo maximum · 100 000 caractères maximum")
        if document is not None:
            try:
                text = decode_document(document.getvalue(), document.name)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.text_area("Aperçu du document", value=text, height=260, disabled=True)
                st.caption(f"{len(text):,} caractères · {len(text.split()):,} mots".replace(",", " "))

    # Une modification ou un changement de source invalide l'ancien résultat.
    current_input = (source, text)
    if st.session_state.get("classified_input") != current_input:
        st.session_state.pop("classification", None)

    st.caption("Le modèle utilise uniquement les 16 premiers tokens après normalisation. Un fichier importé est traité comme un seul texte.")
    if st.button("Classifier le texte", type="primary", disabled=not text.strip(), width="stretch"):
        st.session_state.pop("classification", None)
        try:
            with st.spinner("Analyse du texte…"):
                result = classify_text(text)
        except ModuleNotFoundError:
            st.error("Une dépendance du modèle manque. Installez les dépendances indiquées dans requirements.txt.")
        except FileNotFoundError:
            st.error("Modèle introuvable. Placez toxicity_bilstm.keras dans le dossier artifacts.")
        except Exception:
            logging.getLogger(__name__).exception("Échec de la classification BiLSTM")
            st.error("La classification a échoué. Vérifiez le modèle et la compatibilité de TensorFlow dans les journaux de l'application.")
        else:
            st.session_state.classification = result
            st.session_state.classified_input = current_input

    st.divider()
    st.subheader("Résultat de la classification")
    result = st.session_state.get("classification")
    if result is None:
        st.caption("Saisissez un texte, puis cliquez sur « Classifier le texte ».")
    category, probability = st.columns(2)
    category.metric("Classe prédite", result["category"].capitalize() if result else "—")
    probability.metric("Score de toxicité", f'{result["probability_toxic"]:.1%}' if result else "—", help="Score produit par le modèle, et non une certitude sur le caractère toxique du texte.")
    st.caption("Seuil de décision : 50 %. Classe 1 : toxique · Classe 0 : non toxique.")


if __name__ == "__main__":
    main()
