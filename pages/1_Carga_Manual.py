import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from docx.shared import Pt
from io import BytesIO
from collections import defaultdict

st.title("📥 Sistema de Actas - Consejo de Investigación")

# =========================
# 🔐 CONEXIÓN GOOGLE SHEETS
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
    st.error("❌ Error de conexión")
    st.text(str(e))
    st.stop()

# =========================
# 📝 FORMULARIO
# =========================

st.subheader("📋 Carga de Actas")

anio = st.text_input("Año", "2026")
fecha = st.text_input("Fecha", "18/08/2026")
acta = st.text_input("Número de Acta")

tipo = st.selectbox(
    "Tipo",
    [
        "Proyecto",
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance",
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
        fila = [acta, fecha, anio, tipo, descripcion]

        try:
            sheet.append_row(fila)
            st.success("✅ Registro guardado correctamente")

        except Exception as e:
            st.error("❌ Error al guardar")
            st.text(str(e))

# =========================
# 📄 GENERAR ORDEN DEL DÍA
# =========================

st.markdown("---")
st.subheader("📄 Generar Orden del Día Oficial")

acta_buscar = st.text_input("Ingrese número de Acta a generar")

if st.button("Generar Orden del Día"):

    try:
        data = sheet.get_all_records()

        filas = [f for f in data if str(f["Acta"]) == str(acta_buscar)]

        if not filas:
            st.warning("No hay registros para esa acta")
            st.stop()

        fecha_doc = filas[0]["Fecha"]

        # Agrupar
        agrupado = defaultdict(list)
        for fila in filas:
            agrupado[fila["Tipo"]].append(fila["Descripción"])

        # =========================
        # 🧾 CREAR DOCUMENTO WORD
        # =========================

        doc = Document()

        # --- ENCABEZADO INSTITUCIONAL ---
        p = doc.add_paragraph()
        run = p.add_run("UNIVERSIDAD CATÓLICA DE CUYO\n")
        run.bold = True

        p.add_run("Consejo de Investigación\n")
        p.add_run("\n")

        # --- TÍTULO ---
        titulo = doc.add_paragraph()
        run = titulo.add_run(f"ORDEN DEL DÍA\nActa Nº {acta_buscar}")
        run.bold = True
        titulo.runs[0].font.size = Pt(16)

        # --- FECHA ---
        doc.add_paragraph(f"Fecha: {fecha_doc}")
        doc.add_paragraph("")

        # --- CUERPO ---
        contador = 1

        for tipo, items in agrupado.items():

            doc.add_paragraph(f"{contador}. {tipo}", style='List Number')

            sub = 1
            for item in items:
                doc.add_paragraph(f"{contador}.{sub} {item}")
                sub += 1

            contador += 1
            doc.add_paragraph("")

        # --- CIERRE ---
        doc.add_paragraph("\n")
        doc.add_paragraph("____________________________________")
        doc.add_paragraph("Secretaría de Investigación")
        doc.add_paragraph("Universidad Católica de Cuyo")

        # =========================
        # 📥 DESCARGA
        # =========================

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Descargar Orden del Día (Word)",
            data=buffer,
            file_name=f"Orden_del_Dia_Acta_{acta_buscar}.docx"
        )

        st.success("✅ Documento generado correctamente")

    except Exception as e:
        st.error("❌ Error al generar documento")
        st.text(str(e))
