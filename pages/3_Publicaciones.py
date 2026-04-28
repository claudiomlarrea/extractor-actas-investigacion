import streamlit as st
import pandas as pd

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
        titulo = st.text_input("Título del artículo")
        autores = st.text_input("Autor/es")
        revista = st.text_input("Revista")
        indexacion = st.selectbox("Indexación", ["Scopus", "WoS", "Scielo", "Otra"])

    with col2:
        doi = st.text_input("DOI")
        año = st.number_input("Año", 2000, 2030, 2025)
        unidad = st.text_input("Unidad Académica")

    if st.button("Guardar artículo"):
        st.success("Artículo registrado (pendiente conexión a base de datos)")

# =========================
# 2. LIBROS / CAPÍTULOS
# =========================

with tab2:
    st.subheader("Carga de libros y capítulos")

    col1, col2 = st.columns(2)

    with col1:
        titulo_libro = st.text_input("Título")
        autores_libro = st.text_input("Autor/es")
        tipo = st.selectbox("Tipo", ["Libro", "Capítulo de libro"])

    with col2:
        editorial = st.text_input("Editorial")
        isbn = st.text_input("ISBN")
        año_libro = st.number_input("Año", 2000, 2030, 2025)
        unidad_libro = st.text_input("Unidad Académica")

    if st.button("Guardar libro/capítulo"):
        st.success("Registro guardado")

# =========================
# 3. REPOSITORIOS
# =========================

with tab3:
    st.subheader("Carga en repositorios")

    col1, col2 = st.columns(2)

    with col1:
        titulo_repo = st.text_input("Título del trabajo")
        autores_repo = st.text_input("Autor/es")
        tipo_repo = st.selectbox("Tipo", [
            "Artículo",
            "Informe técnico",
            "Tesis",
            "Documento institucional"
        ])

    with col2:
        repositorio = st.selectbox("Repositorio", [
            "Repositorio UCCuyo",
            "CONICET",
            "Otro"
        ])
        link_repo = st.text_input("Link")
        año_repo = st.number_input("Año", 2000, 2030, 2025)
        unidad_repo = st.text_input("Unidad Académica")

    if st.button("Guardar en repositorio"):
        st.success("Registro guardado")

# =========================
# 4. REUNIONES CIENTÍFICAS
# =========================

with tab4:
    st.subheader("Reuniones científicas")

    col1, col2 = st.columns(2)

    with col1:
        evento = st.text_input("Nombre del evento")
        tipo_evento = st.selectbox("Tipo", [
            "Congreso",
            "Jornada",
            "Seminario",
            "Workshop"
        ])
        rol = st.selectbox("Rol", [
            "Expositor",
            "Asistente",
            "Organizador"
        ])

    with col2:
        trabajo = st.text_input("Título del trabajo")
        lugar = st.text_input("Lugar")
        fecha = st.date_input("Fecha")
        unidad_evento = st.text_input("Unidad Académica")

    if st.button("Guardar evento"):
        st.success("Evento registrado")

# =========================
# 5. DIARIOS (AL FINAL)
# =========================

with tab5:
    st.subheader("Publicaciones en diarios")

    col1, col2 = st.columns(2)

    with col1:
        titulo_diario = st.text_input("Título del artículo")
        medio = st.text_input("Medio (ej: Diario de Cuyo)")
        autor_diario = st.text_input("Autor/es")

    with col2:
        fecha_diario = st.date_input("Fecha")
        link_diario = st.text_input("Link")
        unidad_diario = st.text_input("Unidad Académica")

    resumen = st.text_area("Resumen")

    if st.button("Guardar publicación en diario"):
        st.success("Publicación registrada")

# =========================
# FIN
# =========================

st.markdown("---")
st.caption("Sistema de Producción Científica - UCCuyo")
