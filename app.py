import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Sistema de Actas", layout="wide")

st.title("📊 Sistema Institucional de Actas - Consejo de Investigación")

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

    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\.\s+', '.\n', texto)

    # arreglos comunes
    texto = texto.replace("ACT A", "ACTA")
    texto = texto.replace("miembr os", "miembros")
    texto = texto.replace("DIRECT OR", "DIRECTOR")

    return texto.strip()


# =========================
# EXTRACCIÓN DE METADATA
# =========================

def extraer_metadata(texto):

    # ACTA
    acta_match = re.search(r'ACTA\s*N[º°]?\s*(\d+)', texto)
    acta = acta_match.group(1) if acta_match else ""

    # FECHA (muy importante)
    fecha_match = re.search(
        r'a los (.*?) siendo',
        texto,
        re.IGNORECASE
    )

    fecha = fecha_match.group(1) if fecha_match else ""

    # AÑO
    anio_match = re.search(r'dos mil (\w+)', texto)
    anio = anio_match.group(1) if anio_match else ""

    return acta, fecha, anio


# =========================
# EXTRACCIÓN PRINCIPAL
# =========================

def procesar_acta(texto):

    registros = []

    acta, fecha, anio = extraer_metadata(texto)

    # dividir por ITEM
    bloques = re.split(r'ITEM\s*\d+\.', texto)

    for bloque in bloques:

        bloque_lower = bloque.lower()

        tipo = None

        if "avance" in bloque_lower:
            tipo = "Informe de Avance"
        elif "final" in bloque_lower:
            tipo = "Informe Final"
        elif "proyecto" in bloque_lower:
            tipo = "Proyecto"
        elif "categoriz" in bloque_lower:
            tipo = "Categorización"

        if not tipo:
            continue

        # separar por bullets
        items = re.split(r'●', bloque)

        for item in items:

            item = item.strip()

            if len(item) < 30:
                continue

            # TITULO
            titulo = item.split("Director")[0].strip()
            titulo = re.sub(r'\s+', ' ', titulo)

            # DIRECTOR
            director_match = re.search(
                r'Director[a]?:?\s*([A-Za-zÁÉÍÓÚÑ\s]+)',
                item,
                re.IGNORECASE
            )

            director = director_match.group(1).strip() if director_match else ""

            # FACULTAD
            facultad_match = re.search(r'Facultad de [A-Za-zÁÉÍÓÚÑ ]+', item)
            facultad = facultad_match.group(0) if facultad_match else ""

            # CATEGORIZACIÓN (caso especial)
            docente = ""
            tipo_cat = ""

            if tipo == "Categorización":

                doc_match = re.search(r'([A-ZÁÉÍÓÚÑ\s]+)\s+DNI', item)
                docente = doc_match.group(1).strip() if doc_match else ""

                tipo_match = re.search(r'CATEGOR[IÍ]A\s+([A-ZIV]+)', item)
                tipo_cat = tipo_match.group(1) if tipo_match else ""

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

                "Nombre del Docente categorizado": docente,
                "Tipo de Categorización": tipo_cat,
                "Unidad Académica del Docente Categorizado": facultad if tipo == "Categorización" else ""
            }

            registros.append(registro)

    return registros


# =========================
# UI
# =========================

files = st.file_uploader(
    "📄 Subí actas PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("🚀 Procesar Actas"):

    if not files:
        st.warning("Subí al menos un archivo")
        st.stop()

    base_total = []

    for file in files:

        st.subheader(f"📄 {file.name}")

        texto = extraer_texto_pdf(file)
        texto = limpiar_texto(texto)

        with st.expander("Ver texto"):
            st.text_area("", texto, height=200)

        registros = procesar_acta(texto)

        if registros:
            df = pd.DataFrame(registros)
            st.dataframe(df)
            base_total.extend(registros)
        else:
            st.warning("No se detectaron registros")

    if base_total:
        df_final = pd.DataFrame(base_total)

        st.download_button(
            "📥 Descargar BASE COMPLETA (CSV)",
            df_final.to_csv(index=False),
            "base_actas.csv",
            "text/csv"
        )
