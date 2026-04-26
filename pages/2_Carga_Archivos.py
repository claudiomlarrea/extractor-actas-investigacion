import streamlit as st

# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="Carga de Actas - Consejo de Investigación",
    layout="wide"
)

# =========================
# ESTILO INSTITUCIONAL
# =========================

st.markdown("""
<style>

/* Fondo */
.stApp {
    background-color: #0E1117;
}

/* Títulos */
h1, h2, h3 {
    color: white;
}

/* Texto */
p, li {
    color: #CFCFCF;
}

/* Botones tipo link */
a {
    color: #4FC3F7;
    text-decoration: none;
    font-weight: 500;
}

a:hover {
    text-decoration: underline;
}

.card {
    background-color: #1C1F26;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
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
# LINKS DE ACTAS
# =========================

actas = {
    "Acta 190 - Mayo": "https://drive.google.com/drive/folders/1i6amwbRjPYBqCK0gZ2k5sbcBV6mVM0ki",
    "Acta 191 - Junio": "https://drive.google.com/drive/folders/118VKqYfacn5eBH0dYXRvM5uAXv2M4flI",
    "Acta 192 - Julio": "PEGAR_LINK_AQUI",
    "Acta 193 - Agosto": "PEGAR_LINK_AQUI",
    "Acta 194 - Septiembre": "PEGAR_LINK_AQUI",
    "Acta 195 - Octubre": "PEGAR_LINK_AQUI",
    "Acta 196 - Noviembre": "PEGAR_LINK_AQUI",
    "Acta 197 - Diciembre": "PEGAR_LINK_AQUI"
}

# =========================
# RENDER ACTAS
# =========================

for nombre, link in actas.items():

    st.markdown(f"""
    <div class="card">

    <h3>📁 {nombre}</h3>

    <p>
        🔗 <a href="{link}" target="_blank">Abrir carpeta</a>
    </p>

    <p><strong>Cómo cargar el archivo:</strong></p>

    <ol>
        <li>Se abrirá Google Drive</li>
        <li>Hacer clic en <strong>Nuevo → Subir archivo</strong></li>
        <li>Seleccionar el archivo correspondiente</li>
        <li>Verificar que quede dentro de la carpeta</li>
    </ol>

    </div>
    """, unsafe_allow_html=True)
