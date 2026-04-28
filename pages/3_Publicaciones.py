import streamlit as st

st.set_page_config(page_title="Producción Científica", layout="wide")

st.title("📊 Producción Científica")

# =========================
# Tabs
# =========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📑 Revistas científicas",
    "📚 Libros / Capítulos",
    "🗂️ Repositorios",
    "🎓 Reuniones científicas",
    "📰 Diarios"
])

# =========================
# 1. REVISTAS CIENTÍFICAS
# =========================

with tab1:
    st.subheader("Carga de artículos científicos")

    col1, col2 = st.columns(2)

    with col1:
        titulo = st.text_input("Título del artículo", key="titulo_revista")
        autores = st.text_input("Autor/es", key="autores_revista")
        revista = st.text_input("Revista", key="revista")
        indexacion = st.selectbox("Indexación", ["Scopus", "WoS", "Scielo", "Otra"], key="indexacion")

    with col2:
        doi = st.text_input("DOI", key="doi")
        año = st.number_input("Año", 2000, 2030, 2025, key="año_revista")
        unidad = st.text_input("Unidad Académica", key="unidad_revista")

    if st.button("Guardar artículo", key="btn_revista"):
        st.success("Artículo registrado")

# =========================
# 2. LIBROS / CAPÍTULOS
# =========================

with tab2:
    st.subheader("Carga de libros y capítulos")

    col1, col2 = st.columns(2)

    with col1:
        titulo_libro = st.text_input("Título", key="titulo_libro")
        autores_libro = st.text_input("Autor/es", key="autores_libro")
        tipo = st.selectbox("Tipo", ["Libro", "Capítulo de libro"], key="tipo_libro")

    with col2:
        editorial = st.text_input("Editorial", key="editorial")
        isbn = st.text_input("ISBN", key="isbn")
        año_libro = st.number_input("Año", 2000, 2030, 2025, key="año_libro")
        unidad_libro = st.text_input("Unidad Académica", key="unidad_libro")

    if st.button("Guardar libro/capítulo", key="btn_libro"):
        st.success("Registro guardado")

# =========================
# 3. REPOSITORIOS
# =========================

with tab3:
    st.subheader("Carga en repositorios")

    col1, col2 = st.columns(2)

    with col1:
        titulo_repo = st.text_input("Título del trabajo", key="titulo_repo")
        autores_repo = st.text_input("Autor/es", key="autores_repo")
        tipo_repo = st.selectbox("Tipo", [
            "Artículo",
            "Informe técnico",
            "Tesis",
            "Documento institucional"
        ], key="tipo_repo")

    with col2:
        repositorio = st.selectbox("Repositorio", [
            "Repositorio UCCuyo",
            "CONICET",
            "Otro"
        ], key="repositorio")
        link_repo = st.text_input("Link", key="link_repo")
        año_repo = st.number_input("Año", 2000, 2030, 2025, key="año_repo")
        unidad_repo = st.text_input("Unidad Académica", key="unidad_repo")

    if st.button("Guardar en repositorio", key="btn_repo"):
        st.success("Registro guardado")

# =========================
# 4. REUNIONES CIENTÍFICAS
# =========================

with tab4:
    st.subheader("Reuniones científicas")

    col1, col2 = st.columns(2)

    with col1:
        evento = st.text_input("Nombre del evento", key="evento")
        tipo_evento = st.selectbox("Tipo", [
            "Congreso",
            "Jornada",
            "Seminario",
            "Workshop"
        ], key="tipo_evento")
        rol = st.selectbox("Rol", [
            "Expositor",
            "Asistente",
            "Organizador"
        ], key="rol")

    with col2:
        trabajo = st.text_input("Título del trabajo", key="trabajo")
        lugar = st.text_input("Lugar", key="lugar")
        fecha = st.date_input("Fecha", key="fecha")
        unidad_evento = st.text_input("Unidad Académica", key="unidad_evento")

    if st.button("Guardar evento", key="btn_evento"):
        st.success("Evento registrado")

# =========================
# 5. DIARIOS (AL FINAL)
# =========================

with tab5:
    st.subheader("Publicaciones en diarios")

    col1, col2 = st.columns(2)

    with col1:
        titulo_diario = st.text_input("Título del artículo", key="titulo_diario")
        medio = st.text_input("Medio (ej: Diario de Cuyo)", key="medio")
        autor_diario = st.text_input("Autor/es", key="autor_diario")

    with col2:
        fecha_diario = st.date_input("Fecha", key="fecha_diario")
        link_diario = st.text_input("Link", key="link_diario")
        unidad_diario = st.text_input("Unidad Académica", key="unidad_diario")

    resumen = st.text_area("Resumen", key="resumen_diario")

    if st.button("Guardar publicación en diario", key="btn_diario"):
        st.success("Publicación registrada")

# =========================
# FIN
# =========================

st.markdown("---")
st.caption("Sistema de Producción Científica - UCCuyo")
