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

/* 🔥 FONDO GENERAL CLARO */
.stApp {
    background-color: #F4F6F8;
}

/* 🔥 TEXTO GENERAL NEGRO */
h1, h2, h3, h4, p, li {
    color: #222222;
}

/* 🔥 HEADER (solo este en blanco) */
.header-uccuyo h1,
.header-uccuyo p {
    color: white !important;
}

/* 🔥 TARJETAS */
.card {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 6px solid #064a3f;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

/* 🔥 LINKS */
a {
    color: #1E88E5;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.no-link {
    color: #FF6B6B;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)
# =========================
# HEADER
# =========================

st.markdown("""
<div class='header-uccuyo' style='background-color:#064a3f; padding:25px; border-radius:15px'>
    <h1>Universidad Católica de Cuyo</h1>
    <p>Secretaría de Investigación</p>
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
