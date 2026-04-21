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
        "Informe Final",
        "Informe de Avance",
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

    if acta.strip() == "":
        st.warning("⚠️ Debe ingresar número de acta")
    else:
        fila = [
            acta,
            fecha,
            anio,
            tipo,
            descripcion
        ]

        try:
            sheet.append_row(fila)
            st.success("✅ Guardado correctamente")

        except Exception as e:
            st.error("❌ Error al guardar")
            st.text(str(e))

# =========================
# 📄 GENERAR WORD
# =========================

st.markdown("---")
st.subheader("📄 Generar Orden del Día")

acta_buscar = st.text_input("Número de Acta")

if st.button("Generar Orden del Día"):

    try:
        data = sheet.get_all_records()

        # FILTRAR POR ACTA
        filas = [f for f in data if str(f["Acta"]) == str(acta_buscar)]

        if not filas:
            st.warning("No hay datos para esa acta")
            st.stop()

        # AGRUPAR POR TIPO
        agrupado = {}
        for fila in filas:
            tipo_f = fila["Tipo"]
            desc = fila["Descripción"]

            if tipo_f not in agrupado:
                agrupado[tipo_f] = []

            agrupado[tipo_f].append(desc)

        # =========================
        # 📄 CREAR WORD INSTITUCIONAL
        # =========================

        doc = Document()

        doc.add_heading("ORDEN DEL DÍA", 0)
        doc.add_paragraph("Consejo de Investigación")
        doc.add_paragraph(f"Acta Nº {acta_buscar}")

        fecha_doc = filas[0].get("Fecha", "")
        doc.add_paragraph(f"Fecha: {fecha_doc}")
        doc.add_paragraph("")

        orden_general = 1

        orden_tipos = [
            "Proyecto de Investigación",
            "Proyecto de Cátedra",
            "Jornada de Investigación",
            "Convocatoria de Investigación",
            "Informe de Avance",
            "Informe Final",
            "Categorización Docente"
        ]

        for tipo_f in orden_tipos:
            if tipo_f in agrupado:

                doc.add_paragraph(f"{orden_general}. {tipo_f}s")

                suborden = 1

                for item in agrupado[tipo_f]:
                    doc.add_paragraph(f"    {orden_general}.{suborden} {item}")
                    suborden += 1

                doc.add_paragraph("")
                orden_general += 1

        # =========================
        # 📥 DESCARGA
        # =========================

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Descargar Orden del Día",
            data=buffer,
            file_name=f"Acta_{acta_buscar}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        st.success("✅ Orden del Día generado correctamente")

    except Exception as e:
        st.error("Error al generar Word")
        st.text(str(e))
