import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

st.set_page_config(page_title="Extractor Orden del Día", layout="wide")

st.title("📊 Extractor Completo - Consejo de Investigación")

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
# LIMPIAR TEXTO
# =========================
def limpiar(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto)
    return texto


# =========================
# FECHA Y ACTA
# =========================
def extraer_fecha(texto):
    m = re.search(r'Día:\s*(.*?)Hora:', texto)
    return m.group(1) if m else ""

def extraer_acta(texto):
    return "Orden del Día"


# =========================
# BLOQUES
# =========================
def extraer_bloque(texto, inicio, fin):
    m = re.search(inicio + r'(.*?)' + fin, texto, re.IGNORECASE)
    return m.group(1) if m else ""


# =========================
# EXTRAER ITEMS GENERALES
# =========================
def extraer_items(bloque):

    if not bloque or not isinstance(bloque, str):
        return []

    items = []

    lineas = bloque.split("\n")

    titulo = ""
    director = ""
    unidad = ""

    for linea in lineas:

        l = linea.strip()

        if len(l) < 10:
            continue

        # POSIBLE TITULO (mayúsculas largas)
        if l.isupper() and len(l) > 20:
            titulo = l

        # DIRECTOR (nombres propios)
        elif any(x in l for x in ["Dr", "Dra", "Lic", "Mg", "Ing"]) or len(l.split()) >= 2:
            if len(l) < 80:
                director = l

        # UNIDAD
        elif "Facultad" in l or "Escuela" in l:
            unidad = l

        # si tenemos título + director → guardamos
        if titulo and director:
            items.append({
                "titulo": titulo,
                "director": director,
                "unidad": unidad,
                "puntaje": ""
            })
            titulo = ""
            director = ""
            unidad = ""

    return items


# =========================
# CATEGORIZACIÓN
# =========================
def extraer_categorizacion(texto):

    nombres = re.findall(r'([A-ZÁÉÍÓÚÑ]+ [A-ZÁÉÍÓÚÑ]+)', texto)

    return nombres[0] if nombres else ""


# =========================
# UI
# =========================
files = st.file_uploader("Subí Orden del Día", type=["pdf"], accept_multiple_files=True)

if st.button("Procesar"):

    filas = []

    for file in files:

        texto = extraer_texto_pdf(file)
        texto = limpiar(texto)

        fecha = extraer_fecha(texto)
        acta = extraer_acta(texto)

        # BLOQUES
        finales = extraer_bloque(texto, "INFORMES FINALES", "INFORMES FINALES PRONIS|PRESENTACIÓN")
        avance = extraer_bloque(texto, "INFORMES DE AVANCE", "PRESENTACIÓN")
        proyectos = extraer_bloque(texto, "PRESENTACIÓN DE PROYECTO", "$")

        inf_final = extraer_items(finales)
        inf_avance = extraer_items(avance)
        proy = extraer_items(proyectos)

        categ = extraer_categorizacion(texto)

        fila = {
            "Año": "2026",
            "Fecha": fecha,
            "Acta": acta,

            "Título Informe Final": inf_final[0]["titulo"] if inf_final else "",
            "Director Informe Final": inf_final[0]["director"] if inf_final else "",
            "Unidad Académica Informe Final": inf_final[0]["unidad"] if inf_final else "",
            "Puntaje Informe Final": inf_final[0]["puntaje"] if inf_final else "",

            "Título Informe de Avance": inf_avance[0]["titulo"] if inf_avance else "",
            "Director Informe de Avance": inf_avance[0]["director"] if inf_avance else "",
            "Unidad Académica Informe de Avance": inf_avance[0]["unidad"] if inf_avance else "",
            "Puntaje Informe de Avance": inf_avance[0]["puntaje"] if inf_avance else "",

            "Título Proyecto de Investigación": proy[0]["titulo"] if proy else "",
            "Director Proyecto de Investigación": proy[0]["director"] if proy else "",
            "Unidad Académica Proyecto de Investigación": proy[0]["unidad"] if proy else "",
            "Puntaje Proyecto de Investigación": proy[0]["puntaje"] if proy else "",

            "Categorización Docente": "Sí" if categ else "",
            "Docente Categorizado": categ,
            "Categoría del Docente": ""
        }

        filas.append(fila)

    df = pd.DataFrame(filas)
    st.dataframe(df)

    st.download_button(
        "📥 Descargar CSV FINAL",
        df.to_csv(index=False),
        "base_final.csv",
        "text/csv"
    )
