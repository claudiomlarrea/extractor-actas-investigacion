"""Quita la barra superior derecha de Streamlit (avatar, Deploy, menú ⋮).

Esa UI la inyecta Streamlit Community Cloud / el cliente; no es el logo UCC
ni ninguna imagen del repositorio. Sin esto, a veces se ve la foto de la
cuenta con la que está publicada la app.
"""

from __future__ import annotations

import streamlit as st


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
