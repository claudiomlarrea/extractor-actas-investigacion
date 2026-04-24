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
# 🎨 HEADER
# =========================

col1, col2 = st.columns([1, 6])

with col1:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Logo_placeholder.png/300px-Logo_placeholder.png",
        width=120
    )

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
# 📅 MAPA ACTAS
# =========================

actas_dict = {
    187: {"mes": "Febrero"},
    188: {"mes": "Marzo"},
    189: {"mes": "Abril"},
    190: {"mes": "Mayo"},
    191: {"mes": "Junio"},
    192: {"mes": "Julio"},
    193: {"mes": "Agosto"},
    194: {"mes": "Septiembre"},
    195: {"mes": "Octubre"},
    196: {"mes": "Noviembre"},
    197: {"mes": "Diciembre"},
}

fechas_actas = {
    187: "19 de Febrero 2026",
    188: "19 de Marzo 2026",
    189: "16 de Abril 2026",
    190: "21 de Mayo 2026",
    191: "18 de Junio 2026",
    192: "23 de Julio 2026",
    193: "20 de Agosto 2026",
    194: "15 de Septiembre 2026",
    195: "22 de Octubre 2026",
    196: "19 de Noviembre 2026",
    197: "10 de Diciembre 2026"
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

    # ✅ ACTA + MES
    acta_label = st.selectbox(
        "Número de Acta",
        options=[
            f"Acta N°{n} - {actas_dict[n]['mes']}"
            for n in actas_dict.keys()
        ]
    )

    numero_acta = int(acta_label.split(" ")[1].replace("N°", ""))

    # ✅ FECHA AUTOMÁTICA
    fecha = fechas_actas[numero_acta]

    fecha = st.selectbox(
        "Fecha",
        options=list(fechas_actas.values()),
        index=list(fechas_actas.values()).index(fechas_actas[numero_acta])
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

    submit = st.form_submit_button("Guardar en Google Sheets")

# =========================
# 💾 GUARDAR
# =========================

if submit:

    fila = [
        numero_acta,
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
# 📄 GENERAR ORDEN DEL DÍA
# =========================

if submit:

    fila = [
        numero_acta,
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
    # 📄 CREAR WORD
    # =========================

    doc = Document()

    doc.add_heading('Consejo de Investigación', 0)
    doc.add_paragraph(f'Acta N° {numero_acta}')
    doc.add_paragraph(f'Fecha: {fecha}')
    doc.add_paragraph('')

    doc.add_heading('Orden del Día', level=1)

    doc.add_paragraph(f"Tipo: {tipo}")
    doc.add_paragraph(f"Título: {titulo}")
    doc.add_paragraph(f"Descripción: {descripcion}")
    doc.add_paragraph(f"Director: {director}")
    doc.add_paragraph(f"Unidad Académica: {unidad}")

    doc.add_paragraph('')

    # =========================
    # 📥 DESCARGA
    # =========================

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="Descargar Orden del Día en Word",
        data=buffer,
        file_name=f"Acta_{numero_acta}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
