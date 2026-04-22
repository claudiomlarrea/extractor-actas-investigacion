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

# 🆕 NUEVO CAMPO
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
            descripcion.strip(),
            unidad.strip()   # 🆕 SE AGREGA
        ]

        try:
            sheet.append_row(fila)
            st.success("✅ Registro guardado correctamente")

        except Exception as e:
            st.error("❌ Error al guardar")
            st.text(str(e))

# =========================
# 📄 GENERAR ORDEN DEL DÍA (FORMATO INSTITUCIONAL REAL)
# =========================

st.markdown("---")
st.subheader("📄 Generar Orden del Día Oficial")

acta_buscar = st.text_input("Ingrese número de Acta a generar")

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
            tipo = fila.get("Tipo", "")
            descripcion = fila.get("Descripción", "")
            unidad = fila.get("Unidad Académica", "")

            nombre = ""
            director = ""

            # 🧠 PARSEO SIMPLE
            if "Nombre:" in descripcion:
                partes = descripcion.split("\n")
                for p in partes:
                    if "Nombre:" in p:
                        nombre = p.replace("Nombre:", "").strip()
                    if "Director:" in p:
                        director = p.replace("Director:", "").strip()
            else:
                nombre = descripcion

            agrupado[tipo].append({
                "nombre": nombre,
                "director": director,
                "unidad": unidad
            })

        # =========================
        # 🧾 CREAR WORD
        # =========================

        doc = Document()

        # ENCABEZADO
        doc.add_paragraph("UNIVERSIDAD CATÓLICA DE CUYO").runs[0].bold = True
        doc.add_paragraph("Consejo de Investigación")
        doc.add_paragraph("")

        # TITULO
        titulo = doc.add_paragraph("ORDEN DEL DÍA")
        titulo.runs[0].bold = True

        doc.add_paragraph(f"Acta Nº {acta_buscar}")
        doc.add_paragraph(f"Fecha: {fecha_doc}")
        doc.add_paragraph("")

        orden_tipos = [
            "Proyecto de Cátedra",
            "Proyecto de Investigación",
            "Informe Final",
            "Informe de Avance",
            "Jornada de Investigación",
            "Convocatoria de Investigación",
            "Categorización Docente"
        ]

        contador = 1

        for tipo in orden_tipos:
            if tipo in agrupado:

                # TITULO SECCIÓN
                doc.add_paragraph(f"{contador}. {tipo}")

                for i, item in enumerate(agrupado[tipo], start=1):

                    # NOMBRE
                    if item["nombre"]:
                        doc.add_paragraph(item["nombre"])

                    # DIRECTOR
                    if item["director"]:
                        doc.add_paragraph(f"    {contador}.{i} Director {item['director']}")

                    # UNIDAD
                    if item["unidad"]:
                        doc.add_paragraph(f"    ({item['unidad']})")

                doc.add_paragraph("")
                contador += 1

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

        # =========================
        # 🧾 DOCUMENTO WORD
        # =========================

        doc = Document()

        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)

        # ENCABEZADO
        p = doc.add_paragraph()
        run = p.add_run("UNIVERSIDAD CATÓLICA DE CUYO\n")
        run.bold = True
        p.add_run("Consejo de Investigación\n\n")

        # TÍTULO
        titulo = doc.add_paragraph()
        run = titulo.add_run("ORDEN DEL DÍA")
        run.bold = True
        run.font.size = Pt(16)
        titulo.alignment = 1

        doc.add_paragraph(f"Acta Nº {acta_buscar}")
        doc.add_paragraph(f"Fecha: {fecha_doc}")
        doc.add_paragraph("")

        orden_tipos = [
            "Proyecto",
            "Proyecto de Investigación",
            "Proyecto de Cátedra",
            "Jornada de Investigación",
            "Convocatoria de Investigación",
            "Informe de Avance",
            "Informe Final",
            "Categorización Docente"
        ]

        contador = 1

        for tipo in orden_tipos:
            if tipo in agrupado:

                p = doc.add_paragraph()
                run = p.add_run(f"{contador}. {tipo}")
                run.bold = True

                sub = 1

                for desc, unidad_f in agrupado[tipo]:
                    texto = f"    {contador}.{sub} {desc}"

                    # 🆕 AGREGA UNIDAD
                    if unidad_f:
                        texto += f" ({unidad_f})"

                    doc.add_paragraph(texto)
                    sub += 1

                doc.add_paragraph("")
                contador += 1

        # CIERRE
        doc.add_paragraph("\n")
        doc.add_paragraph("____________________________________")
        doc.add_paragraph("Secretaría de Investigación")
        doc.add_paragraph("Universidad Católica de Cuyo")

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
