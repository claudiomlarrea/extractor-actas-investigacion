# =========================
# 📝 FORMULARIO
# =========================

st.subheader("📋 Carga de Actas")

# 🔧 Estado
if "fecha" not in st.session_state:
    st.session_state.fecha = ""

if "acta" not in st.session_state:
    st.session_state.acta = ""

with st.form("form_acta", clear_on_submit=True):

    anio = st.text_input("Año", "2026")

    fecha = st.text_input("Fecha", key="fecha")

    acta = st.text_input("Número de Acta", key="acta")

    tipo = st.selectbox(
        "Tipo",
        [
            "Proyecto de Investigación",
            "Proyecto de Cátedra",
            "Informe Final",
            "Informe de Avance",
            "Jornada de Investigación",
            "Convocatoria de Investigación",
            "Convocatoria a Proyectos de investigación",
            "Creación de Semillero de Investigación",
            "Categorización Docente"
        ]
    )

    titulo = st.text_input("Título")
    descripcion = st.text_input("Descripción")
    director = st.text_input("Director")
    codirector = st.text_input("Codirector")

    unidad = st.selectbox(
        "Unidad Académica",
        [
            "FDCSSL- Facultad de Derecho y Ciencias Sociales Sede San Luis",
            "FCMSL- Facultad de Ciencias Médicas Sede San Luis",
            "FCVSL- Facultad de Veterinaria Sede San Luis",
            "FCEESL- Facultad de Ciencias Económicas y Empresariales Sede San Luis",
            "FBOSCO- Facultad Don Bosco de Enología y Ciencias de la Alimentación - Sede Rodeo del Medio",
            "FCEESJ- Facultad de Ciencias Económicas y Empresariales Sede San Juan",
            "FFyHSJ- Facultad de Filosofía y Humanidades",
            "ISDSM- Instituto Universitario Santa María",
            "ECRyPSJ- Escuela de Cultura Religiosa y Pastoral",
            "FDCSSJ- Facultad de Derecho y Ciencias Sociales Sede San Juan",
            "FCMSJ- Facultad de Ciencias Médicas San Juan",
            "FEDSJ- Facultad de Educación San Juan",
            "ESEGSJ- Escuela de Seguridad",
            "FCQyTSJ- Facultad de Ciencias Químicas y Tecnológicas San Juan",
            "ISB- Instituto San Buenaventura"
        ]
    )

    docente_categorizado = st.text_input("Docente categorizado")

    categoria_docente = st.selectbox(
        "Categoría Docente",
        [
            "Seleccionar",
            "Investigador Superior I",
            "Investigador Principal II",
            "Investigador Independiente III",
            "Investigador Asistente IV",
            "Investigador Adjunto V",
            "Becario/a de Iniciación VI",
            "Sin categorización / Externo"
        ]
    )

    submit = st.form_submit_button("Guardar en Google Sheets")
