import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Carga de Archivos", layout="wide")

st.title("📂 Carga de Archivos de Actas")

# 🔴 ID carpeta "Actas del Consejo"
ROOT_FOLDER_ID = "1PWQwpzkN8qixL-nDCuInosEL_jgUBpLh"  # la que mostraste en captura

# =========================
# GOOGLE
# =========================

scope = ["https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

drive_service = build("drive", "v3", credentials=creds)

# =========================
# FUNCIONES
# =========================

def obtener_subcarpetas(parent_id):
    resultados = drive_service.files().list(
        q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    return resultados.get("files", [])

def buscar_carpeta_por_nombre(parent_id, nombre_buscar):
    carpetas = obtener_subcarpetas(parent_id)
    for carpeta in carpetas:
        if carpeta["name"].strip() == nombre_buscar.strip():
            return carpeta["id"]
    return None

# =========================
# SELECT ACTA
# =========================

actas = [
    "Acta 187 - Febrero",
    "Acta 188 - Marzo",
    "Acta 189 - Abril",
    "Acta 190 - Mayo",
    "Acta 191 - Junio",
    "Acta 192 - Julio",
    "Acta 193 - Agosto",
    "Acta 194 - Septiembre",
    "Acta 195 - Octubre",
    "Acta 196 - Noviembre",
    "Acta 197 - Diciembre"
]

acta_seleccionada = st.selectbox("Seleccionar Acta", actas)

# =========================
# UPLOAD
# =========================

archivo = st.file_uploader("Subir archivo", type=["pdf", "docx"])

if archivo is not None:

    st.success("Archivo cargado")

    if st.button("Subir a carpeta correspondiente"):

        with st.spinner("Buscando carpeta..."):

            # 🔴 buscar carpeta dentro de ROOT
            carpeta_id = buscar_carpeta_por_nombre(ROOT_FOLDER_ID, acta_seleccionada)

        if not carpeta_id:
            st.error("No se encontró la carpeta en Drive. Revisar nombres.")
        else:

            with st.spinner("Subiendo archivo..."):

                media = MediaIoBaseUpload(
                    io.BytesIO(archivo.read()),
                    mimetype=archivo.type
                )

                file_metadata = {
                    "name": archivo.name,
                    "parents": [carpeta_id]
                }

                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id"
                ).execute()

                file_id = file.get("id")

                link = f"https://drive.google.com/file/d/{file_id}/view"

            st.success("Archivo subido correctamente")

            st.markdown(f"[🔗 Abrir archivo]({link})")
