import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="Extractor Orden del Día", layout="wide")

st.title("📊 Extractor Orden del Día - Consejo de Investigación")

# =========================
# 📄 EXTRAER TEXTO PDF
# =========================
def extraer_texto_pdf(file):
    texto = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto += t + "\n"
    except:
        return ""
    return texto


# =========================
# 🧠 EXTRAER ORDEN DEL DÍA
# =========================
def extraer_orden_dia(texto):

    if not texto:
        return []

    # Normalizar
    texto = texto.replace("\r", "\n")

    # Separar por numeración tipo "1.", "2.", etc.
    bloques = re.split(r"\n\s*\d+\.\s+", texto)

    resultados = []

    for b in bloques:
        b = b.strip()

        if len(b) < 20:
            continue

        lineas = b.split("\n")

        titulo = ""
        director = ""
        unidad = ""

        for l in lineas:
            l = l.strip()

            if not l:
                continue

            # TITULO (línea larga)
            if not titulo and len(l) > 25:
                titulo = l

            # DIRECTOR (nombre corto probable)
            elif not director and 2 <= len(l.split()) <= 5:
                director = l

            # UNIDAD
            elif "Facultad" in l or "Escuela" in l:
                unidad = l

        resultados.append({
            "Tipo": "Orden del Día",
            "Titulo": titulo,
            "Director": director if director else "No detectado",
            "Unidad": unidad if unidad else "No detectado"
        })

    return resultados


# =========================
# 📤 UI
# =========================

files = st.file_uploader("Subí Orden del Día (PDF)", type=["pdf"], accept_multiple_files=True)

if st.button("Procesar"):

    todos = []

    for file in files:

        st.subheader(f"📄 {file.name}")

        texto = extraer_texto_pdf(file)

        if not texto:
            st.error("No se pudo leer el PDF")
            continue

        datos = extraer_orden_dia(texto)

        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df)
            todos.extend(datos)
        else:
            st.warning("No detectó registros")

    # =========================
    # 📥 DESCARGA FINAL
    # =========================
    if todos:
        df_total = pd.DataFrame(todos)

        csv = df_total.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Descargar CSV FINAL",
            csv,
            "orden_del_dia.csv",
            "text/csv"
        )
