import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

st.set_page_config(page_title="Extractor Orden del Día", layout="wide")

st.title("📊 Extractor - Orden del Día (Consejo de Investigación)")

# =========================
# EXTRAER TEXTO
# =========================
def extraer_texto_pdf(file):
    reader = PdfReader(file)
    texto = ""

    for page in reader.pages:
        contenido = page.extract_text()
        if contenido:
            texto += contenido + "\n"

    return texto


# =========================
# LIMPIEZA
# =========================
def limpiar_texto(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto)
    return texto


# =========================
# EXTRAER FECHA
# =========================
def extraer_fecha(texto):
    m = re.search(r'Día:\s*(.*?)Hora:', texto)
    return m.group(1).strip() if m else "No detectado"


# =========================
# EXTRAER ITEMS
# =========================
def extraer_items(texto):

    resultados = []

    # dividir por numeración tipo 1.1, 2.1, etc.
    bloques = re.split(r'\d+\.\d+', texto)

    for b in bloques:

        if "Título" not in b:
            continue

        bloque = b.strip()

        # =========================
        # TIPO
        # =========================
        if "PRONIS" in bloque:
            tipo = "Informe Final PRONIS"
        elif "INFORMES FINALES" in texto.upper():
            tipo = "Informe Final"
        elif "PROYECTO DE INVESTIGACIÓN" in texto.upper():
            tipo = "Proyecto de Investigación"
        else:
            tipo = "No detectado"

        # =========================
        # TITULO
        # =========================
        m = re.search(r'Título(?: del Proyecto)?:\s*(.*?)Director', bloque)
        titulo = m.group(1).strip() if m else "No detectado"

        # =========================
        # DIRECTOR
        # =========================
        m = re.search(r'Director/a?:\s*([A-Za-zÁÉÍÓÚÑ\s\.]+)', bloque)
        director = m.group(1).strip() if m else "No detectado"

        # =========================
        # UNIDAD
        # =========================
        m = re.search(r'Facultad de [A-Za-zÁÉÍÓÚÑ\s]+|Escuela de [A-Za-zÁÉÍÓÚÑ\s]+|ISFD.*?', bloque)
        unidad = m.group(0).strip() if m else "No detectado"

        # =========================
        # PUNTAJE
        # =========================
        m = re.search(r'Puntaje:\s*([\d\.]+)', bloque)
        puntaje = m.group(1) if m else ""

        resultados.append({
            "Tipo": tipo,
            "Título": titulo,
            "Director": director,
            "Unidad Académica": unidad,
            "Puntaje": puntaje
        })

    return resultados


# =========================
# UI
# =========================

files = st.file_uploader("Subí Orden del Día (PDF)", type=["pdf"], accept_multiple_files=True)

if st.button("Procesar"):

    todos = []

    for file in files:

        st.subheader(file.name)

        texto = extraer_texto_pdf(file)
        texto = limpiar_texto(texto)

        with st.expander("Ver texto limpio"):
            st.write(texto)

        fecha = extraer_fecha(texto)

        items = extraer_items(texto)

        for i in items:
            i["Fecha"] = fecha

        if items:
            df = pd.DataFrame(items)
            st.dataframe(df)
            todos.extend(items)
        else:
            st.warning("No se detectaron registros")

    if todos:
        df_total = pd.DataFrame(todos)

        st.download_button(
            "📥 Descargar CSV",
            df_total.to_csv(index=False),
            "orden_dia.csv",
            "text/csv"
        )
