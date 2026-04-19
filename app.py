import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Actas - Sistema", layout="wide")

st.title("📊 Sistema de Actas - Consejo de Investigación")

st.markdown("""
Subí actas en PDF y el sistema:

✔ Limpia el texto  
✔ Detecta proyectos e informes  
✔ Extrae títulos y directores  
✔ Genera base para Excel / Looker  
""")

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
    """
    Limpieza simple (NO rompe palabras)
    """

    texto = re.sub(r'\s+', ' ', texto)

    texto = re.sub(r'\.\s+', '.\n', texto)

    # arreglos típicos de PDF
    texto = texto.replace("DIRECT OR", "DIRECTOR")
    texto = texto.replace("PROYECT OS", "PROYECTOS")
    texto = texto.replace("PRESENT ACIÓN", "PRESENTACIÓN")
    texto = texto.replace("F acultad", "Facultad")

    return texto.strip()


def extraer_items(texto):
    """
    Extracción robusta basada en ●
    """

    items = []

    bloques = re.split(r'●', texto)

    for bloque in bloques:

        if len(bloque.strip()) < 40:
            continue

        bloque = bloque.strip()

        # =========================
        # TIPO
        # =========================
        tipo = "Proyecto"

        if "avance" in bloque.lower():
            tipo = "Informe de Avance"

        elif "final" in bloque.lower():
            tipo = "Informe Final"

        elif "categoriz" in bloque.lower():
            tipo = "Categorización"

        # =========================
        # FACULTAD
        # =========================
        facultad_match = re.search(r'Facultad de [A-Za-zÁÉÍÓÚÑ ]+', bloque)
        facultad = facultad_match.group(0) if facultad_match else "No detectado"

        # =========================
        # DIRECTOR
        # =========================
        director_match = re.search(
            r'Director[a]?:?\s*([A-Za-zÁÉÍÓÚÑ\s\.]+)',
            bloque,
            re.IGNORECASE
        )

        director = director_match.group(1).strip() if director_match else "No detectado"

        if len(director) < 5:
            director = "No detectado"

        # =========================
        # TITULO
        # =========================
        titulo = bloque.split("Director")[0]
        titulo = re.sub(r'\s+', ' ', titulo).strip()

        if len(titulo) < 10:
            continue

        items.append({
            "Tipo": tipo,
            "Facultad": facultad,
            "Titulo": titulo,
            "Director": director
        })

    return items


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

        if not texto.strip():
            st.error("No se pudo leer el PDF")
            continue

        texto_limpio = limpiar_texto(texto)

        # =========================
        # VER TEXTO
        # =========================
        with st.expander("👁 Ver texto limpio"):
            st.text_area("", texto_limpio, height=200)

        # =========================
        # DESCARGAR TXT
        # =========================
        nombre_txt = file.name.replace(".pdf", ".txt")

        st.download_button(
            label="📄 Descargar TXT limpio",
            data=texto_limpio,
            file_name=nombre_txt,
            mime="text/plain"
        )

        # =========================
        # EXTRAER DATOS
        # =========================
        items = extraer_items(texto_limpio)

        if items:
            df = pd.DataFrame(items)
            st.dataframe(df)
            todos.extend(items)
        else:
            st.warning("No detectó ítems")

    # =========================
    # DESCARGA FINAL CSV
    # =========================
    if todos:
        df_total = pd.DataFrame(todos)

        st.download_button(
            "📥 Descargar CSV",
            df_total.to_csv(index=False),
            "actas.csv",
            "text/csv"
        )
