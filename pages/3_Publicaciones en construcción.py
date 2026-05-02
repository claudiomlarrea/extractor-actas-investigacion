import streamlit as st
import gspread
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials

from sheets_config import (
    get_google_sheet_id,
    LEGACY_WORKSHEET_PUBLICACIONES,
    WORKSHEET_PUBLICACIONES,
)

st.set_page_config(page_title="Producción Científica", layout="wide")

# =========================
# GOOGLE SHEETS — pestaña Publicaciones
# =========================

RESOLVED_SHEET_ID = get_google_sheet_id()

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Orden fijo de columnas (fila 1). Debe coincidir con cada append_row.
PUBLICACIONES_HEADERS = [
    "tipo_registro",
    "titulo",
    "autores",
    "unidad_academica",
    "revista",
    "indexacion",
    "indexacion_otra",
    "doi",
    "año",
    "tipo_libro_capitulo",
    "editorial",
    "isbn",
    "tipo_documento_repositorio",
    "repositorio",
    "repositorio_otro",
    "link_repositorio",
    "nombre_evento",
    "tipo_evento",
    "rol",
    "titulo_del_trabajo",
    "lugar",
    "fecha_evento",
    "medio_diario",
    "fecha_diario",
    "link_diario",
    "resumen_diario",
]

TIPO_REVISTA = "Revista científica"
TIPO_LIBRO = "Libro / Capítulo"
TIPO_REPO = "Repositorio"
TIPO_REUNION = "Reunión científica"
TIPO_DIARIO = "Diario"


def _blank_publicacion_fields() -> dict:
    return dict.fromkeys(PUBLICACIONES_HEADERS, "")


def _publicacion_fila(campos: dict) -> list:
    base = _blank_publicacion_fields()
    base.update(campos)
    return [base[h] for h in PUBLICACIONES_HEADERS]


def _fecha_str(val) -> str:
    if val is None:
        return ""
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


def _rango_encabezados() -> str:
    ncols = len(PUBLICACIONES_HEADERS)
    return f"A1:{rowcol_to_a1(1, ncols)}"


def _fijar_fila_encabezados(ws) -> None:
    ws.update(
        [PUBLICACIONES_HEADERS],
        range_name=_rango_encabezados(),
        value_input_option="USER_ENTERED",
    )


def _resolver_worksheet_publicaciones(libro):
    """Pestaña canónica publicaciones_sheet; si solo existe la vieja «Publicaciones», se usa esa."""
    try:
        return libro.worksheet(WORKSHEET_PUBLICACIONES), False
    except gspread.WorksheetNotFound:
        pass
    try:
        return libro.worksheet(LEGACY_WORKSHEET_PUBLICACIONES), True
    except gspread.WorksheetNotFound:
        ws = libro.add_worksheet(
            title=WORKSHEET_PUBLICACIONES,
            rows=3000,
            cols=len(PUBLICACIONES_HEADERS),
        )
        return ws, False


def _fila_encabezados_correcta(ws) -> bool:
    """True si la fila 1 tiene exactamente PUBLICACIONES_HEADERS (orden y texto)."""
    fila = ws.row_values(1)
    n = len(PUBLICACIONES_HEADERS)
    if len(fila) < n:
        return False
    for i in range(n):
        if str(fila[i]).strip() != PUBLICACIONES_HEADERS[i]:
            return False
    return True


def _hoja_publicaciones():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPE,
    )
    cliente = gspread.authorize(creds)
    libro = cliente.open_by_key(RESOLVED_SHEET_ID)
    ws, _legacy_flag = _resolver_worksheet_publicaciones(libro)

    if not _fila_encabezados_correcta(ws):
        _fijar_fila_encabezados(ws)
    return ws, _legacy_flag


def _obtener_hoja_publicaciones():
    try:
        ws, legacy = _hoja_publicaciones()
        return ws, None, legacy
    except Exception as exc:
        return None, exc, False


publicaciones_sheet, sheet_err, publicaciones_es_pestana_legacy = _obtener_hoja_publicaciones()


def _valor_texto(widget_key: str) -> str:
    v = st.session_state.get(widget_key)
    if v is None:
        return ""
    return str(v).strip()


