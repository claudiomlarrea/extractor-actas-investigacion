"""Atajo del menú lateral: abre Actas y baja a generar/descargar el Orden del Día."""

import streamlit as st

st.session_state["_pagina_streamlit_prev"] = "descargar_od"
st.session_state["ir_a_descargar_orden_dia"] = True
st.session_state.pop("volver_dashboard_actas", None)
st.session_state.pop("volver_arriba_cargar_temas", None)
st.switch_page("pages/0_Actas.py")
