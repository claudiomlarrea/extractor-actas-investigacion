from __future__ import annotations

import re
import unicodedata

import streamlit as st
import streamlit.components.v1 as components
import gspread
from gspread.utils import ValueInputOption
from pathlib import Path
from ucc_streamlit_chrome import hide_streamlit_cloud_toolbar
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO
from docx.shared import Pt, RGBColor
import smtplib
import ssl
from email.message import EmailMessage


def _fila_sheet_normalizada(r):
    return {k.lower().strip(): v for k, v in r.items()}


def _unidad_academica_clave(r):
    """Misma fuente que los encabezados de Word: columna «unidad académica» o «unidad»."""
    row = _fila_sheet_normalizada(r)
    return str(row.get("unidad académica") or row.get("unidad") or "").strip()


def ordenar_registros_por_unidad_academica(registros):
    """Orden estable por unidad; dentro de cada unidad conserva el orden del sheet."""
    if not registros:
        return registros
    indexed = list(enumerate(registros))
    indexed.sort(key=lambda t: (_unidad_academica_clave(t[1]).casefold(), t[0]))
    return [r for _, r in indexed]


TIPOS_CON_PUNTAJE = [
    "Proyecto de Investigación",
    "Proyecto de Cátedra",
    "Informe Final",
    "Informe de Avance",
]


def _ayuda_en_iframe(html: str, alto: int) -> None:
    """HTML en iframe: el CSS del tema de Streamlit no vuelve blanco el texto de ayuda."""
    components.html(html, height=alto, scrolling=False)


def _normalizar_puntaje_desde_hoja(x: float) -> float:
    """Corrige escalas x100 típicas de Google Sheets (columna %, formato numérico). Ej: 8850 → 88.5."""
    if x != x or x <= 0:
        return x
    x = float(x)
    while x > 1000 and abs(x - round(x)) < 1e-4:
        ri = int(round(x))
        if ri % 100 != 0:
            break
        x = x / 100.0
    return x