def _unidad_valida(unidad: str) -> bool:
    u = unidad.strip()
    if not u or u.startswith("Seleccionar"):
        return False
    return True


def _guardar_fila(ws, fila: list) -> bool:
    try:
        ws.append_row(fila, value_input_option="USER_ENTERED")
    except Exception as exc:
        st.error(f"No se pudo escribir en Google Sheets: {exc}")
        return False
    return True


def _exito_escritura_en_sheet(ws, mensaje: str) -> None:
    """Evita confusiones entre planillas o pestañas: muestra libro y nombre de hoja según la API."""
    libro = getattr(getattr(ws, "spreadsheet", None), "title", "(sin título)") or "(sin título)"
    pestaña = getattr(ws, "title", WORKSHEET_PUBLICACIONES)
    st.success(mensaje)
    st.info(
        f'Se registró una fila en Drive en la pestaña **«{pestaña}»** dentro del libro **«{libro}»**. '
        f'Usá el enlace «abrir planilla» de arriba y mirá esa misma pestaña (refrescá Sheets con '
        f"F5). Si vacía igual: revisá si hay otra pestaña **«Publicaciones»** (versión vieja "
        "de la app) o que **GitHub → Streamlit Cloud** haya redesplegado este código."
        f"\n\n`RESOLVED_SHEET_ID`: `{RESOLVED_SHEET_ID}` — debe coincidir con `/d/` de tu libro "
        "(o definí `google_sheet_id` en Streamlit Secrets)."
    )


# =========================
# UNIDADES ACADÉMICAS
# =========================

UNIDADES = [
    "Seleccionar unidad académica",
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
]

st.title("📊 Producción Científica")

if sheet_err:
    st.error(
        "No hay conexión con Google Sheets. Revisá `secrets`/cuenta de servicio y "
        f"permisos sobre el libro. Detalle: {sheet_err}"
    )
