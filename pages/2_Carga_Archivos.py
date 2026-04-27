import streamlit as st

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Carga de Actas - Consejo de Investigación",
    layout="wide"
)

# =========================
# ESTILO
# =========================

st.markdown("""
<style>

/* Fondo general oscuro */
.stApp {
    background-color: #0E1117;
}

/* 🔥 Títulos principales en NEGRO (porque están sobre fondo claro de Streamlit) */
h1, h2, h3 {
    color: black !important;
}

/* Texto normal en NEGRO */
p, li, label, span {
    color: black !important;
}

/* Inputs (formularios) */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div {
    color: black !important;
}

/* Links */
a {
    color: #1E88E5;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Tarjetas (cards) */
.card {
    background-color: #F5F5F5;  /* 🔥 gris claro */
    color: black;               /* 🔥 texto negro */
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 6px solid #064a3f;
}

/* Texto sin link */
.no-link {
    color: #C62828;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown("""
<div style='background-color:#064a3f; padding:20px; border-radius:10px'>
    <h2 style='color:white; margin:0'>Universidad Católica de Cuyo</h2>
    <p style='color:white; margin:0'>Secretaría de Investigación</p>
</div>
""", unsafe_allow_html=True)

st.title("📂 Carga de Actas del Consejo de Investigación")

st.markdown("### Seleccione la carpeta correspondiente y cargue el archivo directamente en Google Drive")

# =========================
# LINKS (TODOS CONFIGURADOS)
# =========================

actas = {
    "Acta 190 - Mayo": "https://drive.google.com/drive/folders/1i6amwbRjPYBqCK0gZ2k5sbcBV6mVM0ki",
    "Acta 191 - Junio": "https://drive.google.com/drive/folders/118VKqYfacn5eBH0dYXRvM5uAXv2M4flI",
    "Acta 192 - Julio": "https://drive.google.com/drive/folders/1LdSq7ZcQXItGTKoHoHeFJ7xLVO4lXmRc",
    "Acta 193 - Agosto": "https://drive.google.com/drive/folders/1VVdUSebRgH2FdivZ6ZceoK30mmqtPYVs",
    "Acta 194 - Septiembre": "https://drive.google.com/drive/folders/1XkVQdpn4zNQhy2pLx0SbfTxfDQQw0eoY",
    "Acta 195 - Octubre": "https://drive.google.com/drive/folders/1UhA4EHVhHFlfB75bkbsLGYDm4YzmVZI0",
    "Acta 196 - Noviembre": "https://drive.google.com/drive/folders/1zy8FMLNbqRUkv9EaIgpCKebf1kgy1nmv",
    "Acta 197 - Diciembre": "https://drive.google.com/drive/folders/1pRFUHhn1hxpGDvEirgOjlUf2mB2Ml0Em"
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
        <li>Hacer clic en <strong>Nuevo → Subir archivo</strong></li>
        <li>Seleccionar el archivo correspondiente</li>
        <li>Verificar que quede dentro de la carpeta</li>
    </ol>

    </div>
    """, unsafe_allow_html=True)
