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
        import pdfplumber
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto += t + "\n"
    except:
        return ""
    return texto

def extraer_datos(texto):

    if not texto:
        return []

    texto = texto.replace("\r", "\n")

    resultados = []

    # ACTA
    acta = ""
    m = re.search(r'ACTA\s*N[°º]?\s*(\d+)', texto, re.IGNORECASE)
    if m:
        acta = m.group(1)

    # FECHA
    fecha = ""
    m = re.search(r'\d+\s+d[ií]as.*?dos mil \w+', texto.lower())
    if m:
        fecha = m.group(0)

    # UNIDAD
    unidad = ""
    m = re.search(r'Facultad de [A-Za-zÁÉÍÓÚÑ ]+', texto)
    if m:
        unidad = m.group(0)

    # ITEMS (orden del día)
    items = re.findall(r'\n\s*\d+\.\s+(.*)', texto)

    for i in items:
        resultados.append({
            "Año": "",
            "Fecha": fecha,
            "Acta": acta,
            "Título": i.strip(),
            "Unidad": unidad
        })

    return resultados


# =========================
# 🧠 EXTRACTOR REAL (NO INVENTA)
# =========================
def extraer_datos(texto):

    if not texto:
        return []

    texto = texto.replace("\r", "\n")

    datos = {
        "Año": "",
        "Fecha": "",
        "Acta": "",
        "Título Informe Final": "",
        "Director Informe Final": "",
        "Unidad Académica Informe Final": "",
        "Puntaje Informe Final": "",
        "Título Informe de Avance": "",
        "Director Informe de Avance": "",
        "Unidad Académica Informe de Avance": "",
        "Puntaje Informe de Avance": "",
        "Título Proyecto de Investigación": "",
        "Director Proyecto de Investigación": "",
        "Unidad Académica Proyecto de Investigación": "",
        "Puntaje Proyecto de Investigación": "",
        "Categorización Docente": "",
        "Docente Categorizado": "",
        "Categoría del Docente": ""
    }

    # =========================
    # ACTA
    # =========================
    acta = re.search(r'ACTA\s*N[°º]?\s*(\d+)', texto, re.IGNORECASE)
    if acta:
        datos["Acta"] = acta.group(1)

    # =========================
    # FECHA
    # =========================
    fecha = re.search(r'(\d+\s+d[ií]as.*?dos mil \w+)', texto.lower())
    if fecha:
        datos["Fecha"] = fecha.group(1)

    # =========================
    # AÑO
    # =========================
    anio = re.search(r'dos mil (\w+)', texto.lower())
    if anio:
        datos["Año"] = anio.group(1)

    # =========================
    # INFORME FINAL
    # =========================
    inf_final = re.search(r'INFORME FINAL[:\s]*(.*?)\n', texto, re.IGNORECASE)
    if inf_final:
        datos["Título Informe Final"] = inf_final.group(1).strip()

    dir_final = re.search(r'DIRECTOR[:\s]*([A-Za-zÁÉÍÓÚÑ ]+)', texto)
    if dir_final:
        datos["Director Informe Final"] = dir_final.group(1).strip()

    unidad = re.search(r'(Facultad de [A-Za-zÁÉÍÓÚÑ ]+)', texto)
    if unidad:
        datos["Unidad Académica Informe Final"] = unidad.group(1)

    # =========================
    # INFORME DE AVANCE
    # =========================
    inf_avance = re.search(r'INFORME DE AVANCE[:\s]*(.*?)\n', texto, re.IGNORECASE)
    if inf_avance:
        datos["Título Informe de Avance"] = inf_avance.group(1).strip()

    # =========================
    # PROYECTO
    # =========================
    proyecto = re.search(r'PROYECTO[:\s]*(.*?)\n', texto, re.IGNORECASE)
    if proyecto:
        datos["Título Proyecto de Investigación"] = proyecto.group(1).strip()

    # =========================
    # CATEGORIZACIÓN
    # =========================
    cat = re.search(r'CATEGORIZACI[ÓO]N[:\s]*(.*?)\n', texto, re.IGNORECASE)
    if cat:
        datos["Docente Categorizado"] = cat.group(1).strip()
        datos["Categorización Docente"] = "Sí"

    return [datos]


# =========================
# 📤 UI
# =========================

files = st.file_uploader(
    "Subí Orden del Día (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Procesar"):

    todos = []

    for file in files:

        st.subheader(f"📄 {file.name}")

        texto = extraer_texto_pdf(file)

        if not texto:
            st.error("No se pudo leer el PDF")
            continue

        datos = extraer_datos(texto)

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
