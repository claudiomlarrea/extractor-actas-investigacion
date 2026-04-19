import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from PyPDF2 import PdfReader
import re
import io

# =========================
# CONFIG
# =========================

SPREADSHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"
CARPETA_DRIVE_ID = "1v1UPHiDF3eimPdCfaGGueKWg9M8jzdMJ"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# =========================
# CONEXIÓN GOOGLE
# =========================

def conectar():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID)

    hoja1 = sheet.worksheet("Hoja 1")
    hoja2 = sheet.worksheet("Hoja 2")

    return hoja1, hoja2

# =========================
# NORMALIZAR TEXTO
# =========================

def normalizar_texto(texto):
    texto = texto.lower()

    reemplazos = {
        "dos mil veinticinco": "2025",
        "dos mil veinticuatro": "2024",
        "dos mil veintitrés": "2023",
        "enero": "01",
        "febrero": "02",
        "marzo": "03",
        "abril": "04",
        "mayo": "05",
        "junio": "06",
        "julio": "07",
        "agosto": "08",
        "septiembre": "09",
        "octubre": "10",
        "noviembre": "11",
        "diciembre": "12"
    }

    for k, v in reemplazos.items():
        texto = texto.replace(k, v)

    return texto

# =========================
# EXTRAER DATOS (MEJORADO)
# =========================

def extraer_datos(texto):
    datos = {}

    texto_norm = normalizar_texto(texto)

    # ACTA
    match_acta = re.search(r'acta\s*n[º°]?\s*(\d+)', texto_norm)
    datos["acta"] = match_acta.group(1) if match_acta else "Detectar"

    # FECHA REAL
    match_fecha = re.search(
        r'(\d{1,2}).*?mes.*?(\d{2}).*?(20\d{2})',
        texto_norm
    )

    if match_fecha:
        dia = match_fecha.group(1)
        mes = match_fecha.group(2)
        anio = match_fecha.group(3)

        datos["fecha"] = f"{dia}/{mes}/{anio}"
        datos["anio"] = anio
    else:
        datos["fecha"] = "Detectar"
        datos["anio"] = "Detectar"

    # UNIDAD
    if "universidad católica de cuyo" in texto_norm:
        datos["unidad"] = "UCCuyo"
    else:
        datos["unidad"] = "Detectar"

    # TIPO
    if "proyecto" in texto_norm:
        datos["tipo"] = "Proyecto"
    elif "informe final" in texto_norm:
        datos["tipo"] = "Informe final"
    elif "avance" in texto_norm:
        datos["tipo"] = "Informe de avance"
    else:
        datos["tipo"] = "Otro"

    # DIRECTOR
    match_dir = re.search(r'director[:\s]+([a-zA-Z\s]+)', texto_norm)
    datos["director"] = match_dir.group(1).strip().title() if match_dir else "No detectado"

    return datos

# =========================
# LEER PDF
# =========================

def leer_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    texto = ""

    for page in reader.pages:
        texto += page.extract_text() + "\n"

    return texto

# =========================
# UI
# =========================

st.title("📊 Extractor de Actas - Consejo de Investigación")

if st.button("🚀 Procesar actas"):

    try:
        hoja1, hoja2 = conectar()
        st.success("Conexión exitosa")

        archivos = st.file_uploader(
            "Subí los PDFs",
            type=["pdf"],
            accept_multiple_files=True
        )

        if archivos:

            for archivo in archivos:
                texto = leer_pdf(archivo.read())
                datos = extraer_datos(texto)

                # 🚫 evitar basura
                if datos["acta"] == "Detectar":
                    continue

                hoja1.append_row([
                    datos["acta"],
                    datos["fecha"],
                    datos["anio"],
                    datos["unidad"]
                ])

                hoja2.append_row([
                    datos["acta"],
                    datos["fecha"],
                    datos["anio"],
                    datos["tipo"],
                    texto[:500],
                    datos["director"]
                ])

            st.success("Procesamiento terminado")

        else:
            st.warning("Subí PDFs")

    except Exception as e:
        st.error("Error al procesar")
        st.code(str(e))
