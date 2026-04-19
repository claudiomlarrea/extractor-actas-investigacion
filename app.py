import streamlit as st
import re
from PyPDF2 import PdfReader
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"

# =========================
# CONEXIÓN
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

    return sheet.worksheet("Hoja 1"), sheet.worksheet("Hoja 2")

# =========================
# PDF
# =========================

def extraer_texto_pdf(file):
    reader = PdfReader(file)
    texto = ""

    for page in reader.pages:
        texto += (page.extract_text() or "") + "\n"

    return texto

# =========================
# DATOS ACTA
# =========================

def extraer_datos_basicos(texto):

    acta = re.search(r'ACTA\s*N[º°]?\s*(\d+)', texto)
    acta = acta.group(1) if acta else "Detectar"

    fecha_match = re.search(
        r'(\d{1,2})\s+d[ií]as del mes de\s+(\w+)\s+de\s+dos mil\s+(\w+)',
        texto,
        re.IGNORECASE
    )

    meses = {
        "enero":"01","febrero":"02","marzo":"03","abril":"04",
        "mayo":"05","junio":"06","julio":"07","agosto":"08",
        "septiembre":"09","octubre":"10","noviembre":"11","diciembre":"12"
    }

    anios = {
        "veinticinco":"2025",
        "veinticuatro":"2024"
    }

    if fecha_match:
        dia = fecha_match.group(1)
        mes = meses.get(fecha_match.group(2).lower(), "00")
        anio = anios.get(fecha_match.group(3).lower(), "2025")
        fecha = f"{dia}/{mes}/{anio}"
    else:
        fecha = "Detectar"
        anio = "Detectar"

    unidad = "UCCuyo" if "universidad católica de cuyo" in texto.lower() else "Detectar"

    return acta, fecha, anio, unidad

# =========================
# DETECTAR TIPO
# =========================

def detectar_tipo(texto):
    t = texto.lower()

    if "proyecto de investigación" in t:
        return "Proyecto de Investigación"
    elif "proyecto de cátedra" in t:
        return "Proyecto de Cátedra"
    elif "informe final" in t:
        return "Informe Final"
    elif "informe de avance" in t:
        return "Informe de Avance"
    elif "informe de cátedra" in t:
        return "Informe de Cátedra"
    else:
        return "Otro"

# =========================
# EXTRAER ITEMS (VERSIÓN PRO)
# =========================

def extraer_items(texto):

    items = []

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    for i, linea in enumerate(lineas):

        tipo = detectar_tipo(linea)

        if tipo != "Otro":

            # TÍTULO = siguiente línea larga coherente
            titulo = "Sin título"

            for j in range(i+1, min(i+6, len(lineas))):
                if len(lineas[j]) > 15 and "acta" not in lineas[j].lower():
                    titulo = lineas[j]
                    break

            # DIRECTOR
            director = "No detectado"

            bloque = " ".join(lineas[i:i+10])

            match = re.search(r'Director[:\s]+([A-Za-zÁÉÍÓÚÑ\s]+)', bloque, re.IGNORECASE)
            if match:
                director = match.group(1).strip()

            items.append((tipo, titulo, director))

    return items

# =========================
# APP
# =========================

st.title("📊 Extractor de Actas - Consejo de Investigación")

files = st.file_uploader("Subí los PDFs", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Procesar actas"):

    try:
        hoja1, hoja2 = conectar()
        st.success("✅ Conectado a Google Sheets")

        for file in files:

            st.write(f"📄 Procesando: {file.name}")

            texto = extraer_texto_pdf(file)

            acta, fecha, anio, unidad = extraer_datos_basicos(texto)
            items = extraer_items(texto)

            # HOJA 1
            hoja1.append_row([acta, fecha, anio, unidad])

            if not items:
                st.warning("⚠️ No se detectaron ítems")
                continue

            # HOJA 2
            for tipo, titulo, director in items:
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
