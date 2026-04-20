import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Actas - Sistema", layout="wide")

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
    texto = re.sub(r'\s+', ' ', texto)

    # arreglos típicos PDF
    texto = texto.replace("DIRECT OR", "DIRECTOR")
    texto = texto.replace("PROYECT OS", "PROYECTOS")
    texto = texto.replace("INFORME S", "INFORMES")
    texto = texto.replace("CATEGORIZ ACIÓN", "CATEGORIZACIÓN")

    return texto


def extraer_metadata(texto):
    anio = re.search(r'dos mil (\w+)', texto.lower())
    anio = anio.group(1) if anio else "No detectado"

    fecha = re.search(r'(\d{1,2} días? del mes de .*? dos mil \w+)', texto.lower())
    fecha = fecha.group(1) if fecha else "No detectado"

    acta = re.search(r'ACTA N[º°]\s*(\d+)', texto.upper())
    acta = acta.group(1) if acta else "No detectado"

    return anio, fecha, acta


def extraer_bloques(texto):
    bloques = {}

    patrones = {
        "proyectos": r'Presentación de Proyectos(.*?)ITEM 3',
        "informes_final": r'Informes Finales(.*?)Informes de Avance',
        "informes_avance": r'Informes de Avance(.*?)ITEM 5',
        "categorizacion": r'CATEGORIZACIÓN(.*?)(Siendo las|$)'
    }

    for k, p in patrones.items():
        m = re.search(p, texto, re.IGNORECASE | re.DOTALL)
        bloques[k] = m.group(1) if m else ""

    return bloques


def parse_items(texto, tipo):
    resultados = []

    partes = re.split(r'●', texto)

    for p in partes:
        if len(p.strip()) < 40:
            continue

        titulo = re.split(r'DIRECTOR|Directora|Director', p)[0].strip()

        director = re.search(r'DIRECTOR[: ]+([A-Za-zÁÉÍÓÚÑ\s]+)', p, re.IGNORECASE)
        if not director:
            director = re.search(r'Directora[: ]+([A-Za-zÁÉÍÓÚÑ\s]+)', p)
        if not director:
            director = re.search(r'Director[: ]+([A-Za-zÁÉÍÓÚÑ\s]+)', p)

        director = director.group(1).strip() if director else "No detectado"

        facultad = re.search(r'Facultad de [A-Za-zÁÉÍÓÚÑ\s]+', p)
        facultad = facultad.group(0) if facultad else "No detectado"

        resultados.append({
            "Tipo": tipo,
            "Titulo": titulo,
            "Director": director,
            "Unidad": facultad
        })

    return resultados


def parse_categorizacion(texto):
    resultados = []

    matches = re.findall(r'([A-ZÁÉÍÓÚÑ\s]+) DNI', texto)

    for m in matches:
        resultados.append({
            "Tipo": "Categorización",
            "Titulo": "",
            "Director": m.strip(),
            "Unidad": ""
        })

    return resultados


# =========================
# UI
# =========================

files = st.file_uploader("📄 Subí PDFs", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Procesar"):

    todos = []

    for file in files:

        st.subheader(f"📄 {file.name}")

        texto = extraer_texto_pdf(file)

        if not texto.strip():
            st.error("No se pudo leer el PDF")
            continue

        texto = limpiar_texto(texto)

        with st.expander("Ver texto limpio"):
            st.text_area("", texto, height=200)

        anio, fecha, acta = extraer_metadata(texto)

        bloques = extraer_bloques(texto)

        datos = []
        datos += parse_items(bloques["proyectos"], "Proyecto de Investigación")
        datos += parse_items(bloques["informes_final"], "Informe Final")
        datos += parse_items(bloques["informes_avance"], "Informe de Avance")
        datos += parse_categorizacion(bloques["categorizacion"])

        for d in datos:
            d["Año"] = anio
            d["Fecha"] = fecha
            d["Acta"] = acta

        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df)
            todos.extend(datos)
        else:
            st.warning("No detectó registros")

    if todos:
        df_total = pd.DataFrame(todos)

        st.download_button(
            "📥 Descargar CSV FINAL",
            df_total.to_csv(index=False),
            "actas.csv",
            "text/csv"
        )
