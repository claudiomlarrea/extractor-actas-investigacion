import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Sistema de Actas", layout="wide")

st.title("📊 Sistema de Actas - Consejo de Investigación")

# =========================
# FUNCIONES
# =========================

def extraer_texto_pdf(file):
    reader = PdfReader(file)
    texto = ""

    for page in reader.pages:
        contenido = page.extract_text()
        if contenido:
            texto += contenido + "\n"

    return texto


def limpiar_texto(texto):

    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto)

    # correcciones típicas del PDF
    texto = texto.replace("ACT A", "ACTA")
    texto = texto.replace("DIRECT OR", "DIRECTOR")
    texto = texto.replace("miembr os", "miembros")
    texto = texto.replace("F acultad", "Facultad")

    return texto.strip()


# =========================
# METADATA
# =========================

def extraer_metadata(texto):

    acta_match = re.search(r'ACTA\s*N[º°]?\s*(\d+)', texto)
    acta = acta_match.group(1) if acta_match else ""

    fecha_match = re.search(r'a los (.*?) siendo', texto, re.IGNORECASE)
    fecha = fecha_match.group(1) if fecha_match else ""

    anio_match = re.search(r'dos mil (\w+)', texto)
    anio = anio_match.group(1) if anio_match else ""

    return acta, fecha, anio


# =========================
# EXTRACCIÓN REAL (NUEVA)
# =========================

def extraer_registros(texto):

    registros = []

    acta, fecha, anio = extraer_metadata(texto)

    # patrón: TITULO + Director
    matches = re.findall(
        r'([A-ZÁÉÍÓÚÑ][^\.]{20,}?)\.\s*Director[a]?:?\s*([A-Za-zÁÉÍÓÚÑ\s]+)',
        texto
    )

    for match in matches:

        titulo = match[0].strip()
        director = match[1].strip()

        # =========================
        # CLASIFICACIÓN
        # =========================
        tipo = "Proyecto"

        t = titulo.lower()

        if "avance" in t:
            tipo = "Informe de Avance"
        elif "final" in t:
            tipo = "Informe Final"

        # =========================
        # FACULTAD (global)
        # =========================
        fac_match = re.search(r'Facultad de [A-Za-zÁÉÍÓÚÑ ]+', texto)
        facultad = fac_match.group(0) if fac_match else "No detectado"

        registro = {
            "Año": anio,
            "Fecha": fecha,
            "Acta": acta,

            "Informe de Avance": "Sí" if tipo == "Informe de Avance" else "",
            "Título de Informe de Avance": titulo if tipo == "Informe de Avance" else "",
            "Director del Informe de Avance": director if tipo == "Informe de Avance" else "",
            "Puntaje del Informe de Avance": "",
            "Unidad Académica del Informe de Avance": facultad if tipo == "Informe de Avance" else "",

            "Informe Final": "Sí" if tipo == "Informe Final" else "",
            "Título del Informe Final": titulo if tipo == "Informe Final" else "",
            "Director del Informe Final": director if tipo == "Informe Final" else "",
            "Puntaje del Informe Final": "",
            "Unidad Académica del Informe de Final": facultad if tipo == "Informe Final" else "",

            "Proyecto de Investigación": "Sí" if tipo == "Proyecto" else "",
            "Título del Proyecto de investigación": titulo if tipo == "Proyecto" else "",
            "Director del Proyecto de Investigación": director if tipo == "Proyecto" else "",
            "Puntaje del Proyecto de Investigación": "",
            "Unidad Académica del Proyecto de Investigación": facultad if tipo == "Proyecto" else "",

            "Nombre del Docente categorizado": "",
            "Tipo de Categorización": "",
            "Unidad Académica del Docente Categorizado": ""
        }

        registros.append(registro)

    return registros


# =========================
# UI
# =========================

files = st.file_uploader(
    "📄 Subí PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("🚀 Procesar"):

    if not files:
        st.warning("Subí al menos un PDF")
        st.stop()

    todos = []

    for file in files:

        st.subheader(f"📄 {file.name}")

        texto = extraer_texto_pdf(file)
        texto = limpiar_texto(texto)

        with st.expander("Texto limpio"):
            st.text_area("", texto, height=200)

        registros = extraer_registros(texto)

        if registros:
            df = pd.DataFrame(registros)
            st.dataframe(df)
            todos.extend(registros)
        else:
            st.warning("No detectó registros")

    if todos:
        df_total = pd.DataFrame(todos)

        st.download_button(
            "📥 Descargar CSV",
            df_total.to_csv(index=False),
            "base_actas.csv",
            "text/csv"
        )
