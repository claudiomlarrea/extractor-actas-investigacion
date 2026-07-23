import streamlit as st
from pathlib import Path

from ucc_streamlit_chrome import hide_streamlit_cloud_toolbar
from ucc_navegacion import render_menu_navegacion

st.set_page_config(page_title="Sistema de Actas", layout="wide")
hide_streamlit_cloud_toolbar()

# =========================
# ESTILO
# =========================

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-color: #D8EBE2 !important;
}

/* TEXTO GENERAL */
h1, h2, h3, p {
    color: #1e293b !important;
}

/* SIDEBAR mint (estilo EvaluAR) */
[data-testid="stSidebar"] {
    background-color: #B5D5C6 !important;
}

[data-testid="stSidebar"] > div:first-child {
    background-color: #B5D5C6 !important;
}

[data-testid="stSidebar"] * {
    color: #1e293b !important;
}

/* HEADER */
.header-uccuyo {
    background-color: #064a3f;
    padding: 20px;
    border-radius: 10px;
}

.header-uccuyo h2,
.header-uccuyo p {
    color: white !important;
    margin: 0;
}

/* Navegación: botones claros sobre mint */
[data-testid="stSidebarNav"] a {
    background-color: #ffffff !important;
    color: #1e293b !important;
    font-size: 15px !important;
    margin-bottom: 8px;
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid #9bbbac !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #9fc9b6 !important;
    color: #064a3f !important;
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

_APP_ROOT = Path(__file__).resolve().parent
_LOGO_PATH = _APP_ROOT / "assets" / "logo_uccuyo.png"

col1, col2 = st.columns([1, 6])

with col1:
    if _LOGO_PATH.exists():
        st.image(str(_LOGO_PATH), width=110)

with col2:
    st.markdown("""
    <div class='header-uccuyo'>
        <h2>Universidad Católica de Cuyo</h2>
        <p>Secretaría de Investigación</p>
    </div>
    """, unsafe_allow_html=True)

st.title("📊 Sistema de Actas - Consejo de Investigación")

render_menu_navegacion()

st.markdown("""
**En el celular:** usá los botones verdes de arriba para ir a cada sección.  
En la computadora también podés usar el menú de la izquierda.

• Cargar los temas que van a Consejo de Investigación  
• **Descargar orden del día** (generar Word al final de Cargar Temas)  
• Cargar archivos de los temas  
• Cargar Publicaciones
""")
