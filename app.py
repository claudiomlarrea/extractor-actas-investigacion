import streamlit as st
import re
from PyPDF2 import PdfReader
import gspread
from google.oauth2.service_account import Credentials

# =========================
# CONFIG
# =========================

SPREADSHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"

# =========================
# CONEXIÓN GOOGLE SHEETS
# =========================

def conectar():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)

    hoja1 = sheet.worksheet("Hoja 1")
    hoja2 = sheet.worksheet("Hoja 2")

    return hoja1, hoja2


# =========================
# LEER PDF
# =========================

def extraer_texto_pdf(file):
    reader = PdfReader(file)
    texto = ""

    for page in reader.pages:
        texto += page.extract_text() + "\n"

    return texto


# =========================
# DATOS ACTA
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

    return acta, fecha, anio


# =========================
# DETECTAR TIPO
# =========================

def detectar_tipo(texto):

    texto = texto.lower()

    if "proyecto" in texto:
        return "Proyecto"
    elif "informe final" in texto:
        return "Informe Final"
    elif "avance" in texto:
        return "Informe de Avance"
    elif "categoriz" in texto:
        return "Categorización"
    else:
        return "Otro"


# =========================
# EXTRAER ITEMS
# =========================

def extraer_items(texto):

    items = []

    bloques = re.split(r'\n(?=Facultad)', texto)

    for bloque in bloques:

        if "proyecto" not in bloque.lower():
            continue

        # TÍTULO
        lineas = bloque.split("\n")
        titulo = lineas[1].strip() if len(lineas) > 1 else "Sin título"

        # DIRECTOR
        match_dir = re.search(r'Director[:\s]+([A-Za-zÁÉÍÓÚÑ\s]+)', bloque, re.IGNORECASE)
        director = match_dir.group(1).strip() if match_dir else "No detectado"

        tipo = detectar_tipo(bloque)

        items.append((tipo, titulo, director))

    return items


# =========================
# EVITAR DUPLICADOS
# =========================

def existe(hoja, acta, titulo):
    datos = hoja.get_all_values()

    for fila in datos:
        if len(fila) > 4:
            if fila[0] == acta and fila[4] == titulo:
                return True

    return False


# =========================
# APP
# =========================

st.title("📊 Extractor de Actas - Consejo de Investigación")

files = st.file_uploader("Subí los PDFs", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Procesar actas"):

    try:
        hoja1, hoja2 = conectar()
        st.success("✅ Conexión a Google Sheets OK")

        for file in files:

            st.write(f"📄 Procesando: {file.name}")

            texto = extraer_texto_pdf(file)

            acta, fecha, anio = extraer_datos_basicos(texto)
            items = extraer_items(texto)

            # GUARDAR ACTA
            hoja1.append_row([acta, fecha, anio, "UCCuyo"])

            if not items:
                st.warning("⚠️ No se detectaron proyectos")
                continue

            for tipo, titulo, director in items:

                if existe(hoja2, acta, titulo):
                    continue

                hoja2.append_row([
                    acta,
                    fecha,
                    anio,
                    tipo,
                    titulo,
                    director
                ])

        st.success("🚀 PROCESO COMPLETADO")

    except Exception as e:
        st.error("❌ Error")
        st.write(e)
