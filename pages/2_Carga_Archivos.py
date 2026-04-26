import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# =========================
# ⚙ CONFIG
# =========================

st.set_page_config(page_title="Carga de Archivos", layout="wide")

st.title("📂 Carga de Archivos de Actas")

st.markdown("Suba el archivo correspondiente al acta")

# =========================
# 🔐 CONEXIÓN GOOGLE DRIVE
# =========================

scope = [
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

drive_service = build("drive", "v3", credentials=creds)

# 🔴 TU CARPETA
FOLDER_ID = "1ExWjGHYBgILVKA2-nd6voRZUajm-zeOL"

# =========================
# 📤 SUBIDA DE ARCHIVO
# =========================

archivo = st.file_uploader(
    "Seleccionar archivo",
    type=["pdf", "docx"]
)

if archivo is not None:

    st.success("Archivo cargado correctamente")

    st.write("Nombre:", archivo.name)
    st.write("Tipo:", archivo.type)
    st.write("Tamaño (KB):", round(len(archivo.getvalue()) / 1024, 2))

    if st.button("⬆ Subir a Google Drive"):

        with st.spinner("Subiendo archivo..."):

            media = MediaIoBaseUpload(
                io.BytesIO(archivo.read()),
                mimetype=archivo.type
            )

            file_metadata = {
                "name": archivo.name,
                "parents": [FOLDER_ID]
            }

            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

            file_id = file.get("id")

            link = f"https://drive.google.com/file/d/{file_id}/view"

        st.success("Archivo subido correctamente a Drive")

        st.markdown(f"🔗 [Abrir archivo en Drive]({link})")
