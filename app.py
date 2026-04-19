import streamlit as st
import re
from PyPDF2 import PdfReader
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# CONFIG
# =========================

SPREADSHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"

# =========================
# CONEXIÓN GOOGLE SHEETS
# =========================

def conectar():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID)

    hoja1 = sheet.worksheet("Hoja 1")
    hoja2 = sheet.worksheet("Hoja 2")

    return hoja1, hoja2


# =========================
# LECTURA PDF
# =========================

def extraer_texto_pdf(file):
    reader = PdfReader(file)
    texto = ""

    for page in reader.pages:
        texto += page.extract_text() + "\n"

    return texto


# =========================
# DATOS GENERALES ACTA
# =========================

def extraer_datos_basicos(texto):

    match_acta = re.search(r'ACTA\s*N[º°]?\s*(\d+)', texto)
    acta = match_acta.group(1) if match_acta else "Detectar"

    match_fecha = re.search(
        r'(\d{1,2})\s+d[ií]as del mes de\s+([a-zA-Z]+)\s+de\s+dos mil\s+(\w+)',
        texto,
        re.IGNORECASE
    )

    fecha = "Detectar"
    anio = "Detectar"

    if match_fecha:
        dia = match_fecha.group(1)
        mes = match_fecha.group(2).lower()
        anio_txt = match_fecha.group(3).lower()

        meses = {
            "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
            "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
            "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
        }

        anios = {
            "veinticinco": "2025",
            "veinticuatro": "2024"
        }

        fecha = f"{dia}/{meses.get(mes,'00')}/{anios.get(anio_txt,'2025')}"
        anio = anios.get(anio_txt, "2025")

    return {
        "acta": acta,
        "fecha": fecha,
        "anio": anio
    }


# =========================
# EXTRACCIÓN PROYECTOS
# =========================

def extraer_proyectos(texto):

    proyectos = []

    bloques = re.split(r'\n(?=Facultad)', texto)

    for bloque in bloques:

        if "proyecto" not in bloque.lower():
            continue

        # UNIDAD
        match_unidad = re.search(r'(Facultad.*?)(?:\n|$)', bloque)
        unidad = match_unidad.group(1).strip() if match_unidad else "Detectar"

        # TÍTULO
        lineas = bloque.split("\n")
        titulo = lineas[1].strip() if len(lineas) > 1 else "Detectar"

        # DIRECTOR
        match_dir = re.search(r'Director[:\s]+([A-Za-zÁÉÍÓÚÑ\s]+)', bloque, re.IGNORECASE)

        director = match_dir.group(1).strip() if match_dir else "No detectado"

        proyectos.append({
            "unidad": unidad,
            "titulo": titulo,
            "director": director
        })

    return proyectos


# =========================
# APP STREAMLIT
# =========================

st.title("📊 Extractor de Actas - Consejo de Investigación")

files = st.file_uploader(
    "Subí los PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("🚀 Procesar actas"):

    try:
        hoja1, hoja2 = conectar()
        st.success("✅ Conexión exitosa a Google Sheets")

        for file in files:

            st.write(f"📄 Procesando: {file.name}")

            texto = extraer_texto_pdf(file)

            datos = extraer_datos_basicos(texto)
            proyectos = extraer_proyectos(texto)

            if not proyectos:
                st.warning(f"⚠️ No se detectaron proyectos en {file.name}")
                continue

            for p in proyectos:
                hoja2.append_row([
                    datos["acta"],
                    datos["fecha"],
                    datos["anio"],
                    "Proyecto",
                    p["titulo"],
                    p["director"]
                ])

        st.success("🚀 Procesamiento terminado")

    except Exception as e:
        st.error("❌ Error al procesar")
        st.write(e)
