"""Atajo del menú lateral: abre Cargar Temas y baja a generar/descargar el Orden del Día."""

import streamlit as st

st.session_state["_pagina_streamlit_prev"] = "descargar_od"
st.session_state["ir_a_descargar_orden_dia"] = True
st.switch_page("pages/1_Cargar_Temas_al_Orden_del_Dia.py")