def parse_puntaje_valor(val):
    """Número desde Sheets o texto; admite coma o punto decimal (AR / US)."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        x = float(val)
        if x != x:  # NaN
            return None
        return _normalizar_puntaje_desde_hoja(x)
    s = unicodedata.normalize("NFKC", str(val))
    s = re.sub(r"\s+", "", s)
    if not s or s.lower() in ("nan", "none"):
        return None
    # Patrón claro: parte entera + un separador + parte decimal (evita ambigüedades)
    m = re.match(r"^(\d{1,4})([.,])(\d{1,4})$", s)
    if m:
        whole, _sep, frac = m.groups()
        try:
            return _normalizar_puntaje_desde_hoja(float(f"{whole}.{frac}"))
        except ValueError:
            return None
    # Miles con punto y decimal con coma: 1.234,56
    m2 = re.match(r"^(\d{1,3}(?:\.\d{3})+),(\d+)$", s)
    if m2:
        whole = m2.group(1).replace(".", "")
        frac = m2.group(2)
        try:
            return _normalizar_puntaje_desde_hoja(float(f"{whole}.{frac}"))
        except ValueError:
            return None
    # Solo dígitos (entero)
    m3 = re.match(r"^(\d{1,4})$", s)
    if m3:
        try:
            return _normalizar_puntaje_desde_hoja(float(m3.group(1)))
        except ValueError:
            return None
    # Fallback: un solo tipo de separador
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        s = s.replace(",", ".")
    try:
        return _normalizar_puntaje_desde_hoja(float(s))
    except ValueError:
        return None


def puntaje_a_texto_celda_sheet(x: float) -> str:
    """Texto con punto ASCII para la celda: evita que Sheets (locale ES) reinterprete comas."""
    x = float(x)
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.4f}".rstrip("0").rstrip(".")


def parse_anio_hoja(s: str) -> int | None:
    """Año como entero para la planilla (Looker Studio agrupa por número, no por texto)."""
    if s is None or not str(s).strip():
        return None
    s = str(s).strip()
    if not re.fullmatch(r"\d{4}", s):
        return None
    n = int(s)
    if n < 1990 or n > 2100:
        return None
    return n


def parse_puntaje_campo_formulario(s: str) -> tuple[float, str | None]:
    """Vacío → 0.0. Devuelve (valor, mensaje_error o None)."""
    if s is None or not str(s).strip():
        return 0.0, None
    n = parse_puntaje_valor(s)
    if n is None:
        return 0.0, "Use solo números; decimales con coma o punto (ej: 87,9 o 87.9)."
    if n < 0 or n > 1000:
        return 0.0, "El puntaje debe estar entre 0 y 1000."
    return n, None


def contar_palabras(texto: str) -> int:
    return len(re.findall(r"\S+", str(texto or "").strip()))


def format_puntaje_doc_es(x: float) -> str:
    """Texto para Word/correo: siempre 2 decimales y coma (ej. 86,00 como en la hoja)."""
    x = _normalizar_puntaje_desde_hoja(float(x))
    return f"{x:.2f}".replace(".", ",")


def puntaje_texto_para_word(raw) -> str | None:
    """
    Texto final para la línea «Puntaje: …» del Word.
    Refuerza la corrección x100 (hoja mal formateada / API) y evita mostrar 8780 tal cual.
    """
    if raw in (None, ""):
        return None
    n = parse_puntaje_valor(raw)
    if n is None or n <= 0:
        return None
    x = float(n)
    for _ in range(10):
        if x <= 1000:
            break
        # tolerancia por floats de la API (8780.000000001)
        if abs(x - round(x)) >= 1e-4:
            break
        ri = int(round(x))
        if ri % 100 != 0:
            break
        x = x / 100.0
    if x <= 0 or x > 1000:
        return None
    # Siempre dos decimales y coma decimal (alineado a Google Sheets: 86,00)
    return f"{x:.2f}".replace(".", ",")


# =========================
# ⚙ CONFIGURACIÓN
# =========================

st.set_page_config(page_title="Consejo de Investigación", layout="wide")
hide_streamlit_cloud_toolbar()

_ir_a_descargar_od = st.session_state.pop("ir_a_descargar_orden_dia", False)
_viene_de_otra_pagina = st.session_state.get("_pagina_streamlit_prev") != "cargar_temas"
st.session_state["_pagina_streamlit_prev"] = "cargar_temas"

_scroll_arriba = (not _ir_a_descargar_od) and (
    st.session_state.pop("volver_arriba_cargar_temas", False) or _viene_de_otra_pagina
)

components.html(
    f"""
    <script>
    (function () {{
        const win = window.parent;
        const doc = win.document;
        const storage = win.sessionStorage;
        const irOd = {"true" if _ir_a_descargar_od else "false"};
        const irArriba = {"true" if _scroll_arriba else "false"};

        function subir() {{
            [doc.querySelector("section.main"),
             doc.querySelector('[data-testid="stAppViewContainer"]'),
             doc.querySelector('[data-testid="stMainBlockContainer"]'),
             doc.querySelector('[data-testid="stMain"]')].forEach(function (el) {{
                if (el) el.scrollTop = 0;
            }});
        }}
        function programarSubir() {{
            subir();
            [0, 120, 350, 700, 1200, 2000].forEach(function (ms) {{
                setTimeout(subir, ms);
            }});
        }}

        if (!win._uccNavScrollInit) {{
            win._uccNavScrollInit = true;
            setInterval(function () {{
                if (storage.getItem("ucc_scroll_top") === "1") {{
                    storage.removeItem("ucc_scroll_top");
                    programarSubir();
                }}
            }}, 200);
            function enlazarMenu() {{
                doc.querySelectorAll(
                    '[data-testid="stSidebarNav"] a, [data-testid="stSidebarNavLink"]'
                ).forEach(function (a) {{
                    if (a._uccBound) return;
                    const t = (a.textContent || "").toLowerCase();
                    if (t.includes("cargar") && t.includes("temas")) {{
                        a._uccBound = true;
                        a.addEventListener("pointerdown", function () {{
                            storage.setItem("ucc_scroll_top", "1");
                        }}, true);
                    }}
                }});
            }}
            enlazarMenu();
            new MutationObserver(enlazarMenu).observe(doc.body, {{
                childList: true,
                subtree: true,
            }});
        }}

        if (irArriba) storage.setItem("ucc_scroll_top", "1");
    }})();
    </script>
    """,
    height=0,
)

_APP_ROOT = Path(__file__).resolve().parent.parent
_LOGO_PATH = _APP_ROOT / "assets" / "logo_uccuyo.png"

# =========================
# 🎨 HEADER
# =========================

col1, col2 = st.columns([1, 8], vertical_alignment="center")

with col1:
    if _LOGO_PATH.is_file():
        st.image(str(_LOGO_PATH), width=120)
    else:
        st.caption("Logo no encontrado (assets/logo_uccuyo.png)")

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
    font-weight: 700 !important;
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

/* Barra vertical al final del texto en selects = caret del combobox Base Web */
div[data-baseweb="select"] input,
div[data-baseweb="select"] [data-baseweb="input"] input,
div[data-baseweb="select"] [role="combobox"],
div[data-baseweb="select"] [contenteditable="true"] {
    caret-color: transparent !important;
}

/* Placeholder */
::placeholder {
    color: #777 !important;
}

.stTextInput > div > div > input {
    background-color: white !important;
    color: black !important;
    caret-color: #111111 !important;
}

.stTextArea textarea {
    background-color: white !important;
    color: black !important;
    caret-color: #111111 !important;
}

/* Números: mismo cursor oscuro sobre fondo blanco */
.stNumberInput input,
[data-testid="stNumberInputField"] {
    caret-color: #111111 !important;
}
/* SIDEBAR OPCIONES EN VERDE */
[data-testid="stSidebarNav"] a {
    background-color: #064a3f !important;
    color: white !important;
    font-size: 16px !important;
    margin-bottom: 8px;
    padding: 10px 12px;
    border-radius: 10px;
}

/* OPCIÓN ACTIVA */
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #0B6B5D !important;
    color: white !important;
    font-weight: bold;
}
/* 🔥 SOLUCIÓN DEFINITIVA */
[data-testid="stSidebarNav"] * { color: white !important; }

/* MENSAJE VERDE */
[data-testid="stAlert"] * {
    color: black !important;
    font-weight: 700 !important;
}

/* Leyendas (caption): evitar texto blanco heredado sobre fondo claro */
section.main [data-testid="stCaptionContainer"],
section.main [data-testid="stCaptionContainer"] p,
section.main [data-testid="stCaptionContainer"] small,
section.main [data-testid="stCaptionContainer"] span,
section.main [data-testid="stCaption"],
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stCaptionContainer"] p,
[data-testid="stMain"] [data-testid="stCaptionContainer"] span {
    color: #1a1a1a !important;
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
            ✔ Base de datos de Órdenes del Día del Consejo de Investigación (abrir)
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

MAX_UNIDADES_ACADEMICAS = 5
opciones_unidades_select = [
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
    "Unidad de Vinculación Tecnológica",
    "OIA- Observatorio de Inteligencia Artificial",
    "Vicerrectora de Formación",
    "Departamento de Educación a Distancia",
]

# =========================
# 📝 FORMULARIO
# =========================

st.subheader("Sistema de gestión de temas para el Consejo de Investigación")
st.markdown("<span style='color:black; font-weight:700;'>🔷 Complete solo los campos que correspondan</span>", unsafe_allow_html=True)

# Fuera del form: cada cambio dispara rerun. Dentro de st.form, los widgets no
# actualizan el script hasta enviar, y la fecha quedaba desfasada del desplegable de acta.
col_bas_1, col_bas_2, col_bas_3 = st.columns([1, 2, 2])

with col_bas_1:
    st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Año</div>", unsafe_allow_html=True)
    anio = st.text_input("", "2026", key="anio")

with col_bas_2:
    st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Seleccione el Orden del Día</div>", unsafe_allow_html=True)
    OPCION_ACTA_SIN_SELECCION = "Seleccionar el Orden del día"
    opciones_acta_carga = [OPCION_ACTA_SIN_SELECCION] + [
        f"Orden del Día {actas_dict[n]['mes']} - Acta {n}" for n in actas_dict
    ]
    acta_label = st.selectbox(
        "",
        opciones_acta_carga,
        index=0,
        key="acta",
    )

if acta_label == OPCION_ACTA_SIN_SELECCION:
    numero_acta = None
    fecha = ""
else:
    numero_acta = int(acta_label.split("Acta ")[1])
    fecha = fechas_actas.get(numero_acta, "")

with col_bas_3:
    st.markdown("<div style='margin-bottom:6px; color:black; font-weight:700;'>🟢 Fecha de la reunión de Consejo de Investigación</div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:black; margin:0 0 20px 0; padding-bottom:4px;'><strong>{fecha}</strong></p>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<div style='margin-bottom:8px; color:black; font-weight:700;'>🟢 Elija la Actividad o Tema para enviar al Orden del día</div>",
    unsafe_allow_html=True,
)
col_tipo_1, col_tipo_2 = st.columns([2, 3])
with col_tipo_1:
    tipo = st.selectbox(
        "Tipo de actividad",
        [
            "Proyecto de Investigación",
            "Proyecto de Cátedra",
            "Informe Final",
            "Informe de Avance",
            "Jornada de Investigación",
            "Convocatoria a Proyectos de investigación",
            "Creación de Semillero de Investigación",
            "Categorización Docente",
            "Llamado a Concurso de Becas",
            "Líneas prioritarias de investigación",
            "Otra",
        ],
        key="tipo_actividad",
        label_visibility="collapsed",
    )

with st.form("form_acta", clear_on_submit=False):

    # =========================
    # 📌 IDENTIFICACIÓN
    # =========================

    # Mockup: 3 columnas — Denominación+input | Indicaciones (solo banner) | Puntaje+input
    _hdr_iframe_h = 100
    col_den, col_ind, col_pun = st.columns([2.5, 2.5, 1.05], vertical_alignment="top")

    with col_den:
        _ayuda_en_iframe(
            f"<div style=\"box-sizing:border-box;height:{_hdr_iframe_h - 2}px;display:flex;align-items:center;"
            "padding:8px 12px;font:bold 15px/1.2 system-ui,sans-serif;color:#111;background:#dedede;"
            'border-radius:6px;border:1px solid #c8c8c8;">🟢 Denominación de la actividad o Tema</div>',
            alto=_hdr_iframe_h,
        )

    with col_ind:
        _ayuda_en_iframe(
            f"<div style=\"box-sizing:border-box;min-height:{_hdr_iframe_h - 2}px;padding:8px 10px;font:11.5px/1.3 system-ui,sans-serif;"
            "color:#111;background:#dedede;border-radius:6px;border-left:5px solid #0b6b5d;"
            'border-top:1px solid #c8c8c8;border-right:1px solid #c8c8c8;border-bottom:1px solid #c8c8c8;">'
            "<strong>Indicaciones:</strong> "
            "Título del proyecto; Título del Informe Final o de Avance; "
            "Título de Jornada / Semillero / Instituto u otra actividad</div>",
            alto=_hdr_iframe_h,
        )

    with col_pun:
        if tipo in TIPOS_CON_PUNTAJE:
            _ayuda_en_iframe(
                f"<div style=\"box-sizing:border-box;height:{_hdr_iframe_h - 2}px;display:flex;flex-direction:column;"
                "justify-content:center;gap:6px;padding:8px 10px;font-family:system-ui,sans-serif;"
                "background:#dedede;border-radius:6px;border:1px solid #c8c8c8;\">"
                "<div style=\"font-weight:700;color:#111;font-size:15px;line-height:1.15;\">🟢 Puntaje</div>"
                "<div style=\"font-size:11.5px;line-height:1.3;color:#111;\">"
                "Decimales con coma o punto (ej: 87,9 o 87.9).</div></div>",
                alto=_hdr_iframe_h,
            )

    # Inputs: denominación ancha (hasta borde de Indicaciones) | puntaje a la derecha
    col_tit_w, col_pun_inp = st.columns([5.0, 1.05], vertical_alignment="top")
    with col_tit_w:
        titulo = st.text_input("", key="titulo_actividad_consejo")
    with col_pun_inp:
        puntaje = 0.0
        if tipo in TIPOS_CON_PUNTAJE:
            puntaje_raw = st.text_input(
                "",
                placeholder="Ej: 87,9",
                key="puntaje_informe_consejo",
                label_visibility="collapsed",
            )
            _pv = parse_puntaje_valor(puntaje_raw)
            puntaje = _pv if _pv is not None else 0.0

    # Descripción solo bajo Denominación + Indicaciones (misma proporción que arriba: 2.5+2.5 vs 1.05)
    col_desc_w, _col_desc_pad = st.columns([5.0, 1.05])
    with col_desc_w:
        st.markdown(
            "<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Descripción (no más de 50 palabras)</div>",
            unsafe_allow_html=True,
        )
        descripcion = st.text_area("")

    # =========================
    # 👥 EQUIPO (CONDICIONAL)
    # =========================

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

    if tipo == "Categorización Docente":
        col_doc_1, col_doc_2 = st.columns(2)
        with col_doc_1:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Apellido y nombre del docente</div>", unsafe_allow_html=True)
            apellido_nombre_docente = st.text_input("", key="apellido_nombre_docente")
        with col_doc_2:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 DNI</div>", unsafe_allow_html=True)
            dni_docente = st.text_input("", key="dni_docente")

    if tipo in ["Proyecto de Investigación", "Proyecto de Cátedra", "Informe Final", "Informe de Avance", "Otra"]:

        col_dir_1, col_dir_2 = st.columns(2)
        with col_dir_1:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Director</div>", unsafe_allow_html=True)
            director = st.text_input("", key="director")
        with col_dir_2:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Categoría del Director</div>", unsafe_allow_html=True)
            cat_director = st.selectbox("", categoria_opciones, key="cat_director")

        col_codir_1, col_codir_2 = st.columns(2)
        with col_codir_1:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Codirector</div>", unsafe_allow_html=True)
            codirector = st.text_input("", key="codirector")
        with col_codir_2:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Categoría del Codirector</div>", unsafe_allow_html=True)
            categoria_codirector = st.selectbox("", categoria_opciones, key="cat_codirector")

        st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Equipo de Investigación (no más de 50 palabras)</div>", unsafe_allow_html=True)
        equipo = st.text_area("", key="equipo", height=160)

        col_eq_1, col_eq_2, col_eq_3 = st.columns(3)
        with col_eq_1:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Instituto de Investigación</div>", unsafe_allow_html=True)
            instituto = st.text_input("", key="instituto")
        with col_eq_2:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Cátedra (Si corresponde)</div>", unsafe_allow_html=True)
            catedra = st.text_input("", key="catedra")
        with col_eq_3:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700; font-size:0.92rem; line-height:1.2;'>🟢 Número de Alumnos en el proyecto</div>", unsafe_allow_html=True)
            alumnos = st.text_input("", key="alumnos")

    # =========================
    # 🏫 UNIDAD
    # =========================

    col_uni_res_1, col_uni_res_2, col_uni_res_3 = st.columns([2.9, 1.05, 1.05])
    with col_uni_res_1:
        st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Unidad Académica</div>", unsafe_allow_html=True)
        st.caption(
            f"Máximo {MAX_UNIDADES_ACADEMICAS} unidades. "
            f"Con {MAX_UNIDADES_ACADEMICAS} elegidas, quite una con la × para cambiar."
        )
        unidades_sel = st.multiselect(
            "",
            opciones_unidades_select,
            key="unidades_academicas",
            max_selections=MAX_UNIDADES_ACADEMICAS,
            label_visibility="collapsed",
        )

    # =========================
    # 📄 RESOLUCIONES
    # =========================

    if tipo in ["Proyecto de Investigación", "Proyecto de Cátedra", "Informe Final", "Informe de Avance", "Otra"]:

        with col_uni_res_2:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Resolución CD</div>", unsafe_allow_html=True)
            resolucion_cd = st.text_input("", key="resolucion_cd", max_chars=10, placeholder="Ej: 665")
        with col_uni_res_3:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Resolución CS</div>", unsafe_allow_html=True)
            resolucion_cs = st.text_input("", key="resolucion_cs", max_chars=10, placeholder="Ej: 657")

    else:
        resolucion_cd = ""
        resolucion_cs = ""

    # =========================
    # 👤 RESPONSABLE
    # =========================

    col_fin_1, col_fin_2, col_fin_3, col_fin_4 = st.columns(4)
    with col_fin_1:
        st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🔴 Responsable de carga</div>", unsafe_allow_html=True)
        responsable_de_carga = st.text_input("", key="responsable")

    # =========================
    # 💰 FINANCIAMIENTO
    # =========================

    if tipo != "Categorización Docente":

        with col_fin_2:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Tipo de financiamiento</div>", unsafe_allow_html=True)
            tipo_financiamiento = st.selectbox("", ["Seleccionar...", "Interno", "Externo", "Sin financiamiento"], key="fin")
        with col_fin_3:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Fuente de Financiamiento</div>", unsafe_allow_html=True)
            fuente_financiamiento = st.text_input("", key="fuente")
        with col_fin_4:
            st.markdown("<div style='margin-bottom:-10px; color:black; font-weight:700;'>🟢 Monto en pesos (sin puntos)</div>", unsafe_allow_html=True)
            monto_financiamiento = st.number_input("", min_value=0, step=1000, value=None, key="monto")

    else:
        tipo_financiamiento = ""
        fuente_financiamiento = ""
        monto_financiamiento = 0

    # =========================
    # 🔘 SUBMIT
    # =========================

    submit = st.form_submit_button("Clic para enviar al Consejo de Investigación (Google Sheets)")
    st.markdown("""
        <style>
        div[data-testid="stFormSubmitButton"] button {
            background-color: #7D1C1C !important;
            color: white !important;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
        }
        </style>
        """, unsafe_allow_html=True)

def enviar_correo_tema(fila):

    destinatarios = [
        "investigacion@uccuyo.edu.ar",
        "vincutec@uccuyo.edu.ar",
        "asistente.inv@uccuyo.edu.ar"
    ]

    cuerpo = f"""
