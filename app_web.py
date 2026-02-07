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
    st.warning(f"Advertencia: Algunos módulos no se cargaron correctamente: {e}")

# ===== ESTILOS PERSONALIZADOS =====
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: bold; color: #1f77b4; text-align: center; padding: 1rem 0; }
    .section-header { font-size: 1.3rem; font-weight: bold; color: #ff7f0e; margin-top: 1.5rem; margin-bottom: 0.5rem; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; height: 3em; }
</style>
""", unsafe_allow_html=True)

# ===== INICIALIZACIÓN DE SESSION STATE =====
if 'console_log' not in st.session_state:
    st.session_state.console_log = []
if 'output_files' not in st.session_state:
    st.session_state.output_files = []

# ===== FUNCIONES AUXILIARES =====

def log_message(message, placeholder=None):
    """Agrega mensajes al log y actualiza el contenedor de consola en pantalla"""
    timestamp = time.strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {message}"
    st.session_state.console_log.append(full_msg)
    if placeholder:
        # Mostramos los últimos 15 mensajes para que sea legible y fluido
        placeholder.code("\n".join(st.session_state.console_log[-15:]), language=None)

def read_csv_list(uploaded_file):
    """Lee el CSV y extrae la primera columna con soporte para varias codificaciones"""
    if uploaded_file is None: return []
    try:
        content = uploaded_file.getvalue()
        for enc in ['utf-8', 'latin-1', 'utf-8-sig', 'cp1252']:
            try:
                df = pd.read_csv(BytesIO(content), encoding=enc)
                return df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
            except:
                continue
    except Exception as e:
        st.error(f"Error procesando el CSV: {e}")
    return []

def clear_temp_folder(folder="temp_output"):
    """Limpia archivos residuales en el servidor"""
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

# ===== BARRA LATERAL (SIDEBAR) =====
st.sidebar.title("🔑 Credenciales API")
apollo_api = st.sidebar.text_input("Apollo API Key", type="password")
lusha_api = st.sidebar.text_input("Lusha API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.title("🌎 Selección de Países")

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

# ===== PANEL PRINCIPAL =====
st.markdown('<div class="main-header">🔍 Extractor de Datos v4.3 (En Vivo)</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Ejecución", "📖 Instrucciones"])

with tab1:
    # 1. CARGA DE ARCHIVOS Y VISTA PREVIA
    st.markdown('<div class="section-header">📁 1. Cargar Archivos CSV</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        cargos_file = st.file_uploader("Archivo de Cargos", type=['csv'])
        cargos_list = read_csv_list(cargos_file)
        if cargos_list:
            with st.expander(f"👀 Ver Cargos ({len(cargos_list)})"):
                st.write(cargos_list[:15])

    with col_f2:
        empresas_file = st.file_uploader("Archivo de Empresas", type=['csv'])
        empresas_list = read_csv_list(empresas_file)
        if empresas_list:
            with st.expander(f"👀 Ver Empresas ({len(empresas_list)})"):
                st.write(empresas_list[:15])

    with col_f3:
        id_org_file = st.file_uploader("Archivo de IDs (Org)", type=['csv'])
        ids_list = read_csv_list(id_org_file)
        if ids_list:
            with st.expander(f"👀 Ver IDs ({len(ids_list)})"):
                st.write(ids_list[:15])

    # 2. CONSOLA DE ESTADO EN TIEMPO REAL
    st.markdown('<div class="section-header">📋 2. Estado del Proceso (Consola)</div>', unsafe_allow_html=True)
    console_placeholder = st.empty() # Contenedor dinámico
    
    if st.session_state.console_log:
        console_placeholder.code("\n".join(st.session_state.console_log[-15:]), language=None)
    else:
        console_placeholder.info("La consola se activará al iniciar un proceso.")

    # 3. BOTONES DE ACCIÓN
    st.markdown('<div class="section-header">🚀 3. Ejecutar Extracción</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    def run_generic_process(module, name, *args):
        """Función base para ejecutar cualquier script y capturar el log en vivo"""
        st.session_state.console_log = [] 
        st.session_state.output_files = [] 
        clear_temp_folder()
        
        # Callback que el script llamará para pintar en la web
        def live_callback(msg): 
            log_message(msg, placeholder=console_placeholder)
        
        with st.spinner(f"Procesando {name}..."):
            try:
                # Se asume que cada script tiene una función .run()
                res_path = module.run(*args, "temp_output", live_callback, threading.Event())
                
                if res_path and os.path.exists(res_path) and os.path.getsize(res_path) > 60:
                    with open(res_path, 'r', encoding='utf-8-sig') as f:
                        st.session_state.output_files.append((os.path.basename(res_path), f.read()))
                    live_callback(f"✅ {name} finalizado con éxito.")
                else:
                    live_callback(f"⚠️ {name} terminó, pero no se generaron registros nuevos.")
            except Exception as e:
                live_callback(f"❌ Error crítico: {e}")
        
        time.sleep(1) # Pausa visual
        st.rerun()

    with c1:
        if st.button("🟡 Apollo Contactos"):
            if apollo_api and cargos_list and empresas_list and selected_countries:
                run_generic_process(apollo_script, "Apollo Contactos", apollo_api, empresas_list, cargos_list, selected_countries)
            else: st.error("Faltan datos en Apollo o Selección")

    with c2:
        if st.button("🟡 Apollo Org"):
            if apollo_api and ids_list:
                tmp = "temp_ids.csv"
                pd.DataFrame(ids_list).to_csv(tmp, index=False)
                run_generic_process(apollo_org, "Apollo Organizaciones", apollo_api, tmp)
            else: st.error("Falta API o archivo de IDs")

    with c3:
        if st.button("🟣 Lusha Contactos"):
            if lusha_api and cargos_list and empresas_list and selected_countries:
                run_generic_process(lusha_script, "Lusha Contactos", lusha_api, empresas_list, cargos_list, selected_countries)
            else: st.error("Faltan datos de Lusha")

    with c4:
        if st.button("🟣 Lusha Org"):
            if lusha_api and ids_list:
                tmp = "temp_ids_l.csv"
                pd.DataFrame(ids_list).to_csv(tmp, index=False)
                run_generic_process(lusha_org, "Lusha Organizaciones", lusha_api, tmp)
            else: st.error("Faltan datos")

    # 4. DESCARGA DE RESULTADOS
    if st.session_state.output_files:
        st.markdown('<div class="section-header">💾 4. Descargar Resultados</div>', unsafe_allow_html=True)
        d_col1, d_col2 = st.columns(2)
        
        with d_col1:
            for filename, content in st.session_state.output_files:
                st.download_button(f"📥 Descargar {filename}", data=content, file_name=filename, mime="text/csv")
        
        with d_col2:
            if st.button("🗑️ Limpiar Resultados"):
                st.session_state.output_files = []
                st.session_state.console_log = []
                st.rerun()

with tab2:
    st.markdown("""
    ### 📖 Guía de uso
    1. **Credenciales:** Ingresa tus llaves de Apollo/Lusha en la barra lateral.
    2. **Países:** Selecciona al menos uno para filtrar la búsqueda.
    3. **Archivos:** Sube archivos CSV donde la primera columna contenga los datos (Cargos o Empresas).
    4. **Consola:** Observa el progreso en tiempo real; verás cuántos contactos se encuentran por lote.
    5. **Descarga:** Los botones aparecerán solo si se encuentran registros reales.
    """)
