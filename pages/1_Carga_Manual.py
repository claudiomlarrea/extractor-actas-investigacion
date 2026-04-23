import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO
from collections import defaultdict

# =========================
# 🎯 TÍTULO
# =========================

st.title("Sistema de Actas - Consejo de Investigación")

# =========================
# 🔐 CONEXIÓN
# =========================

try:
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

    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={sheet.id}"
    st.write("Archivo:", sheet_url)

except Exception as e:
    st.error("Error de conexión")
    st.text(str(e))
    st.stop()

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

    # Básicos
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
            "Categorización Docente",
            "Otros"
        ]
    )

    titulo = st.text_input("Título")
    descripcion = st.text_area("Descripción")

    # Equipo
    director = st.text_input("Director")
    categoria_director = st.selectbox("Categoría del Director", categoria_opciones)

    codirector = st.text_input("Codirector")
    categoria_codirector = st.selectbox("Categoría del Codirector", categoria_opciones)

    equipo = st.text_area("Equipo de investigación")

    # Institucional
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

    # Extras
    financiamiento = st.text_input("Financiamiento")
    alumnos = st.text_input("Alumnos")
    archivo = st.file_uploader("Archivo adjunto")

    # Categorización docente (solo si corresponde)
    docente_categorizado = ""
    categoria_docente = ""

    if tipo == "Categorización Docente":
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
        acta.strip(),
        fecha.strip(),
        anio.strip(),
        tipo.strip(),
        titulo.strip(),
        descripcion.strip(),
        director.strip(),
        categoria_director.strip(),
        codirector.strip(),
        categoria_codirector.strip(),
        equipo.strip(),
        docente_categorizado.strip(),
        categoria_docente.strip(),
        unidad.strip(),
        resolucion_cd.strip(),
        instituto.strip(),
        catedra.strip(),
        financiamiento.strip(),
        alumnos.strip()
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

    data = sheet.get_all_records()

    filas = [
        f for f in data
        if str(f.get("ACTA", "")).strip() == str(acta_buscar).strip()
    ]

    if not filas:
        st.warning("No hay registros")
        st.stop()

    fecha_doc = filas[0]["FECHA"]
    agrupado = defaultdict(list)

    for fila in filas:
        agrupado[fila["TIPO"]].append(fila)

    doc = Document()

    doc.add_paragraph("UNIVERSIDAD CATÓLICA DE CUYO").runs[0].bold = True
    doc.add_paragraph("Consejo de Investigación")
    doc.add_paragraph("")
    doc.add_paragraph("ORDEN DEL DÍA").runs[0].bold = True
    doc.add_paragraph(f"Acta Nº {acta_buscar}")
    doc.add_paragraph(f"Fecha: {fecha_doc}")
    doc.add_paragraph("")

    contador = 1

    for tipo, items in agrupado.items():

        doc.add_paragraph(f"{contador}. {tipo}")
        sub = 1

        for item in items:

            titulo = item.get("TITULO", "")
            director = item.get("DIRECTOR", "")
            codirector = item.get("CODIRECTOR", "")
            unidad = item.get("UNIDAD ACADÉMICA", "")

            if titulo:
                doc.add_paragraph(titulo)

            if director:
                doc.add_paragraph(f"    {contador}.{sub} Director: {director}")

            if codirector:
                doc.add_paragraph(f"       Codirector: {codirector}")

            if unidad:
                doc.add_paragraph(f"       Unidad Académica: {unidad}")

            sub += 1

        doc.add_paragraph("")
        contador += 1

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "Descargar Orden del Día",
        buffer,
        file_name=f"Orden_del_Dia_{acta_buscar}.docx"
    )

    st.success("Documento generado")
