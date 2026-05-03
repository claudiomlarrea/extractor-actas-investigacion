import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

sheet_pub = client.open("Datos Consejo Investigación").worksheet("publicaciones_sheet")

st.markdown("""
<style>


[data-testid="stAppViewContainer"] {
    background-color: #F4F6F8 !important;
}

h1, h2, h3, p, label {
    color: #1A1A1A !important;
}

[data-testid="stSidebar"] {
    background-color: #1C1F26;
}
[data-testid="stSidebar"] * {
    color: #EAEAEA !important;
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

input, textarea, select {
    background-color: white !important;
    color: black !important;
}

button[kind="primary"] {
    background-color: #064a3f !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

st.title("📊 Producción Científica")

# =========================
# UNIDADES ACADÉMICAS
# =========================

UNIDADES = [
    "Seleccionar unidad académica",
    "FDCSSL- Facultad de Derecho y Ciencias Sociales Sede San Luis",
    "FCMSL- Facultad de Ciencias Médicas Sede San Luis",
    "FCVSL- Facultad de Ciencias Veterinarias Sede San Luis",
    "FCEESL- Facultad de Ciencias Económicas y Empresariales Sede San Luis",
    "FBOSCO- Facultad Don Bosco",
    "FCEESJ- Facultad de Ciencias Económicas y Empresariales Sede San Juan",
    "FFyHSJ- Facultad de Filosofía y Humanidades",
    "ISDSM- Instituto Universitario Santa María",
    "ECRyPSJ- Escuela Cultura Religiosa y Pastoral",
    "FDCSSJ- Facultad de Derecho y Ciencias Sociales Sede San Juan",
    "FCMSJ- Facultad de Ciencias Médicas San Juan",
    "FEDSJ- Facultad de Educación",
    "ESEGSJ- Escuela de Seguridad",
    "FCQyTSJ- Facultad de Ciencias Químicas y Tecnológicas",
    "ISB- Instituto San Buenaventura",
    "Secretaría de Investigación",
    "Unidad de Vinculación Tecnológica",
]

# =========================
# TABS
# =========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📑 Revistas científicas",
    "📚 Libros / Capítulos",
    "🗂️ Repositorios",
    "🎓 Reuniones científicas",
    "📰 Diarios"
])

# =========================
# 1. REVISTAS
# =========================

with tab1:
    st.subheader("Carga de artículos científicos")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Título del artículo", key="titulo_revista")
        st.text_input("Autor/es", key="autores_revista")
        st.text_input("Revista", key="revista")

        indexacion = st.selectbox(
            "Indexación",
            ["Scopus", "WoS", "Scielo", "Otra"],
            key="indexacion"
        )

        if indexacion == "Otra":
            st.text_input(
                "Especificar indexación / base de datos",
                key="indexacion_otra"
            )

    with col2:
        st.text_input("DOI", key="doi")
        st.number_input("Año", 2000, 2030, 2025, key="año_revista")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_revista")

    if st.button("Guardar artículo", key="btn_revista"):
    
        titulo = st.session_state["titulo_revista"]
        autores = st.session_state["autores_revista"]
        revista = st.session_state["revista"]
        doi = st.session_state["doi"]
        anio = st.session_state["año_revista"]
        unidad = st.session_state["unidad_revista"]
    
        indexacion = st.session_state["indexacion"]
        if indexacion == "Otra":
            indexacion = st.session_state.get("indexacion_otra", "Otra")
    
        fila = [
            "Revista",
            titulo,
            autores,
            revista,
            doi,
            anio,
            unidad,
            indexacion
        ]
    
        sheet_pub.append_row(fila)
    
        st.success("Artículo guardado en Google Sheets")
       

# =========================
# 2. LIBROS
# =========================

with tab2:
    st.subheader("Carga de libros y capítulos")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Título", key="titulo_libro")
        st.text_input("Autor/es", key="autores_libro")
        st.selectbox("Tipo", ["Libro", "Capítulo de libro"], key="tipo_libro")

    with col2:
        st.text_input("Editorial", key="editorial")
        st.text_input("ISBN", key="isbn")
        st.number_input("Año", 2000, 2030, 2025, key="año_libro")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_libro")

    if st.button("Guardar libro/capítulo", key="btn_libro"):
    
        titulo = st.session_state["titulo_libro"]
        autores = st.session_state["autores_libro"]
        tipo_libro = st.session_state["tipo_libro"]   # Libro o Capítulo
        editorial = st.session_state["editorial"]
        isbn = st.session_state["isbn"]
        anio = st.session_state["año_libro"]
        unidad = st.session_state["unidad_libro"]
    
        fila = [
            tipo_libro,   # Tipo
            titulo,
            autores,
            "",           # Revista
            "",           # DOI
            anio,
            unidad,
            "",           # Indexación
            editorial,
            isbn,
            tipo_libro,   # Tipo publicación
            "", "", "", "", "", "", ""   # resto vacío
        ]
    
        sheet_pub.append_row(fila)
    
        st.success("Libro / capítulo guardado en Google Sheets")

# =========================
# 3. REPOSITORIOS
# =========================

with tab3:
    st.subheader("Carga en repositorios")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Título del trabajo", key="titulo_repo")
        st.text_input("Autor/es", key="autores_repo")
        st.selectbox("Tipo", [
            "Artículo",
            "Informe técnico",
            "Tesis",
            "Documento institucional"
        ], key="tipo_repo")

    with col2:
        repositorio = st.selectbox(
            "Repositorio",
            ["Repositorio UCCuyo", "CONICET", "Otro"],
            key="repositorio"
        )

        if repositorio == "Otro":
            st.text_input(
                "Especificar repositorio",
                key="repositorio_otro"
            )

        st.text_input("Link", key="link_repo")
        st.number_input("Año", 2000, 2030, 2025, key="año_repo")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_repo")

    if st.button("Guardar en repositorio", key="btn_repo"):
    
        titulo = st.session_state["titulo_repo"]
        autores = st.session_state["autores_repo"]
        tipo = st.session_state["tipo_repo"]   # Artículo, informe, tesis, etc.
        repositorio = st.session_state["repositorio"]
        link = st.session_state["link_repo"]
        anio = st.session_state["año_repo"]
        unidad = st.session_state["unidad_repo"]
    
        # Si es "Otro"
        if repositorio == "Otro":
            repositorio = st.session_state.get("repositorio_otro", "Otro")
    
        fila = [
            "Repositorio",
            titulo,
            autores,
            "", "",           # Revista, DOI
            anio,
            unidad,
            "",               # Indexación
            "", "",           # Editorial, ISBN
            tipo,             # Tipo publicación
            link,
            "", "", "", "",   # Evento, Lugar, Fecha, Resumen
            repositorio
        ]
    
        sheet_pub.append_row(fila)
    
        st.success("Registro en repositorio guardado en Google Sheets")

# =========================
# 4. REUNIONES CIENTÍFICAS
# =========================

with tab4:
    st.subheader("Reuniones científicas")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Nombre del evento", key="evento")
        st.selectbox("Tipo", [
            "Congreso",
            "Jornada",
            "Seminario",
            "Workshop"
        ], key="tipo_evento")
        st.selectbox("Rol", [
            "Expositor",
            "Asistente",
            "Organizador"
        ], key="rol")

    with col2:
        st.text_input("Título del trabajo", key="trabajo")
        st.text_input("Lugar", key="lugar")
        st.date_input("Fecha", key="fecha")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_evento")

    if st.button("Guardar evento", key="btn_evento"):
    
        evento = st.session_state["evento"]
        tipo_evento = st.session_state["tipo_evento"]   # Congreso, Jornada, etc.
        rol = st.session_state["rol"]
        trabajo = st.session_state["trabajo"]
        lugar = st.session_state["lugar"]
        fecha = st.session_state["fecha"]
        unidad = st.session_state["unidad_evento"]
    
        anio = fecha.year if fecha else ""
    
        fila = [
            "Evento",
            trabajo,
            "",               # Autores (no está en el form)
            "", "",           # Revista, DOI
            anio,
            unidad,
            "",               # Indexación
            "", "",           # Editorial, ISBN
            tipo_evento,      # Tipo publicación
            "",               # Link
            evento,
            lugar,
            str(fecha),
            "",               # Resumen
            ""                # Repositorio
        ]
    
        sheet_pub.append_row(fila)
    
        st.success("Evento guardado en Google Sheets")

# =========================
# 5. DIARIOS
# =========================

with tab5:
    st.subheader("Publicaciones en diarios")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Título del artículo", key="titulo_diario")
        st.text_input("Medio (ej: Diario de Cuyo)", key="medio")
        st.text_input("Autor/es", key="autor_diario")

    with col2:
        st.date_input("Fecha", key="fecha_diario")
        st.text_input("Link", key="link_diario")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_diario")

    st.text_area("Resumen", key="resumen_diario")

    if st.button("Guardar publicación en diario", key="btn_diario"):
    
        titulo = st.session_state["titulo_diario"]
        medio = st.session_state["medio"]
        autores = st.session_state["autor_diario"]
        fecha = st.session_state["fecha_diario"]
        link = st.session_state["link_diario"]
        unidad = st.session_state["unidad_diario"]
        resumen = st.session_state["resumen_diario"]
    
        anio = fecha.year if fecha else ""
    
        fila = [
            "Diario",
            titulo,
            autores,
            medio,          # va en Revista
            "",             # DOI
            anio,
            unidad,
            "",             # Indexación
            "", "",         # Editorial, ISBN
            "Artículo periodístico",
            link,
            "", "",         # Evento, Lugar
            str(fecha),
            resumen,
            ""              # Repositorio
        ]
    
        sheet_pub.append_row(fila)
    
        st.success("Publicación en diario guardada en Google Sheets")

# =========================
# FIN
# =========================

st.markdown("---")
st.caption("Sistema de Producción Científica - UCCuyo")
