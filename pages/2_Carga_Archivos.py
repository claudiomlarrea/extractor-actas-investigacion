import streamlit as st
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Carga de Archivos", layout="wide")
st.title("📂 Carga de Archivos de Actas")

ROOT_FOLDER_ID = "13GUJ-wDQSjGiRKTO9ufiuVZjjhIZyakX"  # carpeta 2026

# =========================
# GOOGLE AUTH
# =========================

scope = [
    "https://www.googleapis.com/auth/drive"
]

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
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    return resultados.get("files", [])


def normalizar(texto):
    return texto.lower().replace(" ", "").replace("-", "")


def buscar_carpeta(parent_id, nombre):
    carpetas = obtener_subcarpetas(parent_id)

    nombre_norm = normalizar(nombre)

    for c in carpetas:
        if normalizar(c["name"]) == nombre_norm:
            return c["id"]

    return None

# =========================
# ACTAS
# =========================

actas = [
    "Acta 190 - Mayo",
    "Acta 191 - Junio",
    "Acta 192 - Julio",
    "Acta 193 - Agosto",
    "Acta 194 - Septiembre",
    "Acta 195 - Octubre",
    "Acta 196 - Noviembre",
    "Acta 197 - Diciembre"
]

acta = st.selectbox("Seleccionar Acta", actas)

# =========================
# SUBIDA
# =========================

archivo = st.file_uploader("Subir archivo", type=["pdf", "docx"])

if archivo is not None:

    st.success("Archivo cargado")

    if st.button("Subir archivo a carpeta correspondiente"):

        with st.spinner("Buscando carpeta..."):
            carpeta_id = buscar_carpeta(ROOT_FOLDER_ID, acta)

        if not carpeta_id:
            st.error("❌ No se encontró la carpeta")
            st.write("Carpetas detectadas:", obtener_subcarpetas(ROOT_FOLDER_ID))

        else:
            try:
                with st.spinner("Subiendo archivo..."):

                    file_bytes = archivo.getvalue()

                    media = MediaIoBaseUpload(
                        io.BytesIO(file_bytes),
                        mimetype=archivo.type,
                        resumable=True
                    )

                    file_metadata = {
                        "name": archivo.name,
                        "parents": [carpeta_id]
                    }

                    file = drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields="id",
                        supportsAllDrives=True
                    ).execute()

                    file_id = file.get("id")

                    link = f"https://drive.google.com/file/d/{file_id}/view"

                st.success("✅ Archivo subido correctamente")
                st.markdown(f"🔗 [Abrir archivo]({link})")

            except HttpError as e:
                st.error("❌ Error al subir archivo")
                st.text(str(e))
if st.button("Crear carpeta test en Drive"):

    folder_metadata = {
        "name": "TEST_ACTAS",
        "mimeType": "application/vnd.google-apps.folder"
    }

    folder = drive_service.files().create(
        body=folder_metadata,
        fields="id",
        supportsAllDrives=True
    ).execute()

    st.success(f"Carpeta creada: {folder.get('id')}")
