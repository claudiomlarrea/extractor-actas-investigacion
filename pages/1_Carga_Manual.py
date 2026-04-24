import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO

# =========================
# ⚙ CONFIGURACIÓN
# =========================

st.set_page_config(
    page_title="Consejo de Investigación",
    layout="wide"
)

# =========================
# 🎨 ESTILO
# =========================


col1, col2 = st.columns([1, 6])

with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Logo_placeholder.png/300px-Logo_placeholder.png", width=2000)

with col2:
    st.markdown("""
    <div style='background-color:#064a3f; padding:20px; border-radius:10px'>
        <h2 style='color:white; margin:0'>
            Universidad Católica de Cuyo
        </h2>
        <p style='color:white; margin:0'>
            Secretaría de Investigación
        </p>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 🟢 HEADER INSTITUCIONAL
# =========================


# =========================
# 🧠 TÍTULO
# =========================

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
# 📅 MAPA ACTAS → FECHAS
# =========================

actas_dict = {
    187: {"mes": "Febrero", "fecha": "20/02/2026"},
    188: {"mes": "Marzo", "fecha": "20/03/2026"},
    189: {"mes": "Abril", "fecha": "24/04/2026"},
    190: {"mes": "Mayo", "fecha": "22/05/2026"},
    191: {"mes": "Junio", "fecha": "19/06/2026"},
    192: {"mes": "Julio", "fecha": "17/07/2026"},
    193: {"mes": "Agosto", "fecha": "21/08/2026"},
    194: {"mes": "Septiembre", "fecha": "18/09/2026"},
    195: {"mes": "Octubre", "fecha": "16/10/2026"},
    196: {"mes": "Noviembre", "fecha": "20/11/2026"},
    197: {"mes": "Diciembre", "fecha": "18/12/2026"},
}

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

    anio = st.text_input("Año", "2026")

    numero_acta = st.selectbox(
        "Número de Acta",
        options=list(actas_dict.keys())
    )

    fecha = st.selectbox(
        "Fecha",
        options=[actas_dict[numero_acta]["fecha"]]
    )

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

    director = st.text_input("Director")
    categoria_director = st.selectbox("Categoría del Director", categoria_opciones)

    codirector = st.text_input("Codirector")
    categoria_codirector = st.selectbox("Categoría del Codirector", categoria_opciones)

    equipo = st.text_area("Equipo de investigación")

    unidad = st.selectbox(
        "Unidad Académica",
        [
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
    )

    resolucion_cd = st.text_input("Resolución del Consejo Directivo")
    instituto = st.text_input("Instituto de Investigación")
    catedra = st.text_input("Cátedra")

    financiamiento = st.text_input("Financiamiento")
    alumnos = st.text_input("Alumnos")

    docente_categorizado = ""
    categoria_docente = ""

    if tipo == "Categorización Docente":
        st.markdown("### Datos de Categorización")
        docente_categorizado = st.text_input("Docente categorizado")
        categoria_docente = st.selectbox("Categoría docente", categoria_opciones)

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

    doc.add_paragraph("CONSEJO DE INVESTIGACIÓN")
    doc.add_paragraph("UNIVERSIDAD CATÓLICA DE CUYO")
    doc.add_paragraph("")
    doc.add_paragraph("ORDEN DEL DÍA")
    doc.add_paragraph(f"Acta Nº {acta_buscar}")
    doc.add_paragraph(f"Fecha: {filas[0].get('FECHA', '')}")
    doc.add_paragraph("")

    contador = 1

    for f in filas:

        doc.add_paragraph(f"{contador}. {f.get('TIPO', '')}")
        doc.add_paragraph(f"   Título: {f.get('TITULO', '')}")

        if f.get("DESCRIPCIÓN"):
            doc.add_paragraph(f"   Descripción: {f.get('DESCRIPCIÓN')}")

        if f.get("DIRECTOR"):
            director = f.get("DIRECTOR")
            cat_dir = f.get("CAT_DIRECTOR", "")
            if cat_dir:
                doc.add_paragraph(f"   Director: {director} ({cat_dir})")
            else:
                doc.add_paragraph(f"   Director: {director}")

        if f.get("CODIRECTOR"):
            codir = f.get("CODIRECTOR")
            cat_codir = f.get("CAT_CODIRECTOR", "")
            if cat_codir:
                doc.add_paragraph(f"   Codirector: {codir} ({cat_codir})")
            else:
                doc.add_paragraph(f"   Codirector: {codir}")

        if f.get("EQUIPO"):
            doc.add_paragraph(f"   Equipo: {f.get('EQUIPO')}")

        if f.get("RESOLUCIÓN DEL CONSEJO DIRECTIVO"):
            doc.add_paragraph(f"   Resolución CD: {f.get('RESOLUCIÓN DEL CONSEJO DIRECTIVO')}")

        if f.get("INSTITUTO DE INVESTIGACIÓN"):
            doc.add_paragraph(f"   Instituto: {f.get('INSTITUTO DE INVESTIGACIÓN')}")

        if f.get("CÁTEDRA"):
            doc.add_paragraph(f"   Cátedra: {f.get('CÁTEDRA')}")

        # 💰 FINANCIAMIENTO BIEN FORMATEADO
        if f.get("FINANCIAMIENTO"):
            fin = f.get("FINANCIAMIENTO")
            try:
                fin = str(fin).replace(".", "")
                fin = int(float(fin))
                fin = f"{fin:,}".replace(",", ".")
            except:
                pass
            doc.add_paragraph(f"   Financiamiento: {fin}")

        if f.get("ALUMNOS"):
            doc.add_paragraph(f"   Alumnos: {f.get('ALUMNOS')}")

        if f.get("UNIDAD ACADÉMICA"):
            doc.add_paragraph(f"   Unidad Académica: {f.get('UNIDAD ACADÉMICA')}")

        doc.add_paragraph("")
        contador += 1

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "Descargar Orden del Día",
        buffer,
        file_name=f"Orden_{acta_buscar}.docx"
    )
