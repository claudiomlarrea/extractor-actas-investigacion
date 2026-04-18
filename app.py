import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# =========================
# CONFIGURACIÓN
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = "17MiyW17W7oLlwSCKjDXCoA85CwBkYqHYhDkblVN37c8"  # 👈 CAMBIAR SI HICISTE COPIA

# =========================
# CONEXIÓN A GOOGLE
# =========================

def conectar():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    drive_service = build("drive", "v3", credentials=creds)

    try:
        sheet = client.open_by_key(SPREADSHEET_ID)
        sheet_actas = sheet.worksheet("Hoja 1")
        sheet_detalle = sheet.worksheet("Hoja 2")
    except Exception as e:
        st.error("❌ Error al acceder al Google Sheet")
        st.error("👉 Verificá:")
        st.write("- Que el ID sea correcto")
        st.write("- Que el archivo esté compartido con la cuenta de servicio")
        st.write("- Que las hojas se llamen exactamente 'Hoja 1' y 'Hoja 2'")
        raise e

    return drive_service, sheet_actas, sheet_detalle


# =========================
# PROCESAMIENTO
# =========================

def procesar_actas():
    try:
        drive, sheet_actas, sheet_detalle = conectar()

        st.success("✅ Conexión exitosa a Google Sheets")

        # Ejemplo: leer datos
        data = sheet_actas.get_all_records()

        st.subheader("📊 Datos encontrados")
        st.dataframe(data)

        st.success("🚀 Listo para procesar actas")

    except Exception as e:
        st.error("❌ Error al procesar las actas")
        st.exception(e)


# =========================
# INTERFAZ STREAMLIT
# =========================

st.set_page_config(page_title="Extractor de Actas", layout="wide")

st.title("📊 Extractor de Actas - Consejo de Investigación")

if st.button("🚀 Procesar actas"):
    procesar_actas()
