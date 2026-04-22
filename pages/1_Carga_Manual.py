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

anio = st.text_input("Año")
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
        "Categorización Docente"
    ]
)

titulo = st.text_input("Título")
director = st.text_input("Director")
unidad = st.text_input("Unidad Académica")
docente_categorizado = st.text_input("Docente categorizado")
categoria_docente = st.text_input("Categoría Docente")

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
            docente_categorizado.strip(),
            categoria_docente.strip(),
            unidad.strip()
        ]

        try:
            sheet.append_row(fila)
            st.success("✅ Registro guardado correctamente")

            # 🔄 LIMPIAR FORMULARIO
            st.rerun()

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
            if str(f.get("ACTA", f.get("Acta", ""))).strip() == acta_buscar.strip()
        ]

        if not filas:
            st.warning("No hay registros para esa acta")
            st.stop()

        fecha_doc = str(filas[0].get("FECHA", filas[0].get("Fecha", ""))).strip()

        agrupado = defaultdict(list)

        for fila in filas:
            tipo_fila = str(fila.get("TIPO", fila.get("Tipo", ""))).strip()
            agrupado[tipo_fila].append(fila)

        doc = Document()

        # ENCABEZADO
        doc.add_paragraph("UNIVERSIDAD CATÓLICA DE CUYO").runs[0].bold = True
        doc.add_paragraph("Consejo de Investigación")
        doc.add_paragraph("")

        # TITULO
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

                    titulo_item = item.get("TITULO", item.get("Titulo", "")).strip()
                    director_item = item.get("DIRECTOR", item.get("Director", "")).strip()
                    unidad_item = item.get("UNIDAD ACADÉMICA", item.get("Unidad Académica", "")).strip()
                    docente_cat = item.get("Docente categorizado", "").strip()
                    categoria_doc = item.get("Categoría Docente", "").strip()

                    # 🔹 TITULO
                    if titulo_item:
                        doc.add_paragraph(titulo_item)

                    # 🔹 CATEGORIZACIÓN DOCENTE
                    if tipo == "Categorización Docente":
                        if docente_cat:
                            doc.add_paragraph(f"    {contador}.{sub} {docente_cat}")
                        if categoria_doc:
                            doc.add_paragraph(f"    Categoría: {categoria_doc}")
                        if unidad_item:
                            doc.add_paragraph(f"    ({unidad_item})")

                    # 🔹 RESTO
                    else:
                        if director_item:
                            doc.add_paragraph(f"    {contador}.{sub} Director {director_item}")
                        if unidad_item:
                            doc.add_paragraph(f"    ({unidad_item})")

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
