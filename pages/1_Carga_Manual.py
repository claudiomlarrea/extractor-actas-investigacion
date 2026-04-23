import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO

st.title("Sistema de Actas - Consejo de Investigación")

# =========================
# 🔐 CONEXIÓN
# =========================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

SHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"
sh = client.open_by_key(SHEET_ID)
sheet = sh.worksheet("Hoja 2")

st.success("Conectado a Google Sheets")

# =========================
# 📝 FORMULARIO
# =========================

st.subheader("Carga de Actas")

categoria_opciones = [
    "Seleccionar",
    "Investigador Superior I",
    "Investigador Principal II",
    "Investigador Independiente III",
    "Investigador Asistente IV",
    "Investigador Adjunto V",
    "Becario/a de Iniciación VI",
    "Sin categorización / Externo"
]

with st.form("form_acta", clear_on_submit=True):

    # -------------------------
    # DATOS BÁSICOS
    # -------------------------
    anio = st.text_input("Año", "2026")
    fecha = st.text_input("Fecha")
    acta = st.text_input("Número de Acta")

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
    descripcion = st.text_area("Descripción")

    # -------------------------
    # EQUIPO
    # -------------------------
    director = st.text_input("Director")
    categoria_director = st.selectbox("Categoría del Director", categoria_opciones)

    codirector = st.text_input("Codirector")
    categoria_codirector = st.selectbox("Categoría del Codirector", categoria_opciones)

    equipo = st.text_area("Equipo de investigación")

    # -------------------------
    # INSTITUCIONAL
    # -------------------------
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

    resolucion_cd = st.text_input("Resolución del Consejo Directivo")
    instituto = st.text_input("Instituto de Investigación")
    catedra = st.text_input("Cátedra")

    # -------------------------
    # EXTRAS
    # -------------------------
    financiamiento = st.text_input("Financiamiento")
    alumnos = st.text_input("Alumnos")
    archivo = st.file_uploader("Archivo adjunto")

    # -------------------------
    # CATEGORIZACIÓN DOCENTE (CONDICIONAL)
    # -------------------------
    docente_categorizado = ""
    categoria_docente = ""

    if tipo == "Categorización Docente":
        st.markdown("### Datos de Categorización")

        docente_categorizado = st.text_input("Docente categorizado")

        categoria_docente = st.selectbox(
            "Categoría docente",
            categoria_opciones
        )

    submit = st.form_submit_button("Guardar en Google Sheets")

# =========================
# 💾 GUARDAR
# =========================

if submit:

    if acta.strip() == "":
        st.warning("Debe ingresar número de acta")
        st.stop()

    fila = [
        acta,
        fecha,
        anio,
        tipo,
        titulo,
        descripcion,
        director,
        "" if categoria_director == "Seleccionar" else categoria_director,
        codirector,
        "" if categoria_codirector == "Seleccionar" else categoria_codirector,
        equipo,
        docente_categorizado,
        "" if categoria_docente == "Seleccionar" else categoria_docente,
        unidad,
        resolucion_cd,
        instituto,
        catedra,
        financiamiento,
        alumnos
    ]

    try:
        sheet.append_row(fila)
        st.success("Registro guardado correctamente")

    except Exception as e:
        st.error("Error al guardar")
        st.text(str(e))

# =========================
# 📄 ORDEN DEL DÍA
# =========================

st.markdown("---")
st.subheader("Generar Orden del Día")

acta_buscar = st.text_input("Ingrese número de Acta")

if st.button("Generar Orden del Día"):

    try:
        data = sheet.get_all_records()
    except Exception as e:
        st.error("Error leyendo datos")
        st.text(str(e))
        st.stop()

   filas = [
    f for f in data
    if str(f.get("ACTA", "")).strip() == acta_buscar.strip()
]

if not filas:
    st.warning("No hay registros")
    st.stop()

doc = Document()

# ENCABEZADO
doc.add_paragraph("CONSEJO DE INVESTIGACIÓN")
doc.add_paragraph("UNIVERSIDAD CATÓLICA DE CUYO")
doc.add_paragraph("")

doc.add_paragraph("ORDEN DEL DÍA")
doc.add_paragraph(f"Acta Nº {acta_buscar}")
doc.add_paragraph(f"Fecha: {filas[0].get('FECHA', '')}")
doc.add_paragraph("")

# CONTENIDO
contador = 1

for f in filas:

    doc.add_paragraph(f"{contador}. {f.get('TIPO', '')}")

    doc.add_paragraph(f"   Título: {f.get('TITULO', '')}")

    if f.get("DIRECTOR"):
        doc.add_paragraph(f"   Director: {f.get('DIRECTOR')}")

    if f.get("CODIRECTOR"):
        doc.add_paragraph(f"   Codirector: {f.get('CODIRECTOR')}")

    if f.get("UNIDAD ACADÉMICA"):
        doc.add_paragraph(f"   Unidad Académica: {f.get('UNIDAD ACADÉMICA')}")

    doc.add_paragraph("")

    contador += 1

# EXPORTAR
buffer = BytesIO()
doc.save(buffer)
buffer.seek(0)

st.download_button(
    "Descargar Orden del Día",
    buffer,
    file_name=f"Orden_{acta_buscar}.docx"
)
