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
# EXTRAER DATOS
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

        # TÍTULO (línea siguiente)
        lineas = bloque.split("\n")
        titulo = lineas[1].strip() if len(lineas) > 1 else "Detectar"

        # DIRECTOR
        match_dir = re.search(r'Director[:\s]+([A-Za-zÁÉÍÓÚÑ\s]+)', bloque, re.IGNORECASE)
        if not match_dir:
            match_dir = re.search(r'DIRECTOR[:\s]+([A-Za-zÁÉÍÓÚÑ\s]+)', bloque)

        director = match_dir.group(1).strip() if match_dir else "No detectado"

        proyectos.append({
            "unidad": unidad,
            "titulo": titulo,
            "director": director
        })

    return proyectos

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
        contenido = page.extract_text()
        if contenido:
            texto += contenido + "\n"

    return texto

# =========================
# INTERFAZ
# =========================

st.title("📊 Extractor de Actas - Consejo de Investigación")

# 👇 SIEMPRE visible
archivos = st.file_uploader(
    "📂 Subí los PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# 👇 botón independiente
if st.button("🚀 Procesar actas"):

    if not archivos:
        st.warning("Primero subí los PDFs")
        st.stop()

    try:
        hoja1, hoja2 = conectar()
        st.success("Conexión exitosa a Google Sheets")

        for archivo in archivos:

            st.write(f"📄 Procesando: {archivo.name}")

            texto = leer_pdf(archivo.read())

            if not texto.strip():
                st.warning(f"No se pudo leer el PDF: {archivo.name}")
                continue

            datos = extraer_datos(texto)

            st.write(datos)  # DEBUG visible

            if datos["acta"] == "Detectar":
                st.warning(f"No se detectó acta en {archivo.name}")
                continue

            # Guardar en Hoja 1
            hoja1.append_row([
                datos["acta"],
                datos["fecha"],
                datos["anio"],
                datos["unidad"]
            ])

            # Guardar en Hoja 2
            hoja2.append_row([
                datos["acta"],
                datos["fecha"],
                datos["anio"],
                datos["tipo"],
                texto[:500],
                datos["director"]
            ])

        st.success("🎉 Procesamiento terminado correctamente")

    except Exception as e:
        st.error("❌ Error al procesar")
        st.code(str(e))
