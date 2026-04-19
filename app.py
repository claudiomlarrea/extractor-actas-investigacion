import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

st.set_page_config(page_title="Sistema de Actas", layout="wide")

st.title("📊 Sistema Institucional de Actas")

# =========================
# PDF
# =========================

def extraer_texto_pdf(file):
    reader = PdfReader(file)
    texto = ""

    for page in reader.pages:
        t = page.extract_text()
        if t:
            texto += t + "\n"

    return texto


# =========================
# LIMPIEZA
# =========================

def limpiar_texto(texto):

    texto = re.sub(r'\s+', ' ', texto)

    fixes = {
        "DIRECT OR": "DIRECTOR",
        "PROYECT O": "PROYECTO",
        "F acultad": "Facultad",
    }

    for k, v in fixes.items():
        texto = texto.replace(k, v)

    texto = re.sub(r'\.\s+', '.\n', texto)

    return texto.strip()


# =========================
# EXTRACTOR 1 (●)
# =========================

def extraer_por_bullets(texto):

    items = []
    bloques = re.split(r'[●❖]', texto)

    for b in bloques:

        if len(b) < 50:
            continue

        tipo = "Proyecto"

        if "avance" in b.lower():
            tipo = "Informe de Avance"
        elif "final" in b.lower():
            tipo = "Informe Final"

        fac = re.search(r'Facultad de [A-Za-zÁÉÍÓÚÑ ]+', b)
        facultad = fac.group(0) if fac else "No detectado"

        dir_match = re.search(r'Director[a]?:?\s*(.+)', b, re.IGNORECASE)
        director = dir_match.group(1).strip() if dir_match else "No detectado"

        titulo = b.split("Director")[0].strip()

        if len(titulo) > 15:
            items.append({
                "Tipo": tipo,
                "Facultad": facultad,
                "Titulo": titulo,
                "Director": director
            })

    return items


# =========================
# EXTRACTOR 2 (tabla tipo 178)
# =========================

def extraer_tabla(texto):

    items = []

    patron = r'Facultad.*?Cuyo\s+(.*?)\s+([A-Za-zÁÉÍÓÚÑ\s]+)'

    matches = re.findall(patron, texto)

    for m in matches:

        titulo = m[0].strip()
        director = m[1].strip()

        items.append({
            "Tipo": "Proyecto PRONIS",
            "Facultad": "Detectado",
            "Titulo": titulo,
            "Director": director
        })

    return items


# =========================
# SELECTOR INTELIGENTE
# =========================

def extraer_items(texto):

    if "●" in texto or "❖" in texto:
        return extraer_por_bullets(texto)

    elif "Unidad Académica" in texto or "PRONIS" in texto:
        return extraer_tabla(texto)

    else:
        return []


# =========================
# UI
# =========================

files = st.file_uploader("Subí PDFs", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Procesar"):

    todos = []

    for file in files:

        st.subheader(file.name)

        texto = extraer_texto_pdf(file)
        limpio = limpiar_texto(texto)

        with st.expander("Texto"):
            st.text_area("", limpio, height=200)

        st.download_button("TXT", limpio, file.name.replace(".pdf", ".txt"))

        items = extraer_items(limpio)

        if items:
            df = pd.DataFrame(items)
            st.dataframe(df)
            todos.extend(items)
        else:
            st.warning("No detectado")

    if todos:
        df_total = pd.DataFrame(todos)

        st.download_button(
            "📥 CSV FINAL",
            df_total.to_csv(index=False),
            "actas_final.csv"
        )
