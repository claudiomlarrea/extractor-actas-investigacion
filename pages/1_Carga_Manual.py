import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO
from docx.shared import Pt
from docx.shared import Pt, RGBColor

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

st.subheader("Sistema de gestión de temas para el Consejo de Investigación")
st.markdown("<span style='color:black; font-weight:600;'>🔷 Complete solo los campos que correspondan</span>", unsafe_allow_html=True)

st.markdown(
    "<div style='margin-bottom:-15px; color:black; font-weight:600;'>🟢 Elija actividad</div>",
    unsafe_allow_html=True
)
tipo = st.selectbox("", [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance",
        "Jornada de Investigación",
        "Convocatoria a Proyectos de investigación",
        "Creación de Semillero de Investigación",
        "Categorización Docente",
        "Cronograma",
        "Llamado a Concurso de Becas",
        "Líneas prioritarias de investigación",
        "Otra"
    ])

with st.form("form_acta", clear_on_submit=True):

    # Año
    st.markdown(
        "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Año</div>",
        unsafe_allow_html=True
    )
    anio = st.text_input("", "2026")

    # Número de Acta
    st.markdown(
        "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Número de Acta</div>",
        unsafe_allow_html=True
    )
    acta_label = st.selectbox(
        "",
        options=[f"Acta N°{n} - {actas_dict[n]['mes']}" for n in actas_dict]
    )

    numero_acta = int(acta_label.split(" ")[1].replace("N°", ""))

    # Fecha
    st.markdown(
        "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Fecha</div>",
        unsafe_allow_html=True
    )
    fecha = st.selectbox(
        "",
        options=list(fechas_actas.values()),
        index=list(fechas_actas.keys()).index(numero_acta)
    )

    # =========================
    # CAMPOS SEGÚN ACTIVIDAD
    # =========================
    
    # 🔴 INICIALIZACIÓN
    director = ""
    cat_director = ""
    codirector = ""
    categoria_codirector = ""
    equipo = ""
    instituto = ""
    catedra = ""
    alumnos = ""
    apellido_nombre_docente = ""
    dni_docente = ""
    
    # -------- PROYECTOS / INFORMES / OTRA --------
    if tipo in [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance",
        "Otra"
    ]:
        pass
    
    # -------- CATEGORIZACIÓN DOCENTE --------
    elif tipo == "Categorización Docente":
    
        st.subheader("Categorización docente")
    
        apellido_nombre_docente = st.text_input("Apellido y Nombre del docente")
        dni_docente = st.text_input("DNI")
    
    # -------- JORNADAS / CONVOCATORIAS / SEMILLEROS --------
    elif tipo in [
        "Jornada de Investigación",
        "Convocatoria a Proyectos de investigación",
        "Creación de Semillero de Investigación"
    ]:
        pass
    
    # -------- CRONOGRAMA / LÍNEAS --------
    elif tipo in [
        "Cronograma",
        "Líneas prioritarias de investigación"
    ]:
        pass

    # =========================
    # 📌 IDENTIFICACIÓN
    # =========================

    st.markdown(
        "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Denominación de la actividad</div>",
        unsafe_allow_html=True
    )
    titulo = st.text_input("")
    
    st.markdown("""
    <div style="
        margin-top:-25px;
        margin-bottom:5px;
        background-color:#E6E6E6;
        padding:10px;
        border-radius:5px;
        font-size:13px;
        color:#000000;
    ">
    <b>Indicaciones:</b>
    <ul style="margin-top:5px; margin-bottom:0;">
    <li>Título del proyecto de investigación</li>
    <li>Título del Informe Final o de Avance</li>
    <li>Nombre de la jornada, semillero, instituto, etc.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # 🎯 PUNTAJE (CONDICIONAL)
    # =========================

    puntaje = 0
    
    tipos_con_puntaje = [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance"
    ]
    
    if tipo in tipos_con_puntaje:
    
        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Puntaje del Proyecto o Informe</div>",
            unsafe_allow_html=True
    )
    
    puntaje = st.number_input(
         "",
         min_value=0,
         max_value=1000,
         step=1,
         key="puntaje",
         help="Ingrese el puntaje asignado según la evaluación"
    )

    # =========================
    # 🧾 RESTO DEL FORMULARIO
    # =========================
    
    st.markdown(
        "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Descripción en no más de 30 palabras</div>",
        unsafe_allow_html=True
    )
    descripcion = st.text_area("")
    
    # 🔴 INICIALIZACIÓN
    director = ""
    cat_director = ""
    codirector = ""
    categoria_codirector = ""
    equipo = ""
    instituto = ""
    catedra = ""
    alumnos = ""
    resolucion_cs = ""
    
    # -------- CAMPOS SOLO PARA PROYECTOS / INFORMES --------
    if tipo in [
        "Proyecto de Investigación",
        "Proyecto de Cátedra",
        "Informe Final",
        "Informe de Avance",
        "Otra"
    ]:

        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Director</div>",
            unsafe_allow_html=True
        )
        director = st.text_input("", key="director")

        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Categoría del Director</div>",
            unsafe_allow_html=True
        )
        cat_director = st.selectbox("", categoria_opciones, key="cat_director")

        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Codirector</div>",
            unsafe_allow_html=True
        )
        codirector = st.text_input("", key="codirector")

        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Categoría del Codirector</div>",
            unsafe_allow_html=True
        )
        categoria_codirector = st.selectbox("", categoria_opciones, key="cat_codirector")

        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Equipo de Investigación</div>",
            unsafe_allow_html=True
        )
        equipo = st.text_area("", key="equipo")

        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Instituto</div>",
            unsafe_allow_html=True
        )
        instituto = st.text_input("", key="instituto")

        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Cátedra</div>",
            unsafe_allow_html=True
        )
        catedra = st.text_input("", key="catedra")

        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Cantidad de Alumnos</div>",
            unsafe_allow_html=True
        )
        alumnos = st.text_input("", key="alumnos")
    
    # -------- UNIDAD (SIEMPRE) --------
    st.markdown(
        "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Unidad Académica</div>",
        unsafe_allow_html=True
    )

    unidad = st.selectbox(
        "",
        [
            "FDCSSL- Facultad de Derecho y Ciencias Sociales Sede San Luis",
            "FCMSL- Facultad de Ciencias Médicas Sede San Luis",
            "FCVSL- Facultad de Ciencias Veterinarias Sede San Luis",
            "FCEESL- Facultad de Ciencias Económicas y Empresariales Sede San Luis",
            "FBOSCO- Facultad Don Bosco",
            "FCEESJ- Facultad de Ciencias Económicas y Empresariales Sede San Juan",
            "FFyHSJ- Facultad de Filosofía y Humanidades",
            "ISDSM- Instituto Universitario Santa María",
            "ECRyPSJ- Escuela Cultura Religiosa y Pastoral",
            "FDCSSJ- Facultad de Derecho y Ciencias Sociales Sede San Juan",
            "FCMSJ- Facultad de Ciencias Médicas San Juan",
            "FEDSJ- Facultad de Educación",
            "ESEGSJ- Escuela de Seguridad",
            "FCQyTSJ- Facultad de Ciencias Químicas y Tecnológicas",
            "ISB- Instituto San Buenaventura",
            "Secretaría de Investigación",
            "Unidad de Vinculación Tecnológica"
        ],
        key="unidad"
    )
    

    # -------- CAMPOS GENERALES --------
   st.markdown(
    "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Resolución CD</div>",
    unsafe_allow_html=True
)
resolucion_cd = st.text_input("", key="resolucion_cd")

# SOLO PARA PROYECTOS / INFORMES
if tipo in [
    "Proyecto de Investigación",
    "Proyecto de Cátedra",
    "Informe Final",
    "Informe de Avance",
    "Otra"
]:
    st.markdown(
        "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Resolución CS del Proyecto (ej: Res-367-CS) solo para Informes Finales y de Avances</div>",
        unsafe_allow_html=True
    )
    resolucion_cs = st.text_input("", key="resolucion_cs")
else:
    resolucion_cs = ""

# SIEMPRE
st.markdown(
    "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🔴 Responsable de carga (obligatorio)</div>",
    unsafe_allow_html=True
)
responsable_de_carga = st.text_input("", key="responsable_de_carga")

# =========================
# 💰 FINANCIAMIENTO
# =========================

st.markdown(
    "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Tipo de financiamiento</div>",
    unsafe_allow_html=True
)
tipo_financiamiento = st.selectbox(
    "",
    ["Seleccionar...", "Sin financiamiento", "Interno", "Externo"],
    key="tipo_financiamiento"
)

st.markdown(
    "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Fuente de financiamiento</div>",
    unsafe_allow_html=True
)
fuente_financiamiento = st.text_input("", key="fuente_financiamiento")

st.markdown(
    "<div style='margin-bottom:-10px; color:black; font-weight:600;'>🟢 Monto del financiamiento</div>",
    unsafe_allow_html=True
)
monto_financiamiento = st.number_input(
    "",
    min_value=0,
    step=1000,
    key="monto_financiamiento"
)



    # =========================
    # 🔘 SUBMIT
    # =========================

submit = st.form_submit_button("Guardar en Google Sheets")

# =========================
# 💾 GUARDAR
# =========================

if submit:

    if tipo_financiamiento == "Seleccionar...":
        tipo_financiamiento = ""

    # 🔹 LIMPIAR "Seleccionar" (versión robusta)
    if unidad.strip().startswith("Seleccionar"):
        unidad = ""

    if instituto.strip().startswith("Seleccionar"):
        instituto = ""

    if catedra.strip().startswith("Seleccionar"):
        catedra = ""

    if tipo_financiamiento.strip().startswith("Seleccionar"):
        tipo_financiamiento = ""

    if str(cat_director).strip().startswith("Seleccionar"):
        cat_director = ""

    if str(categoria_codirector).strip().startswith("Seleccionar"):
        categoria_codirector = ""

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
        apellido_nombre_docente,
        dni_docente,
        unidad,
        resolucion_cd,
        resolucion_cs,
        instituto,
        catedra,
        tipo_financiamiento,
        fuente_financiamiento,
        monto_financiamiento,
        alumnos,
        puntaje,
        responsable_de_carga
        ]

    # VALIDACIONES
    if not anio.strip():
        st.error("Debe completar el año")

    elif not numero_acta:
        st.error("Debe seleccionar el número de acta")

    elif not fecha:
        st.error("Debe seleccionar la fecha")

    elif not tipo:
        st.error("Debe elegir la actividad")

    else:
        sheet.append_row(fila)
        st.success("Registro guardado correctamente")
    
# =========================
# 📄 GENERAR WORD
# =========================

st.markdown("## 📄 Generar Orden del Día")

acta_word = st.selectbox(
    "Seleccionar Orden del Día para generarlo y descargar",
    options=[f"{n} - {actas_dict[n]['mes']}" for n in actas_dict]
)

generar = st.button("Generar Word")

if generar:

    datos = sheet.get_all_records()

    acta_num = int(acta_word.split(" - ")[0])

    registros = [
        r for r in datos
        if str(r.get("numero_acta", "")).strip() == str(acta_num)
    ]

    if not registros:
        st.warning("No hay registros para esta acta")

    else:
        doc = Document()

        doc.add_heading('Consejo de Investigación', 0)

        p_acta = doc.add_paragraph(f'Acta N° {acta_num}')
        p_acta.paragraph_format.space_after = Pt(0)

        fecha_real = registros[0].get("FECHA", registros[0].get("fecha", ""))
        p_fecha = doc.add_paragraph(f'Fecha: {fecha_real}')
        p_fecha.paragraph_format.space_after = Pt(0)

        doc.add_heading('Orden del Día', level=1)

        contador = 1
        unidad_actual = None

        for r in registros:

            r = {k.lower().strip(): v for k, v in r.items()}

            unidad = r.get("unidad académica", r.get("unidad", "")).strip()

            if unidad != unidad_actual:
                h = doc.add_paragraph()
                h.paragraph_format.space_before = Pt(6)
                h.paragraph_format.space_after = Pt(2)
                h.paragraph_format.line_spacing = 1

                run_h = h.add_run(unidad)
                run_h.bold = True
                run_h.font.color.rgb = RGBColor(0, 102, 204)

                unidad_actual = unidad

            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1

            p.add_run(f"{contador}. {r.get('tipo', '')} - {r.get('titulo', '')}\n").bold = True

            descripcion = r.get("descripcion") or r.get("descripción") or ""

            if descripcion:
                p.add_run(f"   Descripción: {descripcion}\n")
                
            tipo_actividad = r.get("tipo", "")

            if tipo_actividad == "Categorización Docente":

                nombre_doc = r.get("apellido_nombre_docente", "")
                dni_doc = r.get("dni_docente", "")

                if nombre_doc:
                    p.add_run(f"   Docente: {nombre_doc}\n")

                if dni_doc:
                    p.add_run(f"   DNI: {dni_doc}\n")

            tipos_con_director = [
                "Proyecto de Investigación",
                "Proyecto de Cátedra",
                "Informe Final",
                "Informe de Avance"
            ]

            if tipo_actividad in tipos_con_director:

                cat = r.get('cat_director', '')
                if cat == "Seleccionar" or cat == "":
                    p.add_run(f"   Director: {r.get('director', '')}\n")
                else:
                    p.add_run(f"   Director: {r.get('director', '')} ({cat})\n")

                cat_codir = r.get('cat_codirector', '')
                if cat_codir == "Seleccionar" or cat_codir == "":
                    p.add_run(f"   Codirector: {r.get('codirector', '')}\n")
                else:
                    p.add_run(f"   Codirector: {r.get('codirector', '')} ({cat_codir})\n")

            if r.get("equipo"):
                p.add_run(f"   Equipo: {r.get('equipo', '')}\n")

            p.add_run(f"   Unidad Académica: {unidad}\n")

            puntaje_valor = r.get("puntaje", 0)
            try:
                puntaje_num = float(puntaje_valor)
            except:
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

            contador += 1

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "Descargar Word",
            data=buffer,
            file_name=f"Acta_{acta_num}.docx"
        )
        
st.markdown("### 🧾 Generar informe por responsable")

responsable_reporte = st.text_input("Responsable de carga para generar informe")

generar_responsables = st.button("Generar informe del responsable")

if generar_responsables:

    datos = sheet.get_all_records()

    acta_num = int(acta_word.split(" - ")[0])

    registros = [
        r for r in datos
        if str(r.get("numero_acta", "")).strip() == str(acta_num)
        and str(r.get("responsable_de_carga", "")).strip().lower() == responsable_reporte.strip().lower()
    ]

    registros = sorted(
        registros,
        key=lambda r: str(
            {k.lower().strip(): v for k, v in r.items()}.get("unidad académica", "")
        ).strip()
    )

    if not responsable_reporte.strip():
        st.warning("Debe ingresar el responsable de carga")

    elif not registros:
        st.warning("No hay registros cargados por ese responsable para esta acta")

    else:
        doc = Document()

        doc.add_heading("Informe de temas cargados", 0)
        doc.add_paragraph(f"Acta N° {acta_num}")
        doc.add_paragraph(f"Responsable de carga: {responsable_reporte}")

        contador = 1
        unidad_actual = None

        for r in registros:

            r = {k.lower().strip(): v for k, v in r.items()}

            unidad = r.get("unidad académica", r.get("unidad", "")).strip()

            if unidad != unidad_actual:
                h = doc.add_paragraph()
                h.paragraph_format.space_before = Pt(6)
                h.paragraph_format.space_after = Pt(2)

                run_h = h.add_run(unidad)
                run_h.bold = True
                run_h.font.color.rgb = RGBColor(0, 102, 204)

                unidad_actual = unidad

            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1

            p.add_run(f"{contador}. {r.get('tipo', '')} - {r.get('titulo', '')}\n").bold = True

            descripcion = r.get("descripcion") or r.get("descripción") or ""

            if descripcion:
                p.add_run(f"   Descripción: {descripcion}\n")

            p.add_run(f"   Unidad Académica: {unidad}\n")

            contador += 1

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "Descargar informe del responsable",
            data=buffer,
            file_name=f"Informe_{responsable_reporte}_Acta_{acta_num}.docx"
        )
