import streamlit as st

st.set_page_config(page_title="Producción Científica", layout="wide")

st.title("📊 Producción Científica")

# =========================
# UNIDADES ACADÉMICAS
# =========================

UNIDADES = [
    "FDCSSL- Facultad de Derecho y Ciencias Sociales Sede San Luis",
    "FCMSL- Facultad de Ciencias Médicas Sede San Luis",
    "FCVSL- Facultad de Veterinaria Sede San Luis",
    "FCEESL- Facultad de Ciencias Económicas y Empresariales Sede San Luis",
    "FBOSCO- Facultad Don Bosco",
    "FCEESJ- Facultad de Ciencias Económicas San Juan",
    "FFyHSJ- Facultad de Filosofía y Humanidades",
    "ISDSM- Instituto Universitario Santa María",
    "ECRyPSJ- Escuela Cultura Religiosa",
    "FDCSSJ- Facultad de Derecho San Juan",
    "FCMSJ- Facultad de Ciencias Médicas San Juan",
    "FEDSJ- Facultad de Educación",
    "ESEGSJ- Escuela de Seguridad",
    "FCQyTSJ- Facultad de Ciencias Químicas",
    "ISB- Instituto San Buenaventura"
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
        st.success("Artículo registrado")

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
        st.success("Registro guardado")

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
        st.success("Registro guardado")

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
        st.success("Evento registrado")

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
        st.success("Publicación registrada")

# =========================
# FIN
# =========================

st.markdown("---")
st.caption("Sistema de Producción Científica - UCCuyo")
