import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO

# =========================
# ⚙ CONFIGURACIÓN
# =========================

st.set_page_config(page_title="Consejo de Investigación", layout="wide")

# =========================
# 🎨 HEADER
# =========================

col1, col2 = st.columns([1, 8], vertical_alignment="center")

with col1:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Logo_placeholder.png/300px-Logo_placeholder.png",
        width=120
    )

with col2:
    st.markdown("""
    <div class='header-uccuyo'>
        <h2 style="font-weight:600;">Universidad Católica de Cuyo</h2>
        <h4 style="opacity:0.9;">Secretaría de Investigación</h4>
        <h5 style="opacity:0.8;">Consejo de Investigación</h5>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 🎨 CSS GLOBAL
# =========================

st.markdown("""
<style>

/* Fondo general */
.stApp {
    background-color: #E6E6E6;
}

/* HEADER INSTITUCIONAL */
.header-uccuyo {
    background: linear-gradient(90deg, #064a3f, #0B6B5D);
    padding: 20px;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}

.header-uccuyo h2,
.header-uccuyo h4,
.header-uccuyo h5 {
    color: white !important;
    margin: 0;
}

/* Títulos GENERALES (NO TOCA HEADER) */
h1, h2, h3, h4, h5, h6 {
    color: black !important;
}

/* Labels */
label {
    color: black !important;
    font-weight: 500;
}

/* INPUTS */
input, textarea {
    background-color: white !important;
    color: black !important;
}

/* Selectbox */
div[data-baseweb="select"] {
    background-color: white !important;
}

div[data-baseweb="select"] span {
    color: black !important;
}

div[role="listbox"] {
    background-color: white !important;
}

div[role="option"] {
    background-color: white !important;
    color: black !important;
}

div[role="option"]:hover {
    background-color: #e6e6e6 !important;
}

/* Placeholder */
::placeholder {
    color: #777 !important;
}

.stTextInput > div > div > input {
    background-color: white !important;
    color: black !important;
}

.stTextArea textarea {
    background-color: white !important;
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🔐 CONEXIÓN
# =========================

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
sheet = client.open_by_key(SHEET_ID).worksheet("Hoja 2")

st.markdown(
    """
    <div style='background-color:#d4edda; padding:15px; border-radius:10px'>
        <a href='https://docs.google.com/spreadsheets/d/17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8' target='_blank' style='text-decoration:none; color:#155724; font-weight:bold; font-size:18px;'>
            ✔ Conectado a Google Sheets (abrir)
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# 📅 DATOS ACTAS
# =========================

actas_dict = {
    187: {"mes": "Febrero"},
    188: {"mes": "Marzo"},
    189: {"mes": "Abril"},
    190: {"mes": "Mayo"},
    191: {"mes": "Junio"},
    192: {"mes": "Julio"},
    193: {"mes": "Agosto"},
    194: {"mes": "Septiembre"},
    195: {"mes": "Octubre"},
    196: {"mes": "Noviembre"},
    197: {"mes": "Diciembre"},
}

fechas_actas = {
    187: "19 de Febrero 2026",
    188: "19 de Marzo 2026",
    189: "16 de Abril 2026",
    190: "21 de Mayo 2026",
    191: "18 de Junio 2026",
    192: "23 de Julio 2026",
    193: "20 de Agosto 2026",
    194: "15 de Septiembre 2026",
    195: "22 de Octubre 2026",
    196: "19 de Noviembre 2026",
    197: "10 de Diciembre 2026"
}
# 🔹 LISTA DE CATEGORÍAS (VA ARRIBA DE TODO)
categoria_opciones = [
    "Seleccionar",
    "Investigador/a Superior I",
    "Investigador/a Principal II",
    "Investigador/a Independiente III",
    "Investigador/a Adjunto/a IV",
    "Investigador/a Asistente V",
    "Becario/a de Iniciación VI",
    "Sin categorización / Externo"
]
# =========================
# 📝 FORMULARIO
# =========================

st.subheader("Carga de Actas")

with st.form("form_acta", clear_on_submit=True):

    anio = st.text_input("Año", "2026")

    acta_label = st.selectbox(
        "Número de Acta",
        options=[f"Acta N°{n} - {actas_dict[n]['mes']}" for n in actas_dict]
    )

    numero_acta = int(acta_label.split(" ")[1].replace("N°", ""))

    fecha = st.selectbox(
        "Fecha",
        options=list(fechas_actas.values()),
        index=list(fechas_actas.keys()).index(numero_acta)
    )

    tipo = st.selectbox("Tipo", [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance",
        "Jornada de Investigación",
        "Convocatoria de Investigación",
        "Convocatoria a Proyectos de investigación",
        "Creación de Semillero de Investigación",
        "Categorización Docente"
    ])

    titulo = st.text_input("Título")

    # =========================
    # 🎯 PUNTAJE (SOLO ESTO ES CONDICIONAL)
    # =========================

    puntaje = 0

    tipos_con_puntaje = [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance"
    ]

    if tipo in tipos_con_puntaje:
        puntaje = st.number_input(
            "Puntaje",
            min_value=0,
            max_value=1000,
            step=1,
            key="puntaje",
            help="Ingrese el puntaje asignado según la evaluación"
        )
    # =========================
    # 🧾 RESTO DEL FORMULARIO (SIEMPRE VISIBLE)
    # =========================

    descripcion = st.text_area("Descripción")

    director = st.text_input("Director")
    cat_director = st.selectbox("Categoría del Director", categoria_opciones)

    codirector = st.text_input("Codirector")
    categoria_codirector = st.selectbox("Categoría del Codirector", categoria_opciones)

    equipo = st.text_area("Equipo")

    unidad = st.selectbox(
        "Unidad Académica",
        [
            "FDCSSL- Facultad de Derecho y Ciencias Sociales Sede San Luis",
            "FCMSL- Facultad de Ciencias Médicas Sede San Luis",
            "FCVSL- Facultad de Veterinaria Sede San Luis",
            "FCEESL- Facultad de Ciencias Económicas y Empresariales Sede San Luis",
            "FBOSCO- Facultad Don Bosco",
            "FCEESJ- Facultad de Ciencias Económicas San Juan",
            "FFyHSJ- Facultad de Filosofía y Humanidades",
            "ISDSM- Instituto Universitario Santa María",
            "ECRyPSJ- Escuela Cultura Religiosa",
            "FDCSSJ- Facultad de Derecho San Juan",
            "FCMSJ- Facultad de Ciencias Médicas San Juan",
            "FEDSJ- Facultad de Educación",
            "ESEGSJ- Escuela de Seguridad",
            "FCQyTSJ- Facultad de Ciencias Químicas",
            "ISB- Instituto San Buenaventura"
        ]
    )

    resolucion_cd = st.text_input("Resolución CD")
    resolucion_cs = st.text_input("Resolución CS del Proyecto (ej: Res-367-CS)")
    instituto = st.text_input("Instituto")
    catedra = st.text_input("Cátedra")
    alumnos = st.text_input("Cantidad de Alumnos")

    # =========================
    # 💰 FINANCIAMIENTO
    # =========================

    tipo_financiamiento = st.selectbox(
        "Tipo de financiamiento",
        ["Seleccionar...", "Interno", "Externo"]
    )

    fuente_financiamiento = st.text_input("Fuente de financiamiento")

    monto_financiamiento = st.number_input(
        "Monto del financiamiento",
        min_value=0,
        step=1000
    )

    st.caption("Complete estos campos solo si corresponde")

    # 🔘 SUBMIT SIEMPRE AL FINAL
    submit = st.form_submit_button("Guardar en Google Sheets")

# =========================
# 💾 GUARDAR
# =========================

if submit:
    if tipo_financiamiento == "Seleccionar...":
        tipo_financiamiento = ""

    fila = [
        numero_acta,
        fecha,
        anio,
        tipo,
        titulo,
        descripcion,
        director,
        cat_director,
        codirector,
        categoria_codirector,
        equipo,
        "",  # Docente categorizado
        "",  # Categoría docente
        unidad,
        resolucion_cd,
        resolucion_cs, 
        instituto,
        catedra,
        tipo_financiamiento,
        fuente_financiamiento,
        monto_financiamiento,
        alumnos,
        puntaje
    ]

    # =========================
    # 🔍 VALIDACIONES
    # =========================

    if not numero_acta or not tipo or not titulo:
        st.error("Faltan datos obligatorios")

    elif tipo in [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance"
    ] and puntaje == 0:
        st.error("Debe ingresar el puntaje")

    elif tipo_financiamiento in ["Interno", "Externo"] and not fuente_financiamiento:
        st.error("Debe indicar la fuente de financiamiento")

    elif tipo_financiamiento in ["Interno", "Externo"] and monto_financiamiento == 0:
        st.error("Debe indicar el monto del financiamiento")

    else:
        sheet.append_row(fila)
        st.success("Registro guardado correctamente")
# =========================
# 📄 GENERAR WORD
# =========================

st.markdown("## 📄 Generar Orden del Día")

acta_word = st.selectbox(
    "Seleccionar Acta",
    options=list(actas_dict.keys())
)

generar = st.button("Generar Word")

if generar:

    datos = sheet.get_all_records()

    acta_num = int(acta_word)

    registros = [
        r for r in datos
        if str(r.get("numero_acta", "")).strip() == str(acta_num)
    ]

    if not registros:
        st.warning("No hay registros para esta acta")
    else:
        doc = Document()

        doc.add_heading('Consejo de Investigación', 0)
        doc.add_paragraph(f'Acta N° {acta_num}')

        fecha_real = registros[0].get("FECHA", registros[0].get("fecha", ""))
        doc.add_paragraph(f'Fecha: {fecha_real}')

        doc.add_heading('Orden del Día', level=1)

        for i, r in enumerate(registros, 1):

            # 🔹 Normalización de claves
            r = {k.lower().strip(): v for k, v in r.items()}

            p = doc.add_paragraph()

            p.add_run(f"{i}. {r.get('tipo', '')} - {r.get('titulo', '')}\n").bold = True

            p.add_run(
                f"   Director: {r.get('director', '')} ({r.get('cat_director', '')})\n"
            )

            if r.get("codirector"):
                p.add_run(
                    f"   Codirector: {r.get('codirector', '')} ({r.get('cat_codirector', '')})\n"
                )

            if r.get("equipo"):
                p.add_run(f"   Equipo: {r.get('equipo', '')}\n")

            p.add_run(f"   Unidad Académica: {r.get('unidad académica', r.get('unidad', ''))}\n")

            # =========================
            # 🎯 PUNTAJE ROBUSTO
            # =========================

            puntaje_valor = r.get("puntaje", 0)

            try:
                puntaje_num = float(puntaje_valor)
            except (TypeError, ValueError):
                puntaje_num = 0

            if puntaje_num > 0:
                p.add_run(f"   Puntaje: {int(puntaje_num)}\n")

            if r.get("resolucion cd"):
                p.add_run(f"   Resolución CD: {r.get('resolucion cd')}\n")

            if r.get("resolucion cs"):
                p.add_run(f"   Resolución CS del Proyecto: {r.get('resolucion cs')}\n")

            if r.get("instituto"):
                p.add_run(f"   Instituto: {r.get('instituto')}\n")

            if r.get("catedra"):
                p.add_run(f"   Cátedra: {r.get('catedra')}\n")

            if r.get("tipo de financiamiento"):
                p.add_run(f"   Financiamiento: {r.get('tipo de financiamiento')}\n")

            if r.get("fuente de financiamiento"):
                p.add_run(f"   Fuente: {r.get('fuente de financiamiento')}\n")

            if r.get("monto del financiamiento"):
                try:
                    monto = int(float(r.get("monto del financiamiento")))
                    monto = f"${monto:,}".replace(",", ".")
                except:
                    monto = r.get("monto del financiamiento")

                p.add_run(f"   Monto: {monto}\n")

            if r.get("alumnos"):
                p.add_run(f"   Alumnos: {r.get('alumnos')}\n")

            doc.add_paragraph("")

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "Descargar Word",
            data=buffer,
            file_name=f"Acta_{acta_num}.docx"
        )
