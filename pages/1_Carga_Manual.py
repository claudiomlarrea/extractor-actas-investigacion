import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO
from collections import defaultdict

# =========================
# 🎯 TÍTULO
# =========================

st.title("📥 Sistema de Actas - Consejo de Investigación")

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

    st.success("✅ Conectado a Google Sheets")

    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={sheet.id}"
    st.write("📍 Archivo:", sheet_url)

except Exception as e:
    st.error("❌ Error de conexión")
    st.text(str(e))
    st.stop()

# =========================
# 🧠 SESSION STATE
# =========================

if "fecha" not in st.session_state:
    st.session_state.fecha = ""

if "acta" not in st.session_state:
    st.session_state.acta = ""

# =========================
# 📝 FORMULARIO
# =========================

st.subheader("📋 Carga de Actas")

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

# =========================
# 💾 GUARDAR
# =========================

if submit:

    if acta.strip() == "":
        st.warning("⚠️ Debe ingresar número de acta")
        st.stop()

    if tipo == "Categorización Docente":
        if docente_categorizado.strip() == "" or categoria_docente == "Seleccionar":
            st.warning("⚠️ Debe completar docente y categoría")
            st.stop()

    fila = [
        acta.strip(),
        fecha.strip(),
        anio.strip(),
        tipo.strip(),
        titulo.strip(),
        descripcion.strip(),
        director.strip(),
        codirector.strip(),
        docente_categorizado.strip() if tipo == "Categorización Docente" else "",
        categoria_docente.strip() if tipo == "Categorización Docente" else "",
        unidad.strip()
    ]

    try:
        sheet.append_row(fila)
        st.success("✅ Registro guardado correctamente")

        # limpiar campos
        st.session_state.fecha = ""
        st.session_state.acta = ""

    except Exception as e:
        st.error("❌ Error al guardar")
        st.text(str(e))

# =========================
# 📄 GENERAR ORDEN DEL DÍA
# =========================

st.markdown("---")
st.subheader("📄 Generar Orden del Día Oficial")

acta_buscar = st.text_input("Ingrese número de Acta")

if st.button("Generar Orden del Día"):

    data = sheet.get_all_records()

    filas = [
        f for f in data
        if str(f.get("ACTA", "")).strip() == str(acta_buscar).strip()
    ]

    if not filas:
        st.warning("No hay registros para esa acta")
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

            if tipo == "Categorización Docente":

                docente = item.get("Docente categorizado", "")
                categoria = item.get("Categoría Docente", "")
                unidad = item.get("UNIDAD ACADÉMICA", "")

                doc.add_paragraph(f"    {contador}.{sub} {docente}")

                if categoria:
                    doc.add_paragraph(f"       Categoría: {categoria}")

                if unidad:
                    doc.add_paragraph(f"       Unidad Académica: {unidad}")

            else:

                titulo = item.get("TITULO", "")
                descripcion = item.get("DESCRIPCIÓN", "")
                director = item.get("DIRECTOR", "")
                codirector = item.get("CODIRECTOR", "")
                unidad = item.get("UNIDAD ACADÉMICA", "")

                if titulo:
                    doc.add_paragraph(titulo)

                if descripcion:
                    doc.add_paragraph(descripcion)

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
        "⬇️ Descargar Orden del Día",
        buffer,
        file_name=f"Orden_del_Dia_Acta_{acta_buscar}.docx"
    )

    st.success("✅ Documento generado correctamente")
