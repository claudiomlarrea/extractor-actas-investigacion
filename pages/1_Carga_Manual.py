import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("📥 Carga Manual de Actas")

# =========================
# 🔐 CONEXIÓN GOOGLE
# =========================

try:
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    SHEET_NAME = "Datos Consejo Investigación"
    sheet = client.open(SHEET_NAME).sheet1

    st.success("✅ Conectado a Google Sheets")

except Exception as e:
    st.error("❌ ERROR de conexión con Google Sheets")
    st.text(str(e))
    st.stop()

# =========================
# 📝 FORMULARIO
# =========================

anio = st.text_input("Año")
fecha = st.text_input("Fecha")
acta = st.text_input("Acta")

titulo_final = st.text_input("Título Informe Final")
director_final = st.text_input("Director Informe Final")
unidad_final = st.text_input("Unidad Académica Informe Final")
puntaje_final = st.text_input("Puntaje Informe Final")

titulo_avance = st.text_input("Título Informe de Avance")
director_avance = st.text_input("Director Informe de Avance")
unidad_avance = st.text_input("Unidad Académica Informe de Avance")
puntaje_avance = st.text_input("Puntaje Informe de Avance")

titulo_proy = st.text_input("Título Proyecto")
director_proy = st.text_input("Director Proyecto")
unidad_proy = st.text_input("Unidad Académica Proyecto")
puntaje_proy = st.text_input("Puntaje Proyecto")

categ_doc = st.text_input("Categorización Docente")
docente = st.text_input("Docente")
categoria = st.text_input("Categoría")

# =========================
# 💾 GUARDAR
# =========================

if st.button("Guardar en Google Sheets"):

    fila = [
        anio,
        fecha,
        acta,
        titulo_final,
        director_final,
        unidad_final,
        puntaje_final,
        titulo_avance,
        director_avance,
        unidad_avance,
        puntaje_avance,
        titulo_proy,
        director_proy,
        unidad_proy,
        puntaje_proy,
        categ_doc,
        docente,
        categoria
    ]

    try:
        sheet.append_row(fila)
        st.success("✅ Guardado en Google Sheets")

    except Exception as e:
        st.error("❌ Error al guardar")
        st.text(str(e))
