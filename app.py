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

    # =========================
    # 1. normalizar espacios base
    # =========================
    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto)

    # =========================
    # 2. separar palabras pegadas (clave)
    # =========================
    texto = re.sub(r'([a-záéíóúñ])([A-ZÁÉÍÓÚÑ])', r'\1 \2', texto)

    # =========================
    # 3. arreglos específicos OCR (muy importantes)
    # =========================
    fixes = {
        "delmes": "del mes",
        "dela": "de la",
        "alos": "a los",
        "lamisma": "la misma",
        "Setratan": "Se tratan",
        "Lecturadel": "Lectura del",
        "actaanterior": "acta anterior",
        "PRESENTACIÓNDEPROYECTOSDEINVESTIGACIÓN": "PRESENTACIÓN DE PROYECTOS DE INVESTIGACIÓN",
        "CARGADEDATOS": "CARGA DE DATOS",
        "INFORMEFINAL": "INFORME FINAL",
        "CATEGORIZACIÓNEXTRAORDINARIA": "CATEGORIZACIÓN EXTRAORDINARIA",
        "Consejode": "Consejo de",
        "Investigacióndela": "Investigación de la",
        "Católicade": "Católica de",
        "UniversidadCatólica": "Universidad Católica",
        "GoogleMeet": "Google Meet",
    }

    for k, v in fixes.items():
        texto = texto.replace(k, v)

    # =========================
    # 4. reconstruir facultades (clave)
    # =========================
    texto = re.sub(r'Facultad de Filosof\s*===\s*ía', 'Facultad de Filosofía', texto)

    # =========================
    # 5. saltos estructurales
    # =========================
    texto = re.sub(r'(\d+\.)', r'\n\n=== ITEM \1 ===\n', texto)

    texto = re.sub(r'(Facultad de [A-Za-zÁÉÍÓÚÑ ]+)', r'\n\n=== \1 ===\n', texto)

    # =========================
    # 6. limpieza final
    # =========================
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\.\s+', '.\n', texto)

    return texto.strip()

def estructurar_texto(texto):

    # SOLO separar ITEMS (no facultades)
    texto = re.sub(r'ITEM\s*(\d+)', r'\n\n=== ITEM \1 ===\n', texto)

    return texto


# =========================
# EXTRACTOR INTELIGENTE
# =========================

def extraer_items(texto):

    items = []

    # =========================
    # DIVIDIR POR PROYECTOS (●)
    # =========================
    bloques = re.split(r'●', texto)

    for bloque in bloques:

        if len(bloque.strip()) < 40:
            continue

        bloque = bloque.strip()

        # =========================
        # TIPO
        # =========================
        tipo = "Proyecto de Investigación"

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
        # DIRECTOR (mejorado)
        # =========================
        director_match = re.search(
            r'Director[a]?:?\s*([A-Za-zÁÉÍÓÚÑ\s\.]+)',
            bloque,
            re.IGNORECASE
        )

        director = director_match.group(1).strip() if director_match else "No detectado"

        # limpiar basura tipo "D", "a", "Mg"
        if len(director) < 5:
            director = "No detectado"

        # =========================
        # TITULO (todo antes de Director)
        # =========================
        titulo = bloque.split("Director")[0]
        titulo = re.sub(r'\s+', ' ', titulo).strip()

        # evitar títulos basura
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
