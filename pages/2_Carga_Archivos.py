import streamlit as st

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Carga de Actas", layout="wide")

st.title("📂 Carga de Archivos de Actas")

st.markdown("### Seleccione la carpeta correspondiente y cargue el archivo directamente en Google Drive")

# =========================
# LINKS DE CARPETAS
# =========================

carpetas = {
    "Acta 190 - Mayo": "https://drive.google.com/drive/folders/1i6amwbRjPYBqCK0gZ2k5sbcBV6mVM0ki",
    "Acta 191 - Junio": "LINK_AQUI",
    "Acta 192 - Julio": "LINK_AQUI",
    "Acta 193 - Agosto": "LINK_AQUI",
    "Acta 194 - Septiembre": "LINK_AQUI",
    "Acta 195 - Octubre": "LINK_AQUI",
    "Acta 196 - Noviembre": "LINK_AQUI",
    "Acta 197 - Diciembre": "LINK_AQUI"
}

# =========================
# UI
# =========================

for nombre, link in carpetas.items():

    col1, col2 = st.columns([1, 6])

    with col1:
        st.markdown("📁")

    with col2:
        st.markdown(f"### {nombre}")
        st.markdown(f"[🔗 Abrir carpeta]({link})")

        st.markdown("""
        **Cómo cargar el archivo:**
        1. Se abrirá Google Drive  
        2. Arrastre el archivo o haga clic en "Nuevo" → "Subir archivo"  
        3. Verifique que el archivo quede dentro de la carpeta  
        """)

    st.divider()
