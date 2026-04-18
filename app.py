import streamlit as st
import io
import re
import pdfplumber
import gspread

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# -----------------------------
# CONFIG
# -----------------------------
FOLDER_ID = "13OCGBUo4SibDbZeMOVOOJ4Pj4OzrEcSa"
SPREADSHEET_ID = "17MiyW17W7oLlwSCKjDXCoA85CwBkYqHYhDKbIVN37c8"

st.set_page_config(page_title="Extractor de Actas", layout="wide")
st.title("📊 Extractor de Actas - Consejo de Investigación")

# -----------------------------
# CONEXIÓN GOOGLE
# -----------------------------
def conectar():

    scope = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    drive = build('drive', 'v3', credentials=creds)
    client = gspread.authorize(creds)

    sheet_actas = client.open_by_key(SPREADSHEET_ID).worksheet("Hoja 1")
    sheet_detalle = client.open_by_key(SPREADSHEET_ID).worksheet("Hoja 2")

    return drive, sheet_actas, sheet_detalle


# -----------------------------
# DRIVE
# -----------------------------
def listar_pdfs(drive):
    query = f"'{FOLDER_ID}' in parents and mimeType='application/pdf'"
    return drive.files().list(q=query).execute().get('files', [])


def descargar_pdf(drive, file_id):
    request = drive.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.seek(0)
    return fh


# -----------------------------
# PDF → TEXTO
# -----------------------------
def extraer_texto(pdf):
    texto = ""
    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            if page.extract_text():
                texto += page.extract_text() + "\n"
    return texto


# -----------------------------
# EXTRACCIÓN
# -----------------------------
def extraer_acta_info(texto):

    acta = re.search(r'ACTA\s*N[°º]?\s*(\d+)', texto, re.IGNORECASE)
    fecha = re.search(r'\d{1,2}/\d{1,2}/\d{4}', texto)

    acta = acta.group(1) if acta else ""
    fecha = fecha.group() if fecha else ""
    anio = fecha.split("/")[-1] if fecha else ""

    unidad = ""
    u = re.search(r'FACULTAD\s*[:\-]?\s*(.*)', texto, re.IGNORECASE)
    if u:
        unidad = u.group(1).strip()

    return acta, fecha, anio, unidad


def extraer_detalle(texto):

    filas = []

    for linea in texto.split("\n"):
        l = linea.upper()

        if "PROYECTO" in l:
            filas.append(("Proyecto", linea.strip()))

        elif "INFORME FINAL" in l:
            filas.append(("Informe Final", linea.strip()))

        elif "INFORME DE AVANCE" in l:
            filas.append(("Informe de Avance", linea.strip()))

        elif "CATEGORIZ" in l:
            filas.append(("Categorización", linea.strip()))

    return filas


# -----------------------------
# BOTÓN PRINCIPAL
# -----------------------------
if st.button("🚀 Procesar actas"):

    drive, sheet_actas, sheet_detalle = conectar()

    archivos = listar_pdfs(drive)

    actas_existentes = sheet_actas.col_values(1)

    nuevas = 0

    for f in archivos:

        pdf = descargar_pdf(drive, f['id'])
        texto = extraer_texto(pdf)

        acta, fecha, anio, unidad = extraer_acta_info(texto)

        if not acta or acta in actas_existentes:
            continue

        # HOJA ACTAS
        sheet_actas.append_row([acta, fecha, anio, unidad])

        # HOJA DETALLE
        detalles = extraer_detalle(texto)

        for tipo, descripcion in detalles:
            sheet_detalle.append_row([acta, fecha, anio, tipo, descripcion])

        nuevas += 1

    st.success(f"✅ {nuevas} actas procesadas correctamente")
