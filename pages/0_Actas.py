"""Atajo del menú lateral: abre el dashboard de actas (tablero superior)."""

import streamlit as st

st.session_state["_pagina_streamlit_prev"] = "actas"
st.session_state["volver_dashboard_actas"] = True
st.session_state.pop("_mantener_scroll_descargar_od", None)
st.session_state.pop("volver_arriba_cargar_temas", None)
st.session_state.pop("ir_a_descargar_orden_dia", None)
st.switch_page("pages/1_Cargar_Temas_al_Orden_del_Dia.py")
