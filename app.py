import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from PyPDF2 import PdfReader
import io
import re

# =========================
# CONFIG
# =========================
SPREADSHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"
FOLDER_ID = "1v1UPHiDF3eimPdCfaGGueKWg9M8jzdMJ"

# =========================
# AUTENTICACIÓN
# =========================
def conectar():
    creds_dict = st.secrets["gcp_service_account"]

    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    # Google Sheets
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)

    sheet_actas = sheet.worksheet("Hoja 1")
    sheet_detalle = sheet.worksheet("Hoja 2")

    # Google Drive
    drive = build("drive", "v3", credentials=creds)

    return drive, sheet_actas, sheet_detalle

# =========================
# EXTRAER TEXTO PDF
# =========================
def extraer_texto_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    return texto

# =========================
# LIMPIEZA TEXTO
# =========================
def limpiar_texto(texto):
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

# =========================
# EXTRACCIÓN INTELIGENTE
# =========================
def extraer_datos(texto):
    datos = {}

    # ACTA
    match_acta = re.search(r'ACTA\s*N[º°]\s*(\d+)', texto, re.IGNORECASE)
    datos["acta"] = match_acta.group(1) if match_acta else "Detectar"

    # FECHA (ej: "15 días del mes de abril de 2025")
    match_fecha = re.search(
        r'(\d{1,2}).*?mes.*?([a-zA-Z]+).*?(\d{4})',
        texto,
        re.IGNORECASE
    )

    if match_fecha:
        dia = match_fecha.group(1)
        mes = match_fecha.group(2)
        anio = match_fecha.group(3)
        datos["fecha"] = f"{dia} {mes} {anio}"
        datos["anio"] = anio
    else:
        datos["fecha"] = "Detectar"
        datos["anio"] = "Detectar"

    # UNIDAD ACADÉMICA
    if "Facultad" in texto:
        datos["unidad"] = "Facultad"
    else:
        datos["unidad"] = "Detectar"

    # TIPO (clasificación)
    if "Proyecto" in texto:
        datos["tipo"] = "Proyecto"
    elif "Informe final" in texto:
        datos["tipo"] = "Informe final"
    elif "Informe de avance" in texto:
        datos["tipo"] = "Informe de avance"
    else:
        datos["tipo"] = "Otro"

    # DIRECTOR (básico)
    match_dir = re.search(r'Director[:\s]+([A-Za-z\s]+)', texto)
    datos["director"] = match_dir.group(1).strip() if match_dir else "No detectado"

    return datos

# =========================
# PROCESAMIENTO
# =========================
def procesar_actas():
    drive, sheet_actas, sheet_detalle = conectar()

    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf'",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    if not files:
        st.warning("No hay PDFs en la carpeta")
        return

    st.success(f"{len(files)} PDFs encontrados")

    for file in files:
        file_id = file["id"]
        nombre = file["name"]

        st.write(f"📄 Procesando: {nombre}")

        request = drive.files().get_media(fileId=file_id)
        file_bytes = request.execute()

        texto = extraer_texto_pdf(file_bytes)
        texto = limpiar_texto(texto)

        datos = extraer_datos(texto)

        # HOJA 1 (RESUMEN)
        sheet_actas.append_row([
            datos["acta"],
            datos["fecha"],
            datos["anio"],
            datos["unidad"],
            datos["tipo"],
            datos["director"]
        ])

        # HOJA 2 (DETALLE)
        sheet_detalle.append_row([
            datos["acta"],
            datos["fecha"],
            datos["anio"],
            datos["tipo"],
            texto
        ])

    st.success("🚀 Procesamiento completo")

# =========================
# UI
# =========================
st.title("📊 Extractor de Actas - Consejo de Investigación")

if st.button("🚀 Procesar actas"):
    procesar_actas()
