import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# 🔐 ID de tu Google Sheet (el que ya estás usando)
SPREADSHEET_ID = "17MiyW17W7oLlwSCKjDXCoA85CwBkYqHYhDkblVN37c8"

# 🔌 CONEXIÓN SEGURA
def conectar():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID)

    # ⚠️ NO usar nombres → usar índice
    sheet_actas = sheet.get_worksheet(0)    # Hoja 1
    sheet_detalle = sheet.get_worksheet(1)  # Hoja 2

    return sheet_actas, sheet_detalle


# 🚀 PROCESAMIENTO SIMPLE (ejemplo base)
def procesar_actas():
    sheet_actas, sheet_detalle = conectar()

    data = sheet_actas.get_all_records()

    if not data:
        st.warning("No hay datos en la hoja.")
        return

    st.success(f"Se cargaron {len(data)} registros")

    for fila in data:
        st.write(fila)


# 🎨 INTERFAZ
st.set_page_config(page_title="Extractor de Actas", layout="wide")

st.title("📊 Extractor de Actas - Consejo de Investigación")

if st.button("🚀 Procesar actas"):
    try:
        procesar_actas()
    except Exception as e:
        st.error("Error al procesar las actas")
        st.exception(e)
