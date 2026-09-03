import streamlit as st

st.set_page_config(page_title="Sistema de Actas", layout="wide")

# Entrada principal: dashboard de actas
st.session_state["_pagina_streamlit_prev"] = "app"
st.session_state["volver_dashboard_actas"] = True
st.session_state.pop("_mantener_scroll_descargar_od", None)
st.session_state.pop("volver_arriba_cargar_temas", None)
st.session_state.pop("ir_a_descargar_orden_dia", None)
st.switch_page("pages/0_Actas.py")
