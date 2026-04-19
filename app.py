import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Actas - Normalizador + Extractor", layout="wide")

st.title("🧠 Sistema de Actas - Consejo de Investigación")

st.markdown("""
Subí actas en PDF y el sistema:

✅ Normaliza el texto  
✅ Extrae proyectos, informes y categorizaciones  
✅ Genera datos estructurados listos para análisis  
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

    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\.\s+', '.\n', texto)
    texto = re.sub(r'([A-ZÁÉÍÓÚÑ ]{8,})', r'\n\1\n', texto)
    texto = texto.replace("�", "")

    return texto.strip()


def estructurar_texto(texto):

    texto = re.sub(r'\n\s*(\d+\.)', r'\n\n=== ITEM \1 ===\n', texto)
    texto = re.sub(r'(Facultad de [A-Za-zÁÉÍÓÚÑ ]+)', r'\n\n=== \1 ===\n', texto)

    return texto


# =========================
# EXTRACTOR INTELIGENTE
# =========================

def extraer_items(texto):

    items = []

    lineas = texto.split("\n")

    tipo_actual = "No detectado"
    facultad_actual = "No detectado"

    titulo = None
    director = "No detectado"

    for linea in lineas:

        l = linea.strip()

        # =========================
        # TIPO
        # =========================
        if "presentación de proyectos" in l.lower():
            tipo_actual = "Proyecto de Investigación"

        elif "proyectos de investigación" in l.lower():
            tipo_actual = "Proyecto de Investigación"

        elif "informes finales" in l.lower():
            tipo_actual = "Informe Final"

        elif "informe final" in l.lower():
            tipo_actual = "Informe Final"

        elif "informes de avance" in l.lower():
            tipo_actual = "Informe de Avance"

        elif "avance" in l.lower():
            tipo_actual = "Informe de Avance"

        elif "categorización" in l.lower():
            tipo_actual = "Categorización"

        # =========================
        # FACULTAD
        # =========================
        if "facultad" in l.lower():
            facultad_actual = l.replace("=", "").strip()

        # =========================
        # TÍTULO
        # =========================
        if l.startswith("●") or l.startswith("❖"):

            if titulo:
                items.append({
                    "Tipo": tipo_actual,
                    "Facultad": facultad_actual,
                    "Titulo": titulo,
                    "Director": director
                })

            titulo = l.replace("●", "").replace("❖", "").strip()
            director = "No detectado"

        # =========================
        # DIRECTOR
        # =========================
        if "director" in l.lower():

            match = re.search(r'director[a]?\s*:?\s*(.+)', l, re.IGNORECASE)

            if match:
                director = match.group(1).strip()

    # último
    if titulo:
        items.append({
            "Tipo": tipo_actual,
            "Facultad": facultad_actual,
            "Titulo": titulo,
            "Director": director
        })

    return items


# =========================
# UI
# =========================

files = st.file_uploader(
    "📄 Subí los PDFs de actas",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("🚀 Procesar actas"):

    if not files:
        st.warning("Subí al menos un PDF")
        st.stop()

    todos_los_items = []

    for file in files:

        st.subheader(f"📄 Procesando: {file.name}")

        try:
            texto_crudo = extraer_texto_pdf(file)

            if not texto_crudo.strip():
                st.error("No se pudo extraer texto")
                continue

            texto_limpio = limpiar_texto(texto_crudo)
            texto_final = estructurar_texto(texto_limpio)

            st.success("✅ Texto normalizado correctamente")

            # =========================
            # MOSTRAR TEXTO
            # =========================
            with st.expander("👁 Ver texto normalizado"):
                st.text_area("Resultado", texto_final, height=300)

            # =========================
            # EXTRAER
            # =========================
            items = extraer_items(texto_final)

            if items:
                st.success(f"📊 {len(items)} ítems detectados")

                df = pd.DataFrame(items)
                st.dataframe(df)

                todos_los_items.extend(items)

            else:
                st.warning("⚠️ No se detectaron ítems")

            # =========================
            # DESCARGA TXT
            # =========================
            nombre_txt = file.name.replace(".pdf", ".txt")

            st.download_button(
                label="⬇ Descargar TXT",
                data=texto_final,
                file_name=nombre_txt,
                mime="text/plain"
            )

        except Exception as e:
            st.error("❌ Error al procesar")
            st.write(e)

    # =========================
    # DESCARGA GLOBAL CSV
    # =========================
    if todos_los_items:

        df_total = pd.DataFrame(todos_los_items)

        csv = df_total.to_csv(index=False)

        st.download_button(
            label="📥 Descargar BASE COMPLETA (CSV)",
            data=csv,
            file_name="actas_procesadas.csv",
            mime="text/csv"
        )
