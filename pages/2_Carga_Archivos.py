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

/* ===== FONDO GENERAL CLARO ===== */
.stApp {
    background-color: #F5F7FA;
}

/* ===== TITULOS ===== */
h1, h2, h3 {
    color: #1a1a1a !important;
}

/* ===== TEXTO ===== */
p, li, label, span {
    color: #333333 !important;
}

/* ===== LINKS ===== */
a {
    color: #1565C0;
    text-decoration: none;
    font-weight: 500;
}

a:hover {
    text-decoration: underline;
}

/* ===== CARDS ===== */
.card {
    background-color: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    border-left: 6px solid #064a3f;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

/* ===== BOTONES ===== */
.stButton>button {
    background-color: #064a3f;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
}

.stButton>button:hover {
    background-color: #0b6b5a;
}

/* ===== INPUTS ===== */
input, textarea {
    color: black !important;
}

/* ===== TEXTO SIN LINK ===== */
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
