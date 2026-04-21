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

anio = st.text_input("Año", key="anio")
fecha = st.text_input("Fecha", key="fecha")
acta = st.text_input("Acta", key="acta")

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

    acta_val = st.session_state.get("acta", "").strip()
    fecha_val = st.session_state.get("fecha", "").strip()
    anio_val = st.session_state.get("anio", "").strip()

    if acta_val == "":
        st.warning("⚠️ Debe ingresar número de acta")
    else:
        fila = [
            acta_val,
            fecha_val,
            anio_val,
            tipo.strip(),
            descripcion.strip()
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

acta_buscar = st.text_input("Número de Acta para generar informe")

if st.button("Generar Orden del Día"):

    try:
        data = sheet.get_all_records()

        # 🔴 FILTRO CORREGIDO (CLAVE)
        filas = [
            f for f in data
            if str(f.get("Acta", "")).strip() == str(acta_buscar).strip()
        ]

        st.write("📊 Registros encontrados:", len(filas))

        if not filas:
            st.warning("No hay datos para esa acta")
            st.stop()

        # =========================
        # 📊 AGRUPAR POR TIPO
        # =========================

        agrupado = {}

        for fila in filas:
            tipo_f = str(fila.get("Tipo", "")).strip()
            desc = str(fila.get("Descripción", "")).strip()

            if tipo_f not in agrupado:
                agrupado[tipo_f] = []

            agrupado[tipo_f].append(desc)

        # =========================
        # 📄 CREAR WORD
        # =========================

        doc = Document()

        doc.add_heading("ORDEN DEL DÍA", 0)
        doc.add_paragraph(f"Acta Nº {acta_buscar}")

        fecha_doc = str(filas[0].get("Fecha", "")).strip()
        doc.add_paragraph(f"Fecha: {fecha_doc}")
        doc.add_paragraph("")

        orden = 1

        for tipo_f, items in agrupado.items():
            doc.add_paragraph(f"{orden}. {tipo_f}")

            sub = 1
            for item in items:
                doc.add_paragraph(f"    {orden}.{sub} {item}")
                sub += 1

            doc.add_paragraph("")
            orden += 1

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
        st.error("❌ Error al generar Word")
        st.text(str(e))
