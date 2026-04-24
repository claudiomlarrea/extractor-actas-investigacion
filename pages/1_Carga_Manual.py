import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO

# =========================
# ⚙ CONFIGURACIÓN
# =========================

st.set_page_config(page_title="Consejo de Investigación", layout="wide")

# =========================
# 🎨 HEADER
# =========================

col1, col2 = st.columns([1, 6])

with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Logo_placeholder.png/300px-Logo_placeholder.png", width=120)

with col2:
    st.markdown("""
    <div style='background-color:#064a3f; padding:20px; border-radius:10px'>
        <h2 style='color:white; margin:0'>Universidad Católica de Cuyo</h2>
        <p style='color:white; margin:0'>Secretaría de Investigación</p>
    </div>
    """, unsafe_allow_html=True)

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
sheet = client.open_by_key(SHEET_ID).worksheet("Hoja 2")

st.success("Conectado a Google Sheets")

# =========================
# 📅 DATOS ACTAS
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

with st.form("form_acta", clear_on_submit=True):

    anio = st.text_input("Año", "2026")

    acta_label = st.selectbox(
        "Número de Acta",
        options=[f"Acta N°{n} - {actas_dict[n]['mes']}" for n in actas_dict]
    )

    numero_acta = int(acta_label.split(" ")[1].replace("N°", ""))

    fecha = fechas_actas[numero_acta]

    st.text_input("Fecha", value=fecha, disabled=True)

    tipo = st.selectbox("Tipo", [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance",
        "Jornada de Investigación",
        "Convocatoria de Investigación",
        "Convocatoria a Proyectos de investigación",
        "Creación de Semillero de Investigación",
        "Categorización Docente"
    ])

    titulo = st.text_input("Título")
    descripcion = st.text_area("Descripción")

    director = st.text_input("Director")
    codirector = st.text_input("Codirector")
    equipo = st.text_area("Equipo")

    unidad = st.text_input("Unidad Académica")
    resolucion_cd = st.text_input("Resolución CD")
    instituto = st.text_input("Instituto")
    catedra = st.text_input("Cátedra")
    financiamiento = st.text_input("Financiamiento")
    alumnos = st.text_input("Alumnos")

    submit = st.form_submit_button("Guardar en Google Sheets")

# =========================
# 💾 GUARDAR (UNA SOLA VEZ)
# =========================

if submit:

    fila = [
        numero_acta, fecha, anio, tipo, titulo, descripcion,
        director, codirector, equipo, unidad,
        resolucion_cd, instituto, catedra, financiamiento, alumnos
    ]

    sheet.append_row(fila)
    st.success("Registro guardado correctamente")

# =========================
# 📄 GENERAR ORDEN DEL DÍA
# =========================

st.markdown("## 📄 Generar Orden del Día")

acta_word = st.selectbox(
    "Seleccionar Acta",
    options=list(actas_dict.keys())
)

if st.button("Generar Word"):

    datos = sheet.get_all_records()

    acta_num = acta_word

    registros = [r for r in datos if str(r["numero_acta"]) == str(acta_num)]

    if not registros:
        st.warning("No hay registros para esta acta")
    else:
        doc = Document()

        doc.add_heading('Consejo de Investigación', 0)
        doc.add_paragraph(f'Acta N° {acta_num}')
        doc.add_paragraph(f'Fecha: {fechas_actas[acta_num]}')

        doc.add_heading('Orden del Día', level=1)

        for i, r in enumerate(registros, 1):
            doc.add_paragraph(f"{i}. {r['TIPO']} - {r['TITULO']}")

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "Descargar Word",
            data=buffer,
            file_name=f"Acta_{acta_word}.docx"
        )
