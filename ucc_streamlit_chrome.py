"""Quita la barra superior derecha de Streamlit (avatar, Deploy, menú ⋮)
y aplica el estilo 3D de botones del Consejo de Investigación.

Esa UI la inyecta Streamlit Community Cloud / el cliente; no es el logo UCC
ni ninguna imagen del repositorio. Sin esto, a veces se ve la foto de la
cuenta con la que está publicada la app.
"""

from __future__ import annotations

import streamlit as st

# Bordó institucional (enviar / OD / descargas de acta)
_BORDO = "#7D1C1C"
_BORDO_CLARO = "#a32828"
_BORDO_OSCURO = "#5c1515"
_BORDO_SOMBRA = "#3d0c0c"

# Verde UCC (mismo tono de los enlaces de navegación)
_VERDE = "#064a3f"
_VERDE_CLARO = "#0a6b5c"
_VERDE_OSCURO = "#04352e"
_VERDE_SOMBRA = "#022821"

_MAIN = ':is(section.main, [data-testid="stMain"])'


def inject_botones_3d_consejo() -> None:
    """3D con degradé: bordó solo donde ya era bordó; el resto verde UCC."""
    st.markdown(
        f"""
        <style>
        /* ——— Bordó 3D: envío al Consejo, acciones OD, enlace a archivos ——— */
        {_MAIN} div[data-testid="stFormSubmitButton"] > button,
        {_MAIN} .st-key-od_acciones_bordo button,
        {_MAIN} .st-key-od_acciones_bordo [data-testid="stDownloadButton"] > button,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button,
        {_MAIN} a > button.ucc-btn-3d,
        {_MAIN} button.ucc-btn-3d {{
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
            cursor: pointer;
        }}

        {_MAIN} div[data-testid="stFormSubmitButton"] > button p,
        {_MAIN} div[data-testid="stFormSubmitButton"] > button span,
        {_MAIN} .st-key-od_acciones_bordo button p,
        {_MAIN} .st-key-od_acciones_bordo button span,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button p,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button span {{
            color: #ffffff !important;
        }}

        {_MAIN} div[data-testid="stFormSubmitButton"] > button:hover,
        {_MAIN} .st-key-od_acciones_bordo button:hover,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button:hover,
        {_MAIN} button.ucc-btn-3d:hover {{
            background: linear-gradient(
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

        {_MAIN} div[data-testid="stFormSubmitButton"] > button:active,
        {_MAIN} .st-key-od_acciones_bordo button:active,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button:active,
        {_MAIN} button.ucc-btn-3d:active {{
            transform: translateY(2px) !important;
            box-shadow:
                0 1px 0 {_BORDO_SOMBRA},
                inset 0 2px 6px rgba(0, 0, 0, 0.35) !important;
            border-bottom-width: 1px !important;
        }}

        {_MAIN} .st-key-od_acciones_bordo button:disabled,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] button:disabled {{
            opacity: 0.55 !important;
            box-shadow: 0 2px 0 {_BORDO_SOMBRA} !important;
            transform: none !important;
        }}

        /* ——— Verde 3D: demás botones Streamlit del área principal ——— */
        {_MAIN} div[data-testid="stButton"] > button,
        {_MAIN} div[data-testid="stDownloadButton"] > button,
        {_MAIN} [data-testid="stBaseButton-secondary"],
        {_MAIN} [data-testid="stBaseButton-primary"] {{
            background: linear-gradient(
                180deg,
                {_VERDE_CLARO} 0%,
                {_VERDE} 48%,
                {_VERDE_OSCURO} 100%
            ) !important;
            background-image: linear-gradient(
                180deg,
                {_VERDE_CLARO} 0%,
                {_VERDE} 48%,
                {_VERDE_OSCURO} 100%
            ) !important;
            color: #ffffff !important;
            border: 1px solid {_VERDE_SOMBRA} !important;
            border-bottom-width: 3px !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow:
                0 4px 0 {_VERDE_SOMBRA},
                0 6px 14px rgba(2, 40, 33, 0.28),
                inset 0 1px 0 rgba(255, 255, 255, 0.22) !important;
            transition: transform 0.08s ease, box-shadow 0.08s ease, filter 0.12s ease !important;
        }}

        {_MAIN} div[data-testid="stButton"] > button p,
        {_MAIN} div[data-testid="stButton"] > button span,
        {_MAIN} div[data-testid="stDownloadButton"] > button p,
        {_MAIN} div[data-testid="stDownloadButton"] > button span {{
            color: #ffffff !important;
        }}

        {_MAIN} div[data-testid="stButton"] > button:hover,
        {_MAIN} div[data-testid="stDownloadButton"] > button:hover {{
            background: linear-gradient(
                180deg,
                #0c7d6c 0%,
                #075a4e 50%,
                #053f36 100%
            ) !important;
            color: #ffffff !important;
            filter: brightness(1.05);
            box-shadow:
                0 3px 0 {_VERDE_SOMBRA},
                0 5px 12px rgba(2, 40, 33, 0.32),
                inset 0 1px 0 rgba(255, 255, 255, 0.28) !important;
        }}

        {_MAIN} div[data-testid="stButton"] > button:active,
        {_MAIN} div[data-testid="stDownloadButton"] > button:active {{
            transform: translateY(2px) !important;
            box-shadow:
                0 1px 0 {_VERDE_SOMBRA},
                inset 0 2px 6px rgba(0, 0, 0, 0.35) !important;
            border-bottom-width: 1px !important;
        }}

        {_MAIN} div[data-testid="stButton"] > button:disabled,
        {_MAIN} div[data-testid="stDownloadButton"] > button:disabled {{
            opacity: 0.55 !important;
            box-shadow: 0 2px 0 {_VERDE_SOMBRA} !important;
            transform: none !important;
        }}

        /*
          Los botones bordó viven dentro de stButton/stDownloadButton:
          reafirmar bordó con mayor especificidad para que no los pinte el verde.
        */
        {_MAIN} .st-key-od_acciones_bordo div[data-testid="stButton"] > button,
        {_MAIN} .st-key-od_acciones_bordo div[data-testid="stDownloadButton"] > button,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] > button,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stDownloadButton"] > button,
        {_MAIN} div[data-testid="stFormSubmitButton"] > button {{
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
            border-color: {_BORDO_SOMBRA} !important;
            box-shadow:
                0 4px 0 {_BORDO_SOMBRA},
                0 6px 14px rgba(61, 12, 12, 0.28),
                inset 0 1px 0 rgba(255, 255, 255, 0.28) !important;
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
