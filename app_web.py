import streamlit as st
import pandas as pd
import os
import csv
import threading
import time
from io import StringIO, BytesIO
import zipfile
import hashlib
import shutil

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(
    page_title="Herramienta de Extracción de Datos",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar los scripts de extracción
apollo_script = None
try:
    import apollo_script
except ImportError:
    pass

# (Resto de imports de lusha_script, etc. se mantienen igual)

# ===== INICIALIZACIÓN DE SESSION STATE =====
if 'console_log' not in st.session_state:
    st.session_state.console_log = []
if 'output_files' not in st.session_state:
    st.session_state.output_files = []
if 'file_hashes' not in st.session_state:
    st.session_state.file_hashes = {}
if 'cached_data' not in st.session_state:
    st.session_state.cached_data = {}

# ===== FUNCIONES AUXILIARES =====

def log_message(message, placeholder=None):
    """Agrega un mensaje al log y actualiza la consola en pantalla inmediatamente."""
    timestamp = time.strftime("%H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    st.session_state.console_log.append(full_message)
    if placeholder:
        # Mostramos los últimos 20 mensajes para que la consola sea legible
        placeholder.code("\n".join(st.session_state.console_log[-20:]), language=None)

def read_csv_list(uploaded_file, cache_key=None):
    """Lee el CSV y permite la vista previa"""
    if uploaded_file is None: return []
    try:
        # Intentar leer con pandas para mayor rapidez en la vista previa
        df = pd.read_csv(uploaded_file, encoding='latin-1', header=0)
        # Tomar la primera columna
        result = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
        return [x for x in result if x]
    except:
        # Fallback a csv tradicional si falla pandas
        uploaded_file.seek(0)
        stringio = StringIO(uploaded_file.getvalue().decode('latin-1'))
        reader = csv.reader(stringio)
        next(reader, None)
        return [row[0].strip() for row in reader if row and row[0].strip()]

# (Funciones create_download_zip y clear_temp_folder se mantienen igual)

# ===== INTERFAZ PRINCIPAL =====
st.markdown('<div style="font-size: 1.5rem; font-weight: bold; color: #1f77b4; text-align: center; padding: 1rem 0;">🔍 Herramienta de Extracción v4.3</div>', unsafe_allow_html=True)

# SIDEBAR (API Keys y Países) - Igual que antes
# ... (Código de sidebar omitido por brevedad, mantener el tuyo) ...

# ÁREA PRINCIPAL
tab1, tab2 = st.tabs(["📊 Extracción de Contactos", "ℹ️ Instrucciones"])

with tab1:
    st.markdown("### 📁 Archivos de Entrada")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cargos_file = st.file_uploader("CSV de Cargos", type=['csv'], key="cargos")
        if cargos_file:
            cargos_list = read_csv_list(cargos_file, "cargos")
            if cargos_list:
                with st.expander(f"👀 Ver cargos ({len(cargos_list)})"):
                    st.write(cargos_list[:10])
                    if len(cargos_list) > 10: st.caption(f"... y {len(cargos_list)-10} más")

    with col2:
        empresas_file = st.file_uploader("CSV de Empresas", type=['csv'], key="empresas")
        if empresas_file:
            empresas_list = read_csv_list(empresas_file, "empresas")
            if empresas_list:
                with st.expander(f"👀 Ver empresas ({len(empresas_list)})"):
                    st.write(empresas_list[:10])
                    if len(empresas_list) > 10: st.caption(f"... y {len(empresas_list)-10} más")

    with col3:
        id_org_file = st.file_uploader("CSV de IDs Organizaciones", type=['csv'], key="id_org")
        if id_org_file:
            ids_list = read_csv_list(id_org_file, "ids")
            if ids_list:
                with st.expander(f"👀 Ver IDs ({len(ids_list)})"):
                    st.write(ids_list[:10])

    st.markdown("### 🚀 Ejecución")
    # --- CONSOLA DINÁMICA ---
    # Creamos el contenedor de la consola ANTES de los botones
    console_placeholder = st.empty()
    if st.session_state.console_log:
        console_placeholder.code("\n".join(st.session_state.console_log[-20:]), language=None)
    else:
        console_placeholder.info("Esperando inicio de proceso...")

    # Botones
    if st.button("🟡 Iniciar Apollo Contactos"):
        if apollo_api and cargos_file and empresas_file and selected_countries:
            st.session_state.output_files = []
            st.session_state.console_log = [] # Limpiar consola al empezar
            
            # Función local para que el script actualice la consola de Streamlit
            def live_log(msg): log_message(msg, placeholder=console_placeholder)
            
            with st.spinner('Extrayendo...'):
                # Llamar al script pasando la función de log dinámico
                import apollo_script
                output = apollo_script.run(apollo_api, empresas_list, cargos_list, selected_countries, "temp_output", live_log, threading.Event())
                
                # Procesar resultado final
                if output and os.path.exists(output) and os.path.getsize(output) > 100:
                    with open(output, 'r', encoding='utf-8') as f:
                        st.session_state.output_files.append(("resultados_apollo.csv", f.read()))
                    live_log("✅ Proceso terminado. Archivo listo.")
                else:
                    live_log("⚠️ No se generaron resultados nuevos.")
                st.rerun()

    # (Lógica de descarga idéntica a la anterior)
    # ...
