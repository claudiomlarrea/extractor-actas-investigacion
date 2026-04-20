import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Sistema de Actas", layout="wide")

st.title("📊 Sistema de Actas - Consejo de Investigación")

st.markdown("""
Subí actas en PDF y el sistema:

✔ Limpia el texto  
✔ Extrae proyectos, informes y categorizaciones  
✔ Detecta títulos y directores  
✔ Genera base lista para Google Sheets / Looker  
""")

# =========================
# FUNCIONES
# =========================

def extraer_texto_pdf(file):
    texto = ""
    reader = PdfReader(file)

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
# EXTRACCIÓN PRINCIPAL
# =========================

def extraer_registros(texto):

    registros = []
    acta, fecha, anio = extraer_metadata(texto)

    # dividir por ITEM (estructura real de las actas)
    bloques = re.split(r'ITEM\s*\d+\.?', texto)

    for bloque in bloques:

        if len(bloque.strip()) < 80:
            continue

        # detectar facultad
        fac_match = re.search(r'Facultad de [A-Za-zÁÉÍÓÚÑ ]+', bloque)
        facultad = fac_match.group(0).strip() if fac_match else "No detectado"

        # dividir por viñetas o separadores
        subitems = re.split(r'●|\n\s*-\s*|\n\s*\*\s*', bloque)

        for sub in subitems:

            sub = sub.strip()

            if len(sub) < 40:
                continue

            # =========================
            # DIRECTOR
            # =========================
            dir_match = re.search(
                r'Director[a]?:?\s*([A-Za-zÁÉÍÓÚÑ\s\.]+)',
                sub,
                re.IGNORECASE
            )

            director = dir_match.group(1).strip() if dir_match else "No detectado"

            # =========================
            # TITULO (MEJORADO)
            # =========================
            titulo = re.split(r'Director[a]?:', sub)[0]

            titulo = re.sub(r'ITEM\s*\d+.*', '', titulo)
            titulo = re.sub(r'Facultad de .*', '', titulo)

            titulo = titulo.replace("Presentación de Proyectos", "")
            titulo = titulo.replace("Informes Finales", "")
            titulo = titulo.replace("Informes de Avance", "")

            titulo = re.sub(r'\s+', ' ', titulo).strip()

            if len(titulo) < 15:
                continue

            # =========================
            # TIPO (CORREGIDO)
            # =========================
            t = sub.lower()

            if "informe de avance" in t or "informes de avance" in t:
                tipo = "Informe de Avance"

            elif "informe final" in t or "informes finales" in t:
                tipo = "Informe Final"

            elif "categoriz" in t:
                tipo = "Categorización"

            elif "proyecto" in t:
                tipo = "Proyecto de Investigación"

            else:
                tipo = "No identificado"

            # =========================
            # GUARDAR
            # =========================
            registros.append({
                "Año": anio,
                "Fecha": fecha,
                "Acta": acta,
                "Tipo": tipo,
                "Título": titulo,
                "Director": director,
                "Facultad": facultad
            })

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

        try:
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

        except Exception as e:
            st.error("Error procesando archivo")
            st.write(e)

    # =========================
    # DESCARGA FINAL
    # =========================

    if todos:
        df_total = pd.DataFrame(todos)

        st.download_button(
            "📥 Descargar CSV",
            df_total.to_csv(index=False),
            "base_actas.csv",
            "text/csv"
        )