Se ha cargado un nuevo tema para el Consejo de Investigación.

Número de Acta: {fila[0]}
Fecha: {fila[1]}
Año: {fila[2]}
Tipo: {fila[3]}
Título: {fila[4]}
Descripción: {fila[5]}
Director: {fila[6]}
Codirector: {fila[8]}
Equipo: {fila[10]}
Unidad Académica: {fila[13]}
Resolución CD: {fila[14]}
Resolución CS: {fila[15]}
Instituto: {fila[16]}
Cátedra: {fila[17]}
Financiamiento: {fila[18]}
Fuente: {fila[19]}
Monto: {fila[20]}
Alumnos: {fila[21]}
Puntaje: {puntaje_texto_para_word(fila[22]) or "N/D"}
Responsable de carga: {fila[23]}
"""

    msg = EmailMessage()
    msg["Subject"] = "Nuevo tema cargado - Consejo de Investigación"
    msg["From"] = st.secrets["email"]["EMAIL_USER"]
    msg["To"] = ", ".join(destinatarios)
    msg.set_content(cuerpo)
    
    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)

        server.login(
            st.secrets["email"]["EMAIL_USER"],
            st.secrets["email"]["EMAIL_PASS"]
        )

        server.send_message(msg)

# =========================
# 💾 GUARDAR
# =========================

if "enviado" not in st.session_state:
    st.session_state.enviado = False

if submit and not st.session_state.enviado:

    if tipo in TIPOS_CON_PUNTAJE:
        puntaje_fila, err_puntaje = parse_puntaje_campo_formulario(
            st.session_state.get("puntaje_informe_consejo", "")
        )
    else:
        puntaje_fila = 0.0
        err_puntaje = None

    if tipo_financiamiento == "Seleccionar...":
        tipo_financiamiento = ""

    unidad = "; ".join(unidades_sel)

    # 🔹 LIMPIAR "Seleccionar" (versión robusta)
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

    if monto_financiamiento is None:
        monto_financiamiento = ""

    anio_hoja = parse_anio_hoja(anio)

    fila = [
        int(numero_acta) if numero_acta is not None else numero_acta,
        fecha,
        anio_hoja,
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
        puntaje_a_texto_celda_sheet(puntaje_fila),
        responsable_de_carga
        ]

    # VALIDACIONES
    if anio_hoja is None:
        st.error("Debe ingresar un año válido de cuatro dígitos (ej: 2026)")

    elif not numero_acta:
        st.error("Debe seleccionar el Orden del día")

    elif not fecha:
        st.error("Debe seleccionar la fecha")

    elif not tipo:
        st.error("Debe elegir la actividad")

    elif not titulo.strip():
        st.error("Debe completar la Denominación de la actividad")

    elif not unidades_sel:
        st.error("Debe seleccionar al menos una Unidad Académica")

    elif len(unidades_sel) > MAX_UNIDADES_ACADEMICAS:
        st.error(
            f"Solo puede seleccionar hasta {MAX_UNIDADES_ACADEMICAS} unidades académicas. "
            "Quite una con la × e intente de nuevo."
        )

    elif contar_palabras(descripcion) > 50:
        st.error("La descripción no debe superar 50 palabras")

    elif contar_palabras(equipo) > 50:
        st.error("El equipo de investigación no debe superar 50 palabras")

    elif not responsable_de_carga.strip():
        st.error("Debe completar el Responsable de carga")

    elif err_puntaje:
        st.error(err_puntaje)

    else:
        sheet.append_row(fila, value_input_option=ValueInputOption.user_entered)

        try:
            enviar_correo_tema(fila)
        except Exception as e:
            st.warning(f"No se pudo enviar el correo automático: {e}")

        st.session_state.enviado = True
        st.success("✅ Registro guardado correctamente.\n\n📂 Ahora cargue el archivo correspondiente.\n\n🔄 Finalmente, vuelva a la página principal del sistema y recárgela para enviar otro tema.")
        st.markdown("""
        <a href="/Carga_de_Archivos" target="_self">
            <button style="
                background-color:#7D1C1C;
                color:white;
                width:auto;
                display:inline-block;
                text-align:left;
                padding:12px 20px;
                border:none;
                border-radius:10px;
                font-size:17px;
                font-weight:700;
                margin-top:10px;
                cursor:pointer;">
                📂 Ahora cargue el archivo correspondiente
            </button>
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        
    
