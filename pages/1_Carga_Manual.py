import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
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
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance",
        "Jornada de Investigación",
        "Convocatoria de Investigación",
        "Categorización Docente"
    ]
)

titulo = st.text_input("Título")
director = st.text_input("Director")
unidad = st.text_input("Unidad Académica")

# =========================
# 💾 GUARDAR
# =========================

if st.button("Guardar en Google Sheets"):

    if acta.strip() == "":
        st.warning("⚠️ Debe ingresar número de acta")

    elif titulo.strip() == "":
        st.warning("⚠️ Debe ingresar el título")

    else:
        fila = [
            acta.strip(),
            fecha.strip(),
            anio.strip(),
            tipo.strip(),
            titulo.strip(),
            director.strip(),
            unidad.strip()
        ]

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

acta_buscar = st.text_input("Ingrese número de Acta")

if st.button("Generar Orden del Día"):

    try:
        data = sheet.get_all_records()

        # 🔥 SOLUCIÓN DEFINITIVA (NO FALLA NUNCA)
        filas = []

        for f in data:
            acta_sheet = str(f.get("Acta", "")).strip()
            acta_input = str(acta_buscar).strip()

            try:
                if int(float(acta_sheet)) == int(float(acta_input)):
                    filas.append(f)
            except:
                pass

        if not filas:
            st.warning("No hay registros para esa acta")
            st.stop()

        fecha_doc = str(filas[0].get("Fecha", "")).strip()

        agrupado = defaultdict(list)

        for fila in filas:
            tipo_fila = str(fila.get("Tipo", "")).strip()
            agrupado[tipo_fila].append(fila)

        # =========================
        # 🧾 DOCUMENTO WORD FORMAL
        # =========================

        doc = Document()

        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(12)

        # ENCABEZADO
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("UNIVERSIDAD CATÓLICA DE CUYO\n")
        run.bold = True
        p.add_run("Consejo de Investigación\n")

        doc.add_paragraph("")

        # TÍTULO
        titulo_doc = doc.add_paragraph()
        titulo_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = titulo_doc.add_run("ORDEN DEL DÍA")
        run.bold = True
        run.font.size = Pt(14)

        doc.add_paragraph("")

        # ACTA Y FECHA
        doc.add_paragraph(f"Acta Nº {acta_buscar}")
        doc.add_paragraph(f"Fecha: {fecha_doc}")
        doc.add_paragraph("")

        # ORDEN
        orden = [
            "Proyecto de Investigación",
            "Proyecto de Cátedra",
            "Informe Final",
            "Informe de Avance",
            "Jornada de Investigación",
            "Convocatoria de Investigación",
            "Categorización Docente"
        ]

        contador = 1

        for tipo in orden:
            if tipo in agrupado:

                doc.add_paragraph(f"{contador}. {tipo}")

                sub = 1

                for item in agrupado[tipo]:

                    titulo_item = str(item.get("Título", "")).strip()
                    director_item = str(item.get("Director", "")).strip()
                    unidad_item = str(item.get("Unidad Académica", "")).strip()

                    doc.add_paragraph(f"   {titulo_item}")
                    doc.add_paragraph(f"      {contador}.{sub} Director {director_item}")
                    doc.add_paragraph(f"      ({unidad_item})")

                    sub += 1

                doc.add_paragraph("")
                contador += 1

        # FIRMA
        doc.add_paragraph("\n")
        doc.add_paragraph("________________________________________")
        doc.add_paragraph("Secretaría de Investigación")
        doc.add_paragraph("Universidad Católica de Cuyo")

        # DESCARGA
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "⬇️ Descargar Orden del Día (Formato Oficial)",
            buffer,
            file_name=f"Orden_del_Dia_Acta_{acta_buscar}.docx"
        )

        st.success("✅ Documento institucional generado correctamente")

    except Exception as e:
        st.error("❌ Error al generar documento")
        st.text(str(e))
