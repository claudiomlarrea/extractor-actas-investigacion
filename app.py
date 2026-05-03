import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Sistema de Actas", layout="wide")

# =========================
# ESTILO
# =========================

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-color: #F4F6F8 !important;
}

/* TEXTO GENERAL */
h1, h2, h3, p {
    color: #1A1A1A !important;
}

/* SIDEBAR (ARREGLADO) */
[data-testid="stSidebar"] {
    background-color: #1C1F26 !important;
}

[data-testid="stSidebar"] * {
    color: #EAEAEA !important;
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
/* TODAS LAS OPCIONES EN VERDE */
[data-testid="stSidebarNav"] a {
    background-color: #064a3f !important;
    color: white !important;
    font-size: 16px !important;
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 10px;
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

st.markdown("""
Bienvenido al sistema.

Usá el menú de la izquierda para:

• Cargar datos manualmente  
• Normalizar actas  

""")
