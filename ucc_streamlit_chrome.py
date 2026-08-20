"""Quita la barra superior derecha de Streamlit (avatar, Deploy, menú ⋮)
y aplica el estilo 3D de botones del Consejo de Investigación.

Esa UI la inyecta Streamlit Community Cloud / el cliente; no es el logo UCC
ni ninguna imagen del repositorio. Sin esto, a veces se ve la foto de la
cuenta con la que está publicada la app.
"""

from __future__ import annotations

import streamlit as st

# Bordó institucional (mismo tono del envío al Consejo)
_BORDO = "#7D1C1C"
_BORDO_CLARO = "#a32828"
_BORDO_OSCURO = "#5c1515"
_BORDO_SOMBRA = "#3d0c0c"
_MAIN = ':is(section.main, [data-testid="stMain"])'


def inject_botones_3d_consejo() -> None:
    """Botones principales en bordó 3D con degradé (área principal, no sidebar)."""
    st.markdown(
        f"""
        <style>
        /* ——— Botones Streamlit (área principal): bordó 3D + degradé ——— */
        {_MAIN} div[data-testid="stButton"] > button,
        {_MAIN} div[data-testid="stDownloadButton"] > button,
        {_MAIN} div[data-testid="stFormSubmitButton"] > button,
        {_MAIN} [data-testid="stBaseButton-secondary"],
        {_MAIN} [data-testid="stBaseButton-primary"],
        {_MAIN} .st-key-od_acciones_bordo button,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button {{
            background: linear-gradient(
                180deg,
                {_BORDO_CLARO} 0%,
                {_BORDO} 48%,
                {_BORDO_OSCURO} 100%
            ) !important;
            background-image: linear-gradient(
                180deg,
                {_BORDO_CLARO} 0%,
                {_BORDO} 48%,
                {_BORDO_OSCURO} 100%
            ) !important;
            color: #ffffff !important;
            border: 1px solid {_BORDO_SOMBRA} !important;
            border-bottom-width: 3px !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow:
                0 4px 0 {_BORDO_SOMBRA},
                0 6px 14px rgba(61, 12, 12, 0.28),
                inset 0 1px 0 rgba(255, 255, 255, 0.28) !important;
            transition: transform 0.08s ease, box-shadow 0.08s ease, filter 0.12s ease !important;
        }}

        {_MAIN} div[data-testid="stButton"] > button p,
        {_MAIN} div[data-testid="stButton"] > button span,
        {_MAIN} div[data-testid="stDownloadButton"] > button p,
        {_MAIN} div[data-testid="stDownloadButton"] > button span,
        {_MAIN} div[data-testid="stFormSubmitButton"] > button p,
        {_MAIN} div[data-testid="stFormSubmitButton"] > button span,
        {_MAIN} .st-key-od_acciones_bordo button p,
        {_MAIN} .st-key-od_acciones_bordo button span,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button p,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button span {{
            color: #ffffff !important;
        }}

        {_MAIN} div[data-testid="stButton"] > button:hover,
        {_MAIN} div[data-testid="stDownloadButton"] > button:hover,
        {_MAIN} div[data-testid="stFormSubmitButton"] > button:hover,
        {_MAIN} .st-key-od_acciones_bordo button:hover,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button:hover {{
            background: linear-gradient(
                180deg,
                #b52e2e 0%,
                #8f2020 50%,
                #6b1818 100%
            ) !important;
            background-image: linear-gradient(
                180deg,
                #b52e2e 0%,
                #8f2020 50%,
                #6b1818 100%
            ) !important;
            color: #ffffff !important;
            filter: brightness(1.04);
            box-shadow:
                0 3px 0 {_BORDO_SOMBRA},
                0 5px 12px rgba(61, 12, 12, 0.32),
                inset 0 1px 0 rgba(255, 255, 255, 0.32) !important;
        }}

        {_MAIN} div[data-testid="stButton"] > button:active,
        {_MAIN} div[data-testid="stDownloadButton"] > button:active,
        {_MAIN} div[data-testid="stFormSubmitButton"] > button:active,
        {_MAIN} .st-key-od_acciones_bordo button:active,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button:active {{
            transform: translateY(2px) !important;
            box-shadow:
                0 1px 0 {_BORDO_SOMBRA},
                inset 0 2px 6px rgba(0, 0, 0, 0.35) !important;
            border-bottom-width: 1px !important;
        }}

        {_MAIN} div[data-testid="stButton"] > button:disabled,
        {_MAIN} div[data-testid="stDownloadButton"] > button:disabled,
        {_MAIN} .st-key-od_acciones_bordo button:disabled,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button:disabled {{
            background: linear-gradient(
                180deg,
                {_BORDO_CLARO} 0%,
                {_BORDO} 48%,
                {_BORDO_OSCURO} 100%
            ) !important;
            color: #ffffff !important;
            opacity: 0.55 !important;
            box-shadow: 0 2px 0 {_BORDO_SOMBRA} !important;
            transform: none !important;
        }}

        /* Enlace HTML con aspecto de botón (p. ej. ir a Carga de Archivos) */
        {_MAIN} a > button.ucc-btn-3d,
        {_MAIN} button.ucc-btn-3d {{
            background: linear-gradient(
                180deg,
                {_BORDO_CLARO} 0%,
                {_BORDO} 48%,
                {_BORDO_OSCURO} 100%
            ) !important;
            color: #ffffff !important;
            border: 1px solid {_BORDO_SOMBRA} !important;
            border-bottom-width: 3px !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            box-shadow:
                0 4px 0 {_BORDO_SOMBRA},
                0 6px 14px rgba(61, 12, 12, 0.28),
                inset 0 1px 0 rgba(255, 255, 255, 0.28) !important;
            cursor: pointer;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hide_streamlit_cloud_toolbar() -> None:
    st.markdown(
        """
        <style>
        /* Barra derecha del header (avatar, Deploy, menú de Streamlit) */
        [data-testid="stHeader"] [data-testid="stToolbar"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    inject_botones_3d_consejo()
