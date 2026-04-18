import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io
from PyPDF2 import PdfReader

# =========================
# CONFIGURACIÓN
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"
FOLDER_ID = "1ExWjGHYBgILVKA2-nd6voRZUajm-zeOL"

# =========================
# CONEXIÓN
# =========================

def conectar():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    drive_service = build("drive", "v3", credentials=creds)

    sheet = client.open_by_key(SPREADSHEET_ID)
    sheet_actas = sheet.worksheet("Hoja 1")
    sheet_detalle = sheet.worksheet("Hoja 2")

    return drive_service, sheet_actas, sheet_detalle

# =========================
# LISTAR PDFs EN DRIVE
# =========================

def listar_pdfs(drive):
    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf'",
        fields="files(id, name)"
    ).execute()

    return results.get("files", [])

# =========================
# DESCARGAR PDF
# =========================

def descargar_pdf(drive, file_id):
    request = drive.files().get_media(fileId=file_id)
    file = io.BytesIO(request.execute())
    return file

# =========================
# EXTRAER TEXTO PDF
# =========================

def extraer_texto(pdf_file):
    reader = PdfReader(pdf_file)
    texto = ""

    for page in reader.pages:
        texto += page.extract_text() or ""

    return texto

# =========================
# PROCESAR ACTAS
# =========================

def procesar_actas():
    drive, sheet_actas, sheet_detalle = conectar()

    st.success("✅ Conexión exitosa")

    archivos = listar_pdfs(drive)

    if not archivos:
        st.warning("⚠️ No hay PDFs en la carpeta")
        return

    st.subheader("📂 PDFs encontrados")
    for f in archivos:
        st.write(f["name"])

    for archivo in archivos:
        try:
            pdf = descargar_pdf(drive, archivo["id"])
            texto = extraer_texto(pdf)

            # 🔥 ACÁ después metemos IA / regex avanzada
            acta = "Detectar"
            fecha = "Detectar"
            año = "Detectar"

            # Guardar resumen
            sheet_actas.append_row([
                acta,
                fecha,
                año,
                archivo["name"]
            ])

            # Guardar detalle
            sheet_detalle.append_row([
                archivo["name"],
                texto[:500]  # preview
            ])

        except Exception as e:
            st.error(f"Error procesando {archivo['name']}")
            st.exception(e)

    st.success("🚀 Procesamiento terminado")

# =========================
# UI
# =========================

st.set_page_config(layout="wide")

st.title("📊 Extractor de Actas - Consejo de Investigación")

if st.button("🚀 Procesar actas"):
    procesar_actas()
