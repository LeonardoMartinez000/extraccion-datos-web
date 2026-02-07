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

# Importar los scripts de extracción
apollo_script = None
apollo_org = None
lusha_script = None
lusha_org = None

try:
    import apollo_script
except ImportError:
    pass

try:
    import apollo_org
except ImportError:
    pass

try:
    import lusha_script
except ImportError:
    pass

try:
    import lusha_org
except ImportError:
    pass

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(
    page_title="Herramienta de Extracción de Datos",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ESTILOS PERSONALIZADOS =====
st.markdown("""
<style>
    .main-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ===== INICIALIZACIÓN DE SESSION STATE =====
if 'console_log' not in st.session_state:
    st.session_state.console_log = []
if 'stop_event' not in st.session_state:
    st.session_state.stop_event = threading.Event()
if 'process_running' not in st.session_state:
    st.session_state.process_running = False
if 'output_files' not in st.session_state:
    st.session_state.output_files = []
if 'file_hashes' not in st.session_state:
    st.session_state.file_hashes = {}
if 'cached_data' not in st.session_state:
    st.session_state.cached_data = {}

# ===== FUNCIONES AUXILIARES =====

def log_message(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.console_log.append(f"[{timestamp}] {message}")

def clear_log():
    st.session_state.console_log = []

def clear_temp_folder(folder="temp_output"):
    """Limpia la carpeta temporal para evitar archivos residuales"""
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

def get_file_hash(uploaded_file):
    if uploaded_file is None:
        return None
    file_content = uploaded_file.getvalue()
    file_hash = hashlib.md5(
        f"{uploaded_file.name}_{uploaded_file.size}_{file_content[:100]}".encode()
    ).hexdigest()
    return file_hash

def read_csv_list(uploaded_file, cache_key=None):
    if uploaded_file is None:
        return []
    
    file_hash = get_file_hash(uploaded_file)
    
    if cache_key and file_hash:
        cache_full_key = f"{cache_key}_{file_hash}"
        if cache_key in st.session_state.file_hashes:
            old_hash = st.session_state.file_hashes[cache_key]
            if old_hash != file_hash:
                if cache_full_key in st.session_state.cached_data:
                    del st.session_state.cached_data[cache_full_key]
        st.session_state.file_hashes[cache_key] = file_hash
        if cache_full_key in st.session_state.cached_data:
            return st.session_state.cached_data[cache_full_key]

    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1']
    for encoding in encodings:
        try:
            stringio = StringIO(uploaded_file.getvalue().decode(encoding))
            reader = csv.reader(stringio)
            header = next(reader, None)
            result = [row[0].strip() for row in reader if row and row[0].strip()]
            if result:
                if cache_key and file_hash:
                    st.session_state.cached_data[f"{cache_key}_{file_hash}"] = result
                return result
        except:
            continue
    return []

def create_download_zip(files_dict):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files_dict.items():
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

def run_extraction(process_type, api_key, params):
    try:
        output_folder = "temp_output"
        clear_temp_folder(output_folder) # Limpiar antes de cada ejecución real
        
        if process_type == "apollo_contact":
            if apollo_script is None: return None
            empresas, cargos, paises = params
            apollo_script.run(api_key, empresas, cargos, paises, output_folder, log_message, st.session_state.stop_event)
            return os.path.join(output_folder, "resultados_apollo.csv")
        
        elif process_type == "apollo_org":
            if apollo_org is None: return None
            temp_csv = params
            apollo_org.run(api_key, temp_csv, output_folder, log_message, st.session_state.stop_event)
            return os.path.join(output_folder, "apollo_organizations_output.csv")
        
        elif process_type == "lusha_contact":
            if lusha_script is None: return None
            empresas, cargos, paises = params
            lusha_script.run(api_key, empresas, cargos, paises, output_folder, log_message, st.session_state.stop_event)
            return os.path.join(output_folder, "resultados_lusha.csv")
        
        elif process_type == "lusha_org":
            if lusha_org is None: return None
            temp_csv = params
            lusha_org.run(api_key, temp_csv, output_folder, log_message, st.session_state.stop_event)
            return os.path.join(output_folder, "lusha_organizations_output.csv")
    except Exception as e:
        log_message(f"❌ Error: {e}")
        return None

# ===== INTERFAZ PRINCIPAL =====

st.markdown('<div class="main-header">🔍 Herramienta de Extracción de Datos v4.2 Web</div>', unsafe_allow_html=True)

# SIDEBAR
st.sidebar.markdown("### 🔑 API Keys")
apollo_api = st.sidebar.text_input("Apollo API Key", type="password", key="apollo_api")
lusha_api = st.sidebar.text_input("Lusha API Key", type="password", key="lusha_api")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌎 Países")
paises_dict = {
    "Norteamérica": ["United States", "Canada", "Mexico"],
    "Centroamérica": ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Nicaragua", "Panama"],
    "Suramérica": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"]
}

selected_countries = []
for region, countries in paises_dict.items():
    with st.sidebar.expander(f"📍 {region}"):
        for country in countries:
            if st.checkbox(country, key=f"country_{country}"):
                selected_countries.append(country)

# ÁREA PRINCIPAL
tab1, tab2 = st.tabs(["📊 Extracción de Contactos", "ℹ️ Instrucciones"])

with tab1:
    st.markdown('<div class="section-header">📁 Archivos de Entrada</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cargos_file = st.file_uploader("CSV de Cargos", type=['csv'], key="cargos")
    with col2:
        empresas_file = st.file_uploader("CSV de Empresas", type=['csv'], key="empresas")
    with col3:
        id_org_file = st.file_uploader("CSV de IDs Organizaciones", type=['csv'], key="id_org")

    st.markdown('<div class="section-header">🚀 Ejecutar Extracción</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    # Lógica unificada para procesar resultados y evitar persistencia errónea
    def process_and_save(output_path, filename):
        if output_path and os.path.exists(output_path):
            # Verificar si el archivo tiene más que solo el header (ej. > 50 bytes)
            if os.path.getsize(output_path) > 60:
                with open(output_path, 'r', encoding='utf-8') as f:
                    st.session_state.output_files.append((filename, f.read()))
                log_message(f"✅ Proceso completado. {filename} listo.")
            else:
                log_message("⚠️ El proceso terminó pero no se encontraron registros válidos.")
        else:
            log_message("❌ No se pudo generar el archivo de resultados.")
        st.rerun()

    with c1:
        if st.button("🟡 Apollo Contactos", disabled=st.session_state.process_running):
            if apollo_api and cargos_file and empresas_file and selected_countries:
                with st.spinner('Procesando...'):
                    st.session_state.output_files = [] # LIMPIEZA CLAVE
                    clear_log()
                    empresas = read_csv_list(empresas_file, "empresas")
                    cargos = read_csv_list(cargos_file, "cargos")
                    output = run_extraction("apollo_contact", apollo_api, (empresas, cargos, selected_countries))
                    process_and_save(output, "resultados_apollo.csv")
            else:
                st.error("⚠️ Datos incompletos")

    with c2:
        if st.button("🟡 Apollo Org", disabled=st.session_state.process_running):
            if apollo_api and id_org_file:
                with st.spinner('Procesando...'):
                    st.session_state.output_files = [] # LIMPIEZA CLAVE
                    clear_log()
                    temp_csv = "temp_ids.csv"
                    with open(temp_csv, 'wb') as f: f.write(id_org_file.getvalue())
                    output = run_extraction("apollo_org", apollo_api, temp_csv)
                    if os.path.exists(temp_csv): os.remove(temp_csv)
                    process_and_save(output, "apollo_organizations.csv")

    with c3:
        if st.button("🟣 Lusha Contactos", disabled=st.session_state.process_running):
            if lusha_api and cargos_file and empresas_file and selected_countries:
                with st.spinner('Procesando...'):
                    st.session_state.output_files = [] # LIMPIEZA CLAVE
                    clear_log()
                    empresas = read_csv_list(empresas_file, "empresas")
                    cargos = read_csv_list(cargos_file, "cargos")
                    output = run_extraction("lusha_contact", lusha_api, (empresas, cargos, selected_countries))
                    process_and_save(output, "resultados_lusha.csv")

    with c4:
        if st.button("🟣 Lusha Org", disabled=st.session_state.process_running):
            if lusha_api and id_org_file:
                with st.spinner('Procesando...'):
                    st.session_state.output_files = [] # LIMPIEZA CLAVE
                    clear_log()
                    temp_csv = "temp_ids_lusha.csv"
                    with open(temp_csv, 'wb') as f: f.write(id_org_file.getvalue())
                    output = run_extraction("lusha_org", lusha_api, temp_csv)
                    if os.path.exists(temp_csv): os.remove(temp_csv)
                    process_and_save(output, "lusha_organizations.csv")

    st.markdown('<div class="section-header">📋 Consola de Ejecución</div>', unsafe_allow_html=True)
    if st.session_state.console_log:
        st.code("\n".join(st.session_state.console_log[-50:]), language=None)
    
    if st.session_state.output_files:
        st.markdown('<div class="section-header">💾 Descargar Resultados</div>', unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            for filename, content in st.session_state.output_files:
                st.download_button(f"📥 Descargar {filename}", data=content, file_name=filename, mime="text/csv")
        with col_dl2:
            if len(st.session_state.output_files) > 1:
                zip_data = create_download_zip({f: c for f, c in st.session_state.output_files})
                st.download_button("📦 Descargar Todos (ZIP)", data=zip_data, file_name="resultados.zip", mime="application/zip")
        if st.button("🗑️ Limpiar Todo"):
            st.session_state.output_files = []
            clear_log()
            st.rerun()

with tab2:
    st.info("Esta versión limpia automáticamente los resultados previos antes de cada búsqueda para evitar confusiones entre empresas.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Extracción de Datos v4.2 | Fix: Session Data Persistence</div>", unsafe_allow_html=True)
