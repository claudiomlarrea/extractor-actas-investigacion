import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO
from collections import defaultdict

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

# 🆕 CAMPOS CORRECTOS
titulo = st.text_input("Título")
director = st.text_input("Director")
unidad = st.text_input("Unidad Académica")

# =========================
# 💾 GUARDAR
# =========================

if st.button("Guardar en Google Sheets"):

    if acta.strip() == "":
        st.warning("⚠️ Debe ingresar número de acta")
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

        filas = [
            f for f in data
            if str(f.get("Acta", "")).strip() == str(acta_buscar).strip()
        ]

        if not filas:
            st.warning("No hay registros para esa acta")
            st.stop()

        fecha_doc = filas[0]["Fecha"]

        agrupado = defaultdict(list)

        for fila in filas:
            agrupado[fila["Tipo"]].append(fila)

        doc = Document()

        doc.add_paragraph("UNIVERSIDAD CATÓLICA DE CUYO").runs[0].bold = True
        doc.add_paragraph("Consejo de Investigación")
        doc.add_paragraph("")

        doc.add_paragraph("ORDEN DEL DÍA").runs[0].bold = True

        doc.add_paragraph(f"Acta Nº {acta_buscar}")
        doc.add_paragraph(f"Fecha: {fecha_doc}")
        doc.add_paragraph("")

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

                    # TITULO
                    doc.add_paragraph(item["Título"])

                    # DIRECTOR
                    doc.add_paragraph(f"    {contador}.{sub} Director {item['Director']}")

                    # UNIDAD
                    doc.add_paragraph(f"    ({item['Unidad Académica']})")

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

    except Exception as e:
        st.error("❌ Error al generar documento")
        st.text(str(e))
