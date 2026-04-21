import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")

st.title("📊 Carga de Actas - Consejo de Investigación")

# =========================
# 🔐 CONEXIÓN GOOGLE SHEETS
# =========================
def conectar_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("Actas Investigacion").sheet1

    return sheet


# =========================
# 🧠 ESTADO
# =========================
if "registros" not in st.session_state:
    st.session_state.registros = []


# =========================
# 📌 DATOS DEL ACTA
# =========================
st.subheader("📄 Datos del Acta")

col1, col2, col3 = st.columns(3)

anio = col1.text_input("Año")
fecha = col2.text_input("Fecha")
acta = col3.text_input("N° Acta")


# =========================
# ➕ AGREGAR REGISTROS
# =========================
st.subheader("➕ Agregar ítem")

tipo = st.selectbox("Tipo", [
    "Informe Final",
    "Informe de Avance",
    "Proyecto",
    "Categorización"
])

titulo = st.text_input("Título / Descripción")
director = st.text_input("Director / Responsable")
unidad = st.text_input("Unidad Académica")
puntaje = st.text_input("Puntaje")

docente = ""
categoria = ""

if tipo == "Categorización":
    docente = st.text_input("Docente")
    categoria = st.text_input("Categoría")

if st.button("➕ Agregar a la lista"):
    st.session_state.registros.append({
        "Año": anio,
        "Fecha": fecha,
        "Acta": acta,
        "Tipo": tipo,
        "Título": titulo,
        "Director": director,
        "Unidad": unidad,
        "Puntaje": puntaje,
        "Docente": docente,
        "Categoría": categoria
    })


# =========================
# 📊 MOSTRAR DATOS
# =========================
if st.session_state.registros:
    st.subheader("📋 Registros cargados")

    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df)


# =========================
# 💾 GUARDAR EN SHEETS
# =========================
if st.button("💾 Guardar en Google Sheets"):

    sheet = conectar_sheets()

    for r in st.session_state.registros:
        sheet.append_row([
            r["Año"],
            r["Fecha"],
            r["Acta"],
            r["Tipo"],
            r["Título"],
            r["Director"],
            r["Unidad"],
            r["Puntaje"],
            r["Docente"],
            r["Categoría"]
        ])

    st.success("✅ Datos guardados correctamente")

    st.session_state.registros = []
