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
try:
    import apollo_script
    import apollo_org
    import lusha_script
    import lusha_org
except ImportError as e:
    st.warning(f"Advertencia: Algunos módulos no se cargaron: {e}")

# ===== ESTILOS =====
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: bold; color: #1f77b4; text-align: center; padding: 1rem 0; }
    .section-header { font-size: 1.3rem; font-weight: bold; color: #ff7f0e; margin-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ===== INICIALIZACIÓN DE SESSION STATE =====
if 'console_log' not in st.session_state:
    st.session_state.console_log = []
if 'output_files' not in st.session_state:
    st.session_state.output_files = []

# ===== FUNCIONES AUXILIARES =====

def log_message(message, placeholder=None):
    """Actualiza la consola en tiempo real"""
    timestamp = time.strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {message}"
    st.session_state.console_log.append(full_msg)
    if placeholder:
        # Mostramos los últimos 15 mensajes para fluidez
        placeholder.code("\n".join(st.session_state.console_log[-15:]), language=None)

def read_csv_list(uploaded_file):
    """Lee el CSV y retorna lista de la primera columna"""
    if uploaded_file is None: return []
    try:
        # Leemos el contenido para no agotar el buffer del archivo
        content = uploaded_file.getvalue()
        # Intentar varias codificaciones
        for enc in ['utf-8', 'latin-1', 'utf-8-sig']:
            try:
                df = pd.read_csv(BytesIO(content), encoding=enc)
                return df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
            except:
                continue
    except Exception as e:
        st.error(f"Error leyendo archivo: {e}")
    return []

def clear_temp_folder(folder="temp_output"):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

# ===== SIDEBAR (API KEYS Y PAÍSES) =====
st.sidebar.title("🔑 Configuración")
apollo_api = st.sidebar.text_input("Apollo API Key", type="password")
lusha_api = st.sidebar.text_input("Lusha API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.title("🌎 Países")
paises_dict = {
    "Norteamérica": ["United States", "Canada", "Mexico"],
    "Centroamérica": ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Nicaragua", "Panama"],
    "Suramérica": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"]
}

selected_countries = []
for region, countries in paises_dict.items():
    with st.sidebar.expander(f"📍 {region}"):
        for country in countries:
            if st.checkbox(country, key=f"c_{country}"):
                selected_countries.append(country)

# ===== ÁREA PRINCIPAL =====
st.markdown('<div class="main-header">🔍 Herramienta de Extracción de Datos v4.3</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Panel de Control", "ℹ️ Ayuda"])

with tab1:
    # SECCIÓN ARCHIVOS
    st.markdown('<div class="section-header">📁 1. Cargar Archivos</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        cargos_file = st.file_uploader("Cargos", type=['csv'])
        cargos_list = read_csv_list(cargos_file)
        if cargos_list:
            with st.expander(f"👀 Ver Cargos ({len(cargos_list)})"):
                st.write(cargos_list[:15])

    with col_f2:
        empresas_file = st.file_uploader("Empresas", type=['csv'])
        empresas_list = read_csv_list(empresas_file)
        if empresas_list:
            with st.expander(f"👀 Ver Empresas ({len(empresas_list)})"):
                st.write(empresas_list[:15])

    with col_f3:
        id_org_file = st.file_uploader("IDs Organizaciones", type=['csv'])
        ids_list = read_csv_list(id_org_file)
        if ids_list:
            with st.expander(f"👀 Ver IDs ({len(ids_list)})"):
                st.write(ids_list[:15])

    # CONSOLA EN TIEMPO REAL
    st.markdown('<div class="section-header">📋 2. Estado del Proceso</div>', unsafe_allow_header=True)
    console_placeholder = st.empty()
    if st.session_state.console_log:
        console_placeholder.code("\n".join(st.session_state.console_log[-15:]), language=None)
    else:
        console_placeholder.info("Esperando que inicies una tarea...")

    # BOTONES DE ACCIÓN
    st.markdown('<div class="section-header">🚀 3. Ejecutar</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    def run_process(script_module, name, *args):
        st.session_state.console_log = [] # Reiniciar consola
        st.session_state.output_files = [] # Limpiar descargas previas
        clear_temp_folder()
        
        def live_log(msg): log_message(msg, placeholder=console_placeholder)
        
        with st.spinner(f"Ejecutando {name}..."):
            try:
                # El script debe retornar la ruta del archivo generado
                res_path = script_module.run(*args, "temp_output", live_log, threading.Event())
                
                if res_path and os.path.exists(res_path) and os.path.getsize(res_path) > 60:
                    with open(res_path, 'r', encoding='utf-8-sig') as f:
                        st.session_state.output_files.append((os.path.basename(res_path), f.read()))
                    live_log(f"✅ {name} completado con éxito.")
                else:
                    live_log(f"⚠️ {name} finalizó sin encontrar registros nuevos.")
            except Exception as e:
                live_log(f"❌ Error crítico: {e}")
        st.rerun()

    with c1:
        if st.button("🟡 Apollo Contactos"):
            if apollo_api and cargos_list and empresas_list and selected_countries:
                run_process(apollo_script, "Apollo Contactos", apollo_api, empresas_list, cargos_list, selected_countries)
            else: st.error("Faltan datos (API, Archivos o Países)")

    with c2:
        if st.button("🟡 Apollo Org"):
            if apollo_api and ids_list:
                # Guardar temporalmente el archivo de IDs para el script de org
                tmp = "temp_ids.csv"; pd.DataFrame(ids_list).to_csv(tmp, index=False)
                run_process(apollo_org, "Apollo Organizaciones", apollo_api, tmp)
            else: st.error("Faltan API o IDs")

    with c3:
        if st.button("🟣 Lusha Contactos"):
            if lusha_api and cargos_list and empresas_list and selected_countries:
                run_process(lusha_script, "Lusha Contactos", lusha_api, empresas_list, cargos_list, selected_countries)
            else: st.error("Faltan datos")

    with c4:
        if st.button("🟣 Lusha Org"):
            if lusha_api and ids_list:
                tmp = "temp_ids_l.csv"; pd.DataFrame(ids_list).to_csv(tmp, index=False)
                run_process(lusha_org, "Lusha Organizaciones", lusha_api, tmp)
            else: st.error("Faltan datos")

    # DESCARGAS
    if st.session_state.output_files:
        st.markdown('<div class="section-header">💾 4. Descargar Resultados</div>', unsafe_allow_html=True)
        for filename, content in st.session_state.output_files:
            st.download_button(f"📥 Guardar {filename}", data=content, file_name=filename, mime="text/csv")
        
        if st.button("🗑️ Limpiar Todo"):
            st.session_state.output_files = []
            st.session_state.console_log = []
            st.rerun()

with tab2:
    st.markdown("### Guía rápida")
    st.write("1. Ingresa las API keys a la izquierda.")
    st.write("2. Selecciona al menos un país.")
    st.write("3. Sube tus CSV (puedes ver la vista previa para confirmar que se cargaron bien).")
    st.write("4. Presiona el botón del proceso que necesites.")
