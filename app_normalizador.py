import streamlit as st
from PyPDF2 import PdfReader
import re

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Normalizador de Actas", layout="wide")

st.title("🧠 Normalizador de Actas - Consejo de Investigación")

st.markdown("""
Subí actas en PDF y el sistema generará un **TXT limpio y estructurado** listo para análisis.
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
    Limpieza institucional del texto
    """

    # eliminar múltiples espacios
    texto = re.sub(r'\s+', ' ', texto)

    # normalizar saltos de línea
    texto = re.sub(r'\.\s+', '.\n', texto)

    # separar títulos en mayúsculas
    texto = re.sub(r'([A-ZÁÉÍÓÚÑ ]{8,})', r'\n\1\n', texto)

    # eliminar caracteres raros
    texto = texto.replace("�", "")

    return texto.strip()


def estructurar_texto(texto):
    """
    Agrega separadores útiles para el siguiente paso
    """

    # separar por temas numerados
    texto = re.sub(r'\n\s*(\d+\.)', r'\n\n=== ITEM \1 ===\n', texto)

    # separar facultades
    texto = re.sub(r'(Facultad de [A-Za-zÁÉÍÓÚÑ ]+)', r'\n\n=== \1 ===\n', texto)

    return texto


# =========================
# UI
# =========================

files = st.file_uploader(
    "📄 Subí los PDFs de actas",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("🚀 Normalizar actas"):

    if not files:
        st.warning("Subí al menos un PDF")
        st.stop()

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

            # vista previa
            with st.expander("👁 Ver texto normalizado"):
                st.text_area("Resultado", texto_final, height=300)

            # descarga
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