else:
    _tab_real = getattr(publicaciones_sheet, "title", WORKSHEET_PUBLICACIONES)
    st.markdown(
        f"""
        <div style='background-color:#d4edda;padding:12px;border-radius:8px;margin-bottom:1rem'>
          <strong>Conectado</strong> — escritura en pestaña
          «{_tab_real}» —
          <a href='https://docs.google.com/spreadsheets/d/{RESOLVED_SHEET_ID}' target='_blank'>abrir planilla</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if publicaciones_es_pestana_legacy:
        st.warning(
            f'Los datos van a **«{LEGACY_WORKSHEET_PUBLICACIONES}»** porque no existe '
            f'**«{WORKSHEET_PUBLICACIONES}»**. Para usar solo la nueva pestaña, creala '
            '(o renombrá esta) como `publicaciones_sheet` en Google Sheets.'
        )
    st.caption(
        "Al cargar esta página se escribe la **fila 1** si faltan o no coinciden los encabezados "
        "(lista `PUBLICACIONES_HEADERS` en el código)."
    )
    with st.expander("Si la fila 1 necesita regenerarse"):
        if st.button("Sobrescribir encabezados (A1 → última columna)"):
            try:
                _fijar_fila_encabezados(publicaciones_sheet)
                st.success("Encabezados actualizados. Revisá la planilla.")
            except Exception as exc:
                st.error(f"No se pudo escribir en Sheets: {exc}")


# =========================
# TABS
# =========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📑 Revistas científicas",
    "📚 Libros / Capítulos",
    "🗂️ Repositorios",
    "🎓 Reuniones científicas",
    "📰 Diarios",
])

# =========================
# 1. REVISTAS
# =========================

with tab1:
    st.subheader("Carga de artículos científicos")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Título del artículo", key="titulo_revista")
        st.text_input("Autor/es", key="autores_revista")
        st.text_input("Revista", key="revista")

        indexacion = st.selectbox(
            "Indexación",
            ["Scopus", "WoS", "Scielo", "Otra"],
            key="indexacion",
        )

        if indexacion == "Otra":
            st.text_input(
                "Especificar indexación / base de datos",
                key="indexacion_otra",
            )

    with col2:
        st.text_input("DOI", key="doi")
        st.number_input("Año", 2000, 2030, 2025, key="año_revista")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_revista")

    if st.button("Guardar artículo", key="btn_revista"):
        if not publicaciones_sheet:
            st.error("Sin conexión a la planilla; no se guardó.")
        else:
            t = _valor_texto("titulo_revista")
            au = _valor_texto("autores_revista")
            unidad = _valor_texto("unidad_revista")
            if not t or not au or not _unidad_valida(unidad):
                st.error(
                    "Completá título, autores y elegí una unidad "
                    "(no puede quedar «Seleccionar unidad académica»)."
                )
            else:
                idx_otra = ""
                if st.session_state.get("indexacion") == "Otra":
                    idx_otra = _valor_texto("indexacion_otra")
                fila = _publicacion_fila({
                    "tipo_registro": TIPO_REVISTA,
                    "titulo": t,
                    "autores": au,
                    "unidad_academica": unidad,
                    "revista": _valor_texto("revista"),
                    "indexacion": st.session_state.get("indexacion", "") or "",
                    "indexacion_otra": idx_otra,
                    "doi": _valor_texto("doi"),
                    "año": st.session_state.get("año_revista", ""),
                })
                if _guardar_fila(publicaciones_sheet, fila):
                    _exito_escritura_en_sheet(publicaciones_sheet, "Artículo registrado")

# =========================
# 2. LIBROS
# =========================

with tab2:
    st.subheader("Carga de libros y capítulos")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Título", key="titulo_libro")
        st.text_input("Autor/es", key="autores_libro")
        st.selectbox("Tipo", ["Libro", "Capítulo de libro"], key="tipo_libro")

    with col2:
        st.text_input("Editorial", key="editorial")
        st.text_input("ISBN", key="isbn")
        st.number_input("Año", 2000, 2030, 2025, key="año_libro")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_libro")

    if st.button("Guardar libro/capítulo", key="btn_libro"):
        if not publicaciones_sheet:
            st.error("Sin conexión a la planilla; no se guardó.")
        else:
            t = _valor_texto("titulo_libro")
            au = _valor_texto("autores_libro")
            unidad = _valor_texto("unidad_libro")
            if not t or not au or not _unidad_valida(unidad):
                st.error(
                    "Completá título, autores y elegí una unidad "
                    "(no puede quedar «Seleccionar unidad académica»)."
                )
            else:
                fila = _publicacion_fila({
                    "tipo_registro": TIPO_LIBRO,
                    "titulo": t,
                    "autores": au,
                    "unidad_academica": unidad,
                    "año": st.session_state.get("año_libro", ""),
                    "tipo_libro_capitulo": st.session_state.get("tipo_libro", "") or "",
                    "editorial": _valor_texto("editorial"),
                    "isbn": _valor_texto("isbn"),
                })
                if _guardar_fila(publicaciones_sheet, fila):
                    _exito_escritura_en_sheet(publicaciones_sheet, "Registro guardado")

# =========================
# 3. REPOSITORIOS
# =========================

with tab3:
    st.subheader("Carga en repositorios")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Título del trabajo", key="titulo_repo")
        st.text_input("Autor/es", key="autores_repo")
        st.selectbox(
            "Tipo",
            ["Artículo", "Informe técnico", "Tesis", "Documento institucional"],
            key="tipo_repo",
        )

    with col2:
        repositorio = st.selectbox(
            "Repositorio",
            ["Repositorio UCCuyo", "CONICET", "Otro"],
            key="repositorio",
        )

        if repositorio == "Otro":
            st.text_input("Especificar repositorio", key="repositorio_otro")

        st.text_input("Link", key="link_repo")
        st.number_input("Año", 2000, 2030, 2025, key="año_repo")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_repo")

    if st.button("Guardar en repositorio", key="btn_repo"):
        if not publicaciones_sheet:
            st.error("Sin conexión a la planilla; no se guardó.")
        else:
            t = _valor_texto("titulo_repo")
            au = _valor_texto("autores_repo")
            unidad = _valor_texto("unidad_repo")
            if not t or not au or not _unidad_valida(unidad):
                st.error(
                    "Completá título, autores y elegí una unidad "
                    "(no puede quedar «Seleccionar unidad académica»)."
                )
            else:
                otro_nom = ""
                if st.session_state.get("repositorio") == "Otro":
                    otro_nom = _valor_texto("repositorio_otro")
                fila = _publicacion_fila({
                    "tipo_registro": TIPO_REPO,
                    "titulo": t,
                    "autores": au,
                    "unidad_academica": unidad,
                    "año": st.session_state.get("año_repo", ""),
                    "tipo_documento_repositorio": st.session_state.get("tipo_repo", "") or "",
                    "repositorio": st.session_state.get("repositorio", "") or "",
                    "repositorio_otro": otro_nom,
                    "link_repositorio": _valor_texto("link_repo"),
                })
                if _guardar_fila(publicaciones_sheet, fila):
                    _exito_escritura_en_sheet(publicaciones_sheet, "Registro guardado")

# =========================
# 4. REUNIONES CIENTÍFICAS
# =========================

with tab4:
    st.subheader("Reuniones científicas")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Nombre del evento", key="evento")
        st.selectbox(
            "Tipo",
            ["Congreso", "Jornada", "Seminario", "Workshop"],
            key="tipo_evento",
        )
        st.selectbox(
            "Rol",
            ["Expositor", "Asistente", "Organizador"],
            key="rol",
        )

    with col2:
        st.text_input("Título del trabajo", key="trabajo")
        st.text_input("Lugar", key="lugar")
        st.date_input("Fecha", key="fecha")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_evento")

    if st.button("Guardar evento", key="btn_evento"):
        if not publicaciones_sheet:
            st.error("Sin conexión a la planilla; no se guardó.")
        else:
            ev_nombre = _valor_texto("evento")
            unidad = _valor_texto("unidad_evento")
            if not ev_nombre or not _unidad_valida(unidad):
                st.error(
                    "Completá nombre del evento y elegí una unidad válida "
                    "(no puede quedar «Seleccionar unidad académica»)."
                )
            else:
                fila = _publicacion_fila({
                    "tipo_registro": TIPO_REUNION,
                    "unidad_academica": unidad,
                    "nombre_evento": ev_nombre,
                    "tipo_evento": st.session_state.get("tipo_evento", "") or "",
                    "rol": st.session_state.get("rol", "") or "",
                    "titulo_del_trabajo": _valor_texto("trabajo"),
                    "lugar": _valor_texto("lugar"),
                    "fecha_evento": _fecha_str(st.session_state.get("fecha")),
                })
                if _guardar_fila(publicaciones_sheet, fila):
                    _exito_escritura_en_sheet(publicaciones_sheet, "Evento registrado")

# =========================
# 5. DIARIOS
# =========================

with tab5:
    st.subheader("Publicaciones en diarios")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Título del artículo", key="titulo_diario")
        st.text_input("Medio (ej: Diario de Cuyo)", key="medio")
        st.text_input("Autor/es", key="autor_diario")

    with col2:
        st.date_input("Fecha", key="fecha_diario")
        st.text_input("Link", key="link_diario")
        st.selectbox("Unidad Académica", UNIDADES, key="unidad_diario")

    st.text_area("Resumen", key="resumen_diario")

    if st.button("Guardar publicación en diario", key="btn_diario"):
        if not publicaciones_sheet:
            st.error("Sin conexión a la planilla; no se guardó.")
        else:
            t = _valor_texto("titulo_diario")
            au = _valor_texto("autor_diario")
            unidad = _valor_texto("unidad_diario")
            if not t or not au or not _unidad_valida(unidad):
                st.error(
                    "Completá título, autores y elegí una unidad "
                    "(no puede quedar «Seleccionar unidad académica»)."
                )
            else:
                fila = _publicacion_fila({
                    "tipo_registro": TIPO_DIARIO,
                    "titulo": t,
                    "autores": au,
                    "unidad_academica": unidad,
                    "medio_diario": _valor_texto("medio"),
                    "fecha_diario": _fecha_str(st.session_state.get("fecha_diario")),
                    "link_diario": _valor_texto("link_diario"),
                    "resumen_diario": _valor_texto("resumen_diario"),
                })
                if _guardar_fila(publicaciones_sheet, fila):
                    _exito_escritura_en_sheet(publicaciones_sheet, "Publicación registrada")

# =========================
# FIN
# =========================

st.markdown("---")
st.caption("Sistema de Producción Científica - UCCuyo")
