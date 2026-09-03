"""Menú de navegación visible en el contenido (celular y escritorio).

Enlaces HTML en la página principal: verde UCC 3D y rutas sin prefijo numérico
(igual que el menú lateral de Streamlit).
"""

from __future__ import annotations

import streamlit as st

# Rutas sin prefijo numérico (Streamlit: "1_Cargar_Foo.py" → "/Cargar_Foo").
_MENU_ENLACES: list[tuple[str, str]] = [
    ("/", "Inicio"),
    ("/Actas", "Actas"),
    ("/Cargar_Temas_al_Orden_del_Dia", "Cargar Temas"),
    ("/Descargar_Orden_del_Dia", "Descargar orden del día"),
    ("/Carga_de_Archivos", "Carga de Archivos"),
    ("/Publicaciones", "Publicaciones"),
]

_VERDE = "#064a3f"
_VERDE_CLARO = "#0a6b5c"
_VERDE_OSCURO = "#04352e"
_VERDE_SOMBRA = "#022821"


def _enlace(ruta: str, texto: str) -> str:
    return (
        f'<a class="ucc-nav-btn-3d" href="{ruta}">{texto}</a>'
    )


def render_menu_navegacion() -> None:
    st.markdown(
        f"""
        <style>
        a.ucc-nav-btn-3d {{
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
            width: 100%;
            min-height: 3rem;
            padding: 12px 10px;
            border-radius: 10px;
            background: linear-gradient(
                180deg,
                {_VERDE_CLARO} 0%,
                {_VERDE} 48%,
                {_VERDE_OSCURO} 100%
            );
            color: #ffffff !important;
            font-family: system-ui, -apple-system, sans-serif;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none !important;
            text-align: center;
            line-height: 1.25;
            border: 1px solid {_VERDE_SOMBRA};
            border-bottom-width: 3px;
            box-shadow:
                0 4px 0 {_VERDE_SOMBRA},
                0 6px 14px rgba(2, 40, 33, 0.28),
                inset 0 1px 0 rgba(255, 255, 255, 0.22);
            transition: transform 0.08s ease, box-shadow 0.08s ease, filter 0.12s ease;
        }}
        a.ucc-nav-btn-3d:hover {{
            background: linear-gradient(
                180deg,
                #0c7d6c 0%,
                #075a4e 50%,
                #053f36 100%
            );
            color: #ffffff !important;
            filter: brightness(1.05);
            box-shadow:
                0 3px 0 {_VERDE_SOMBRA},
                0 5px 12px rgba(2, 40, 33, 0.32),
                inset 0 1px 0 rgba(255, 255, 255, 0.28);
        }}
        a.ucc-nav-btn-3d:active {{
            transform: translateY(2px);
            box-shadow:
                0 1px 0 {_VERDE_SOMBRA},
                inset 0 2px 6px rgba(0, 0, 0, 0.35);
            border-bottom-width: 1px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

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
