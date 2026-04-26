
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# =========================
# ⚙ CONFIG
# =========================

st.set_page_config(page_title="Carga de Archivos", layout="wide")

st.title("📂 Carga de Archivos de Actas")

# 🔴 PONER TU ID DE CARPETA COMPARTIDA
FOLDER_ID = "ACA_TU_ID_DE_DRIVE"

# 🔴 TU SHEET
SHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"

# =========================
# 🔐 CONEXIÓN GOOGLE
# =========================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet("Hoja 2")

drive_service = build("drive", "v3", credentials=creds)

# =========================
# 📅 DATOS ACTAS (igual que tu app)
# =========================

actas_dict = {
    187: "Febrero",
    188: "Marzo",
    189: "Abril",
    190: "Mayo",
    191: "Junio",
    192: "Julio",
    193: "Agosto",
    194: "Septiembre",
    195: "Octubre",
    196: "Noviembre",
    197: "Diciembre",
}

# =========================
# 📤 SUBIR ARCHIVO
# =========================

def subir_a_drive(archivo, nombre):

    media = MediaIoBaseUpload(
        io.BytesIO(archivo.read()),
        mimetype=archivo.type
    )

    file_metadata = {
        "name": nombre,
        "parents": [FOLDER_ID]
    }

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = file.get("id")

    link = f"https://drive.google.com/file/d/{file_id}/view"

    return link

# =========================
# 📝 FORM
# =========================

with st.form("form_archivo"):

    acta_label = st.selectbox(
        "Seleccionar Acta",
        options=[f"Acta {n} - {actas_dict[n]}" for n in actas_dict]
    )

    numero_acta = int(acta_label.split(" ")[1])

    tipo = st.selectbox("Tipo de archivo", [
        "Proyecto de Investigación",
        "Informe Final",
        "Informe de Avance",
        "Documentación",
        "Otro"
    ])

    titulo = st.text_input("Título / Referencia del archivo")

    archivo = st.file_uploader(
        "Subir archivo",
        type=["pdf", "docx"]
    )

    submit = st.form_submit_button("Subir archivo")

# =========================
# 💾 PROCESO
# =========================

if submit:

    if not archivo or not titulo:
        st.error("Faltan datos obligatorios")
    else:

        nombre_archivo = f"Acta_{numero_acta}_{titulo}_{datetime.now().strftime('%Y%m%d_%H%M')}"

        with st.spinner("Subiendo archivo a Drive..."):

            link = subir_a_drive(archivo, nombre_archivo)

        # Guardar en Sheets (solo lo necesario)
        fila = [
            numero_acta,
            "",  # fecha (opcional)
            "",  # año
            tipo,
            titulo,
            "", "", "", "", "", "", "", "", "",
            "", "", "", "",
            link  # 🔴 LINK ARCHIVO
        ]

        sheet.append_row(fila)

        st.success("Archivo subido y vinculado correctamente")

        st.markdown(f"[🔗 Ver archivo]({link})")
