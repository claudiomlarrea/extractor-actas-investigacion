
import streamlit as st
import pandas as pd

st.title("📥 Carga Manual de Actas")

# Campos principales
anio = st.text_input("Año")
fecha = st.text_input("Fecha")
acta = st.text_input("Acta")

st.subheader("📄 Informe Final")
titulo_final = st.text_input("Título Informe Final")
director_final = st.text_input("Director Informe Final")
unidad_final = st.text_input("Unidad Académica Informe Final")
puntaje_final = st.text_input("Puntaje Informe Final")

st.subheader("📄 Informe de Avance")
titulo_avance = st.text_input("Título Informe de Avance")
director_avance = st.text_input("Director Informe de Avance")
unidad_avance = st.text_input("Unidad Académica Informe de Avance")
puntaje_avance = st.text_input("Puntaje Informe de Avance")

st.subheader("📄 Proyecto de Investigación")
titulo_proy = st.text_input("Título Proyecto")
director_proy = st.text_input("Director Proyecto")
unidad_proy = st.text_input("Unidad Académica Proyecto")
puntaje_proy = st.text_input("Puntaje Proyecto")

st.subheader("👤 Docente")
categ_doc = st.text_input("Categorización Docente")
docente = st.text_input("Docente")
categoria = st.text_input("Categoría")

if st.button("Guardar registro"):

    data = {
        "Año": anio,
        "Fecha": fecha,
        "Acta": acta,
        "Título Informe Final": titulo_final,
        "Director Informe Final": director_final,
        "Unidad Académica Informe Final": unidad_final,
        "Puntaje Informe Final": puntaje_final,
        "Título Informe de Avance": titulo_avance,
        "Director Informe de Avance": director_avance,
        "Unidad Académica Informe de Avance": unidad_avance,
        "Puntaje Informe de Avance": puntaje_avance,
        "Título Proyecto": titulo_proy,
        "Director Proyecto": director_proy,
        "Unidad Académica Proyecto": unidad_proy,
        "Puntaje Proyecto": puntaje_proy,
        "Categorización Docente": categ_doc,
        "Docente": docente,
        "Categoría": categoria
    }

    df = pd.DataFrame([data])
    st.success("Registro cargado correctamente")
    st.dataframe(df)
