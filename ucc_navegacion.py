"""Menú de navegación visible en el contenido (celular y escritorio).

Enlaces HTML en la página principal: verde UCC y rutas sin prefijo numérico
(igual que el menú lateral de Streamlit).
"""

from __future__ import annotations

import streamlit as st

# Rutas sin prefijo numérico (Streamlit: "1_Cargar_Foo.py" → "/Cargar_Foo").
_MENU_ENLACES: list[tuple[str, str]] = [
    ("/", "Inicio"),
    ("/Cargar_Temas_al_Orden_del_Dia", "Cargar Temas"),
    ("/Descargar_Orden_del_Dia", "Descargar orden del día"),
    ("/Carga_de_Archivos", "Carga de Archivos"),
    ("/Publicaciones", "Publicaciones"),
]

_ESTILO_ENLACE = (
    "display:flex;align-items:center;justify-content:center;"
    "box-sizing:border-box;width:100%;min-height:3rem;padding:12px 10px;"
    "border-radius:10px;background-color:#064a3f;color:#ffffff;"
    "font-family:system-ui,-apple-system,sans-serif;font-weight:600;font-size:14px;"
    "text-decoration:none;text-align:center;line-height:1.25;"
    "border:1px solid #053a32;"
)


def _enlace(ruta: str, texto: str) -> str:
    return f'<a href="{ruta}" style="{_ESTILO_ENLACE}">{texto}</a>'


def render_menu_navegacion() -> None:
    st.markdown(
        '<p style="font-size:0.95rem;font-weight:700;color:#064a3f;margin:0 0 0.5rem 0;">'
        "Secciones del sistema</p>",
        unsafe_allow_html=True,
    )

    fila1 = "".join(_enlace(h, t) for h, t in _MENU_ENLACES[:2])
    fila2 = "".join(_enlace(h, t) for h, t in _MENU_ENLACES[2:4])
    fila3 = _enlace(_MENU_ENLACES[4][0], _MENU_ENLACES[4][1])

    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
            {fila1}
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
            {fila2}
        </div>
        <div style="margin-bottom:12px;">
            {fila3}
        </div>
        """,
        unsafe_allow_html=True,
    )
