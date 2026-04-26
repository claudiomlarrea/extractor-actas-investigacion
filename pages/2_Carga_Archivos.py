import streamlit as st

st.set_page_config(page_title="Carga de Archivos", layout="wide")

st.title("📂 Carga de Archivos de Actas")

st.markdown("Suba el archivo correspondiente al acta")

archivo = st.file_uploader(
    "Seleccionar archivo",
    type=["pdf", "docx"]
)

if archivo is not None:
    st.success("Archivo cargado correctamente")

    st.write("Nombre:", archivo.name)
    st.write("Tipo:", archivo.type)
    st.write("Tamaño (KB):", round(len(archivo.getvalue()) / 1024, 2))
