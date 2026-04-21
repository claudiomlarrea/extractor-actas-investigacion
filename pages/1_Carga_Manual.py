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

    # 👉 ID REAL de tu Google Sheets
    SHEET_ID = "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8"

    sh = client.open_by_key(SHEET_ID)

    # 👉 HOJA DONDE VA A GUARDAR (CAMBIAR SI QUERÉS)
    sheet = sh.worksheet("Hoja 2")

    st.success("✅ Conectado a Google Sheets")
    st.write("📍 Archivo:", sh.url)

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

tipo = st.selectbox("Tipo", ["Informe Final", "Informe de Avance", "Proyecto"])

descripcion = st.text_area("Descripción")

# =========================
# 💾 GUARDAR
# =========================

if st.button("Guardar en Google Sheets"):

    fila = [
        acta,
        fecha,
        anio,
        tipo,
        descripcion
    ]

    try:
        sheet.append_row(fila)
        st.success("✅ Guardado en Google Sheets")

    except Exception as e:
        st.error("❌ Error al guardar")
        st.text(str(e))