# =========================
# 📄 GENERAR WORD
# =========================

st.markdown('<div id="descargar-orden-del-dia"></div>', unsafe_allow_html=True)

if _ir_a_descargar_od:
    components.html(
        """
        <script>
        (function () {
            function bajar() {
                const el = window.parent.document.getElementById("descargar-orden-del-dia");
                if (!el) return false;
                el.scrollIntoView({behavior: "smooth", block: "start"});
                return true;
            }
            [0, 300, 700, 1200, 2000, 3500].forEach(function (ms) {
                setTimeout(bajar, ms);
            });
        })();
        </script>
        """,
        height=0,
    )

st.markdown("## 📄 Generar y descargar Orden del Día")

OPCION_OD_SIN_SELECCION = "Seleccione el orden del día"
opciones_od_word = [OPCION_OD_SIN_SELECCION] + [
    f"{n} - {actas_dict[n]['mes']}" for n in actas_dict
]

acta_word = st.selectbox(
    "Seleccionar Orden del Día para generar y descargar",
    options=opciones_od_word,
    index=0,
)

generar = st.button("Generar Orden del Día")

if generar:
    st.session_state["_estuvo_en_seccion_od"] = True

    if acta_word == OPCION_OD_SIN_SELECCION:
        st.warning("Seleccione un orden del día antes de generar.")
    else:
        datos = sheet.get_all_records()

        acta_num = int(acta_word.split(" - ")[0])

        registros = [
            r for r in datos
            if str(r.get("numero_acta", "")).strip() == str(acta_num)
        ]
        registros = ordenar_registros_por_unidad_academica(registros)

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

                equipo_txt = r.get("equipo", "")

                if equipo_txt:
                    equipo_txt = equipo_txt.replace("\n", "; ")
                    p.add_run(f"   Equipo: {equipo_txt}\n")

                p.add_run(f"   Unidad Académica: {unidad}\n")

                raw_punt = r.get("puntaje")
                txt_puntaje = puntaje_texto_para_word(raw_punt)
                if txt_puntaje:
                    p.add_run(f"   Puntaje: {txt_puntaje}\n")

                if r.get("resolucion_cd"):
                    p.add_run(f"   Resolución CD: {r.get('resolucion_cd')}\n")

                if r.get("resolucion_cs"):
                    p.add_run(f"   Resolución CS del Proyecto: {r.get('resolucion_cs')}\n")

                if r.get("instituto"):
                    p.add_run(f"   Instituto: {r.get('instituto')}\n")

                if r.get("catedra"):
                    p.add_run(f"   Cátedra: {r.get('catedra')}\n")

                if r.get("tipo de financiamiento"):
                    p.add_run(f"   Financiamiento: {r.get('tipo de financiamiento')}\n")

                if r.get("fuente de financiamiento"):
                    p.add_run(f"   Fuente: {r.get('fuente de financiamiento')}\n")

                if r.get("responsable_de_carga"):
                    p.add_run(f"   Responsable de carga: {r.get('responsable_de_carga')}\n")

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
                "Descargar Orden del Día",
                data=buffer,
                file_name=f"Acta_{acta_num}.docx"
            )
        
st.markdown("### 🧾 Generar informe por responsable")

responsable_reporte = st.text_input("Responsable de carga para generar informe")

generar_responsables = st.button("Generar informe del responsable de carga")

if generar_responsables:

    if acta_word == OPCION_OD_SIN_SELECCION:
        st.warning("Seleccione un orden del día antes de generar el informe.")
    else:
        datos = sheet.get_all_records()

        acta_num = int(acta_word.split(" - ")[0])

        registros = [
            r for r in datos
            if str(r.get("numero_acta", "")).strip() == str(acta_num)
            and str(r.get("responsable_de_carga", "")).strip().lower() == responsable_reporte.strip().lower()
        ]
        registros = ordenar_registros_por_unidad_academica(registros)

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
                "Descargar informe del responsable de carga",
                data=buffer,
                file_name=f"Informe_{responsable_reporte}_Acta_{acta_num}.docx"
            )

if _ir_a_descargar_od or st.session_state.pop("_estuvo_en_seccion_od", False):
    st.session_state["volver_arriba_cargar_temas"] = True
