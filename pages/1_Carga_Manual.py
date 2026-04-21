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

    if not acta:
        st.warning("⚠️ Debe ingresar número de acta")
        st.stop()

    if not descripcion:
        st.warning("⚠️ Debe ingresar una descripción")
        st.stop()

    fila = [
        acta.strip(),
        fecha.strip(),
        anio.strip(),
        tipo.strip(),
        descripcion.strip()
    ]

    try:
        sheet.append_row(fila)
        st.success("✅ Guardado en Google Sheets")

    except Exception as e:
        st.error("❌ Error al guardar")
        st.text(str(e))


# =========================
# 📄 GENERAR ORDEN DEL DÍA
# =========================

st.markdown("---")
st.subheader("📄 Generar Orden del Día por Acta")

acta_buscar = st.text_input("Ingrese número de Acta para generar Word")

if st.button("Generar Orden del Día"):

    try:
        data = sheet.get_all_records()

        # FILTRO CORREGIDO (clave)
        filas = [
            f for f in data
            if str(f.get("Acta", "")).strip() == str(acta_buscar).strip()
        ]

        # eliminar filas vacías
        filas = [f for f in filas if f.get("Descripción")]

        if not filas:
            st.warning("No hay datos para esa acta")
            st.stop()

        # AGRUPAR POR TIPO
        agrupado = {}
        for fila in filas:
            tipo = fila.get("Tipo", "Sin tipo")
            desc = fila.get("Descripción", "")

            if tipo not in agrupado:
                agrupado[tipo] = []

            agrupado[tipo].append(desc)

        # CREAR WORD
        doc = Document()
        doc.add_heading(f"Orden del Día - Acta {acta_buscar}", 0)

        for tipo, items in agrupado.items():
            doc.add_heading(tipo, level=1)

            for item in items:
                doc.add_paragraph(f"- {item}")

        # Guardar en memoria (mejor que archivo físico)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Descargar Word",
            data=buffer,
            file_name=f"Acta_{acta_buscar}.docx"
        )

        st.success("✅ Orden del Día generado correctamente")

    except Exception as e:
        st.error("❌ Error al generar Word")
        st.text(str(e))
