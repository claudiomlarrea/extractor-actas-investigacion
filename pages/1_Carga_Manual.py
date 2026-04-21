import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO

st.title("📥 Carga Manual de Actas")

# =========================
# 🔐 CONEXIÓN GOOGLE
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
    st.write("📍 Archivo:", sh.url)

except Exception as e:
    st.error("❌ ERROR de conexión con Google Sheets")
    st.text(str(e))
    st.stop()

# =========================
# 📝 FORMULARIO
# =========================

anio = st.text_input("Año")
fecha = st.text_input("Fecha")
acta = st.text_input("Acta")

tipo = st.selectbox(
    "Tipo",
    [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Jornada de Investigación",
        "Convocatoria de Investigación",
        "Categorización Docente"
    ]
)

descripcion = st.text_area("Descripción")

# =========================
# 💾 GUARDAR
# =========================

if st.button("Guardar en Google Sheets"):

    fila = [
        acta,
        fecha,
        anio,
        tipo,
        descripcion
    ]

    try:
        sheet.append_row(fila)
        st.success("✅ Guardado en Google Sheets")

    except Exception as e:
        st.error("❌ Error al guardar")
        st.text(str(e))

# =========================
# 📄 GENERAR INFORME WORD
# =========================

st.markdown("---")
st.subheader("📄 Generar Orden del Día por Acta")

acta_busqueda = st.text_input("Ingrese número de Acta para generar informe")

if st.button("Generar Word"):

    try:
        data = sheet.get_all_values()
        encabezado = data[0]
        filas = data[1:]

        # Filtrar por acta
        filtradas = [f for f in filas if f[0] == acta_busqueda]

        if not filtradas:
            st.warning("No hay datos para esa acta")
        else:
            doc = Document()

            doc.add_heading(f"Orden del Día - Acta {acta_busqueda}", 0)

            for f in filtradas:
                tipo = f[3]
                descripcion = f[4]

                doc.add_heading(tipo, level=2)
                doc.add_paragraph(descripcion)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="📥 Descargar Informe Word",
                data=buffer,
                file_name=f"Acta_{acta_busqueda}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    except Exception as e:
        st.error("Error al generar Word")
        st.text(str(e))
