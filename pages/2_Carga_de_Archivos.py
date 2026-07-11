import streamlit as st
from pathlib import Path

from ucc_streamlit_chrome import hide_streamlit_cloud_toolbar

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Carga de Actas - Consejo de Investigación",
    layout="wide"
)
hide_streamlit_cloud_toolbar()

# =========================
# ESTILO
# =========================

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-color: #D8EBE2 !important;
}

.block-container {
    background-color: transparent !important;
    opacity: 1 !important;
}

section.main > div {
    opacity: 1 !important;
}

h1, h2, h3, p, li {
    color: #1e293b !important;
}

[data-testid="stSidebar"] {
    background-color: #B5D5C6 !important;
}

[data-testid="stSidebar"] > div:first-child {
    background-color: #B5D5C6 !important;
}

[data-testid="stSidebar"] * {
    color: #1e293b !important;
}

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

_APP_ROOT = Path(__file__).resolve().parents[1]
_LOGO_PATH = _APP_ROOT / "assets" / "logo_uccuyo.png"

col1, col2 = st.columns([1, 6])

with col1:
    if _LOGO_PATH.exists():
        st.image(str(_LOGO_PATH), width=110)
    else:
        st.warning("Logo no encontrado")

with col2:
    st.markdown("""
    <div class='header-uccuyo'>
        <h2>Universidad Católica de Cuyo</h2>
        <p>Secretaría de Investigación</p>
    </div>
    """, unsafe_allow_html=True)

# TÍTULO
st.title("📂 Carga de Archivos para el Consejo de Investigación")

st.markdown("### Seleccione la carpeta correspondiente y cargue el archivo directamente en Google Drive")

# =========================
# LINKS (TODOS CONFIGURADOS)
# =========================

actas = {
    "Categorización CVar 2026": "https://drive.google.com/drive/folders/1kLCX1LIHYpEH8W0ud-5SW39Z_GGGLXmp",
    "Orden del Día Mayo - Acta 190": "https://drive.google.com/drive/folders/1i6amwbRjPYBqCK0gZ2k5sbcBV6mVM0ki",
    "Orden del Día Junio - Acta 191": "https://drive.google.com/drive/folders/118VKqYfacn5eBH0dYXRvM5uAXv2M4flI",
    "Orden del Día Julio - Acta 192": "https://drive.google.com/drive/folders/1T1GID13Wa5TXmTfibQ0HAMBtNmOvC-DH",
    "Orden del Día Agosto - Acta 193": "https://drive.google.com/drive/folders/1VVdUSebRgH2FdivZ6ZceoK30mmqtPYVs",
    "Orden del Día Septiembre - Acta 194": "https://drive.google.com/drive/folders/1XkVQdpn4zNQhy2pLx0SbfTxfDQQw0eoY",
    "Orden del Día Octubre - Acta 195": "https://drive.google.com/drive/folders/1UhA4EHVhHFlfB75bkbsLGYDm4YzmVZI0",
    "Orden del Día Noviembre - Acta 196": "https://drive.google.com/drive/folders/1zy8FMLNbqRUkv9EaIgpCKebf1kgy1nmv",
    "Orden del Día Diciembre - Acta 197": "https://drive.google.com/drive/folders/1pRFUHhn1hxpGDvEirgOjlUf2mB2Ml0Em"
}

# =========================
# RENDER
# =========================

for nombre, link in actas.items():

    if "XXXXXXXX" in link:
        link_html = "<p class='no-link'>🔒 Carpeta aún no habilitada</p>"
    else:
        link_html = f'<p>🔗 <a href="{link}" target="_blank">Abrir carpeta</a></p>'

    st.markdown(f"""
    <div class="card">

    <h3>📁 {nombre}</h3>

    {link_html}

    <p><strong>Cómo cargar el archivo:</strong></p>

    <ol>
        <li>Se abrirá Google Drive</li>
        <li><strong>Hacer clic en la Carpeta de su Unidad Académica</strong></li>
        <li>Hacer clic en <strong>Nuevo → Subir archivo</strong></li>
        <li>Seleccionar el archivo correspondiente</li>
        <li>Verificar que quede dentro de la carpeta</li>
    </ol>

    </div>
    """, unsafe_allow_html=True)
