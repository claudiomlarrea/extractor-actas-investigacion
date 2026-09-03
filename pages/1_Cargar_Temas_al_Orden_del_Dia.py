"""Atajo del menú: abre Actas y baja al Paso 1 (cargar tema)."""

import streamlit as st

st.session_state["_pagina_streamlit_prev"] = "cargar_temas_menu"
st.session_state["volver_arriba_cargar_temas"] = True
st.session_state.pop("_mantener_scroll_descargar_od", None)
st.session_state.pop("volver_dashboard_actas", None)
st.session_state.pop("ir_a_descargar_orden_dia", None)
st.switch_page("pages/0_Actas.py")
