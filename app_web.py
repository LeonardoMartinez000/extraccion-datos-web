import streamlit as st
import pandas as pd
import os
import csv
import threading
import time
from io import StringIO, BytesIO
import zipfile

# Importar los scripts de extracción (manejo de errores)
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
        font-size: 2.5rem;
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

# ===== FUNCIONES AUXILIARES =====

def log_message(message):
    """Agregar mensaje al log de consola"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.console_log.append(f"[{timestamp}] {message}")

def clear_log():
    """Limpiar el log de consola"""
    st.session_state.console_log = []

def read_csv_list(uploaded_file):
    """Leer archivo CSV y retornar lista de valores de la primera columna"""
    if uploaded_file is None:
        return []
    
    # Intentar diferentes codificaciones comunes
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'windows-1252', 'cp1252']
    
    for encoding in encodings:
        try:
            stringio = StringIO(uploaded_file.getvalue().decode(encoding))
            reader = csv.reader(stringio)
            next(reader)  # Saltar encabezado
            result = [row[0].strip() for row in reader if row and row[0].strip()]
            
            if result:  # Si se leyó algo exitosamente
                log_message(f"✅ Archivo CSV leído correctamente (codificación: {encoding})")
                return result
        except (UnicodeDecodeError, UnicodeError):
            continue  # Intentar con la siguiente codificación
        except Exception as e:
            log_message(f"⚠️ Error al leer CSV con {encoding}: {e}")
            continue
    
    log_message(f"❌ No se pudo leer el archivo CSV con ninguna codificación estándar")
    return []

def create_download_zip(files_dict):
    """Crear un ZIP con múltiples archivos"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files_dict.items():
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

def run_extraction(process_type, api_key, params):
    """Ejecutar proceso de extracción"""
    try:
        output_folder = "temp_output"
        os.makedirs(output_folder, exist_ok=True)
        
        if process_type == "apollo_contact":
            if apollo_script is None:
                log_message("❌ ERROR: apollo_script.py no está disponible")
                return None
            
            empresas, cargos, paises = params
            apollo_script.run(api_key, empresas, cargos, paises, output_folder, log_message, st.session_state.stop_event)
            return os.path.join(output_folder, "resultados_apollo.csv")
        
        elif process_type == "apollo_org":
            if apollo_org is None:
                log_message("❌ ERROR: apollo_org.py no está disponible")
                return None
            
            temp_csv = params
            apollo_org.run(api_key, temp_csv, output_folder, log_message, st.session_state.stop_event)
            return os.path.join(output_folder, "apollo_organizations_output.csv")
        
        elif process_type == "lusha_contact":
            if lusha_script is None:
                log_message("❌ ERROR: lusha_script.py no está disponible")
                return None
            
            empresas, cargos, paises = params
            lusha_script.run(api_key, empresas, cargos, paises, output_folder, log_message, st.session_state.stop_event)
            return os.path.join(output_folder, "resultados_lusha.csv")
        
        elif process_type == "lusha_org":
            if lusha_org is None:
                log_message("❌ ERROR: lusha_org.py no está disponible")
                return None
            
            temp_csv = params
            lusha_org.run(api_key, temp_csv, output_folder, log_message, st.session_state.stop_event)
            return os.path.join(output_folder, "lusha_organizations_output.csv")
        
    except Exception as e:
        log_message(f"❌ Error: {e}")
        return None

# ===== INTERFAZ PRINCIPAL =====

st.markdown('<div class="main-header">🔍 Herramienta de Extracción de Datos v4.0 Web</div>', unsafe_allow_html=True)

# ===== SIDEBAR - API KEYS =====
st.sidebar.markdown("### 🔑 API Keys")
apollo_api = st.sidebar.text_input("Apollo API Key", type="password", key="apollo_api")
lusha_api = st.sidebar.text_input("Lusha API Key", type="password", key="lusha_api")

st.sidebar.markdown("---")

# ===== SIDEBAR - SELECCIÓN DE PAÍSES =====
st.sidebar.markdown("### 🌎 Países")

paises_dict = {
    "Norteamérica": ["United States", "Canada", "Mexico"],
    "Centroamérica": ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Nicaragua", "Panama"],
    "Suramérica": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", 
                   "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"]
}

selected_countries = []
for region, countries in paises_dict.items():
    with st.sidebar.expander(f"📍 {region}"):
        for country in countries:
            if st.checkbox(country, key=f"country_{country}"):
                selected_countries.append(country)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Países seleccionados:** {len(selected_countries)}")

# ===== ÁREA PRINCIPAL =====

# Tabs para organizar funcionalidad
tab1, tab2 = st.tabs(["📊 Extracción de Contactos", "ℹ️ Instrucciones"])

with tab1:
    # ===== SECCIÓN DE ARCHIVOS =====
    st.markdown('<div class="section-header">📁 Archivos de Entrada</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cargos_file = st.file_uploader("CSV de Cargos", type=['csv'], key="cargos")
        if cargos_file:
            preview_cargos = read_csv_list(cargos_file)
            if preview_cargos:
                with st.expander(f"👀 Ver cargos ({len(preview_cargos)} encontrados)"):
                    st.write(preview_cargos[:10])
                    if len(preview_cargos) > 10:
                        st.caption(f"... y {len(preview_cargos) - 10} más")
    
    with col2:
        empresas_file = st.file_uploader("CSV de Empresas", type=['csv'], key="empresas")
        if empresas_file:
            preview_empresas = read_csv_list(empresas_file)
            if preview_empresas:
                with st.expander(f"👀 Ver empresas ({len(preview_empresas)} encontradas)"):
                    st.write(preview_empresas[:10])
                    if len(preview_empresas) > 10:
                        st.caption(f"... y {len(preview_empresas) - 10} más")
    
    with col3:
        id_org_file = st.file_uploader("CSV de IDs Organizaciones", type=['csv'], key="id_org")
        if id_org_file:
            preview_ids = read_csv_list(id_org_file)
            if preview_ids:
                with st.expander(f"👀 Ver IDs ({len(preview_ids)} encontrados)"):
                    st.write(preview_ids[:10])
                    if len(preview_ids) > 10:
                        st.caption(f"... y {len(preview_ids) - 10} más")
    
    # ===== SECCIÓN DE ACCIONES =====
    st.markdown('<div class="section-header">🚀 Ejecutar Extracción</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🟡 Apollo Contactos", disabled=st.session_state.process_running):
            if apollo_api and cargos_file and empresas_file and selected_countries:
                with st.spinner('Procesando...'):
                    clear_log()
                    log_message("🚀 Iniciando Apollo Contactos...")
                    
                    empresas = read_csv_list(empresas_file)
                    cargos = read_csv_list(cargos_file)
                    
                    # Validación adicional
                    if not empresas:
                        log_message("❌ ERROR: El archivo de empresas está vacío o no se pudo leer")
                        log_message("💡 Verifica que:")
                        log_message("   - El archivo tenga al menos una empresa después del encabezado")
                        log_message("   - El formato sea: empresa (en la primera fila) seguido de los nombres")
                        st.error("El archivo de empresas está vacío o tiene un formato incorrecto")
                        st.stop()
                    
                    if not cargos:
                        log_message("❌ ERROR: El archivo de cargos está vacío o no se pudo leer")
                        log_message("💡 Verifica que:")
                        log_message("   - El archivo tenga al menos un cargo después del encabezado")
                        log_message("   - El formato sea: cargo (en la primera fila) seguido de los títulos")
                        st.error("El archivo de cargos está vacío o tiene un formato incorrecto")
                        st.stop()
                    
                    log_message(f"📊 Datos cargados: {len(empresas)} empresas, {len(cargos)} cargos, {len(selected_countries)} países")
                    
                    output_file = run_extraction("apollo_contact", apollo_api, (empresas, cargos, selected_countries))
                    
                    if output_file and os.path.exists(output_file):
                        with open(output_file, 'r', encoding='utf-8') as f:
                            st.session_state.output_files.append(("resultados_apollo.csv", f.read()))
                        log_message("✅ Proceso completado. Archivo disponible para descarga.")
                        st.rerun()
            else:
                st.error("⚠️ Faltan datos: API Key Apollo, archivos CSV y países")
    
    with col2:
        if st.button("🟡 Apollo Organizaciones", disabled=st.session_state.process_running):
            if apollo_api and id_org_file:
                with st.spinner('Procesando...'):
                    clear_log()
                    log_message("🚀 Iniciando Apollo Organizaciones...")
                    
                    temp_csv = "temp_ids.csv"
                    with open(temp_csv, 'wb') as f:
                        f.write(id_org_file.getvalue())
                    
                    output_file = run_extraction("apollo_org", apollo_api, temp_csv)
                    
                    if output_file and os.path.exists(output_file):
                        with open(output_file, 'r', encoding='utf-8') as f:
                            st.session_state.output_files.append(("apollo_organizations_output.csv", f.read()))
                        log_message("✅ Proceso completado. Archivo disponible para descarga.")
                        st.rerun()
                    
                    if os.path.exists(temp_csv):
                        os.remove(temp_csv)
            else:
                st.error("⚠️ Faltan datos: API Key Apollo y archivo de IDs")
    
    with col3:
        if st.button("🟣 Lusha Contactos", disabled=st.session_state.process_running):
            if lusha_api and cargos_file and empresas_file and selected_countries:
                with st.spinner('Procesando...'):
                    clear_log()
                    log_message("🚀 Iniciando Lusha Contactos...")
                    
                    empresas = read_csv_list(empresas_file)
                    cargos = read_csv_list(cargos_file)
                    
                    # Validación adicional
                    if not empresas:
                        log_message("❌ ERROR: El archivo de empresas está vacío o no se pudo leer")
                        st.error("El archivo de empresas está vacío o tiene un formato incorrecto")
                        st.stop()
                    
                    if not cargos:
                        log_message("❌ ERROR: El archivo de cargos está vacío o no se pudo leer")
                        st.error("El archivo de cargos está vacío o tiene un formato incorrecto")
                        st.stop()
                    
                    log_message(f"📊 Datos cargados: {len(empresas)} empresas, {len(cargos)} cargos, {len(selected_countries)} países")
                    
                    output_file = run_extraction("lusha_contact", lusha_api, (empresas, cargos, selected_countries))
                    
                    if output_file and os.path.exists(output_file):
                        with open(output_file, 'r', encoding='utf-8') as f:
                            st.session_state.output_files.append(("resultados_lusha.csv", f.read()))
                        log_message("✅ Proceso completado. Archivo disponible para descarga.")
                        st.rerun()
            else:
                st.error("⚠️ Faltan datos: API Key Lusha, archivos CSV y países")
    
    with col4:
        if st.button("🟣 Lusha Organizaciones", disabled=st.session_state.process_running):
            if lusha_api and id_org_file:
                with st.spinner('Procesando...'):
                    clear_log()
                    log_message("🚀 Iniciando Lusha Organizaciones...")
                    
                    temp_csv = "temp_ids.csv"
                    with open(temp_csv, 'wb') as f:
                        f.write(id_org_file.getvalue())
                    
                    output_file = run_extraction("lusha_org", lusha_api, temp_csv)
                    
                    if output_file and os.path.exists(output_file):
                        with open(output_file, 'r', encoding='utf-8') as f:
                            st.session_state.output_files.append(("lusha_organizations_output.csv", f.read()))
                        log_message("✅ Proceso completado. Archivo disponible para descarga.")
                        st.rerun()
                    
                    if os.path.exists(temp_csv):
                        os.remove(temp_csv)
            else:
                st.error("⚠️ Faltan datos: API Key Lusha y archivo de IDs")
    
    # ===== CONSOLA DE LOG =====
    st.markdown('<div class="section-header">📋 Consola de Ejecución</div>', unsafe_allow_html=True)
    
    if st.session_state.console_log:
        console_text = "\n".join(st.session_state.console_log[-50:])
        st.code(console_text, language=None)
    else:
        st.info("👋 La consola mostrará el progreso de la extracción cuando inicies un proceso.")
    
    # ===== DESCARGA DE RESULTADOS =====
    if st.session_state.output_files:
        st.markdown('<div class="section-header">💾 Descargar Resultados</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            for filename, content in st.session_state.output_files:
                st.download_button(
                    label=f"📥 Descargar {filename}",
                    data=content,
                    file_name=filename,
                    mime="text/csv"
                )
        
        with col2:
            if len(st.session_state.output_files) > 1:
                files_dict = {filename: content for filename, content in st.session_state.output_files}
                zip_buffer = create_download_zip(files_dict)
                
                st.download_button(
                    label="📦 Descargar Todos (ZIP)",
                    data=zip_buffer,
                    file_name="resultados_completos.zip",
                    mime="application/zip"
                )
        
        if st.button("🗑️ Limpiar Resultados"):
            st.session_state.output_files = []
            clear_log()
            st.rerun()

with tab2:
    st.markdown("""
    ## 📖 Instrucciones de Uso
    
    ### 1️⃣ Configurar API Keys
    En la barra lateral izquierda, ingresa tus API Keys para:
    - **Apollo**: Para búsquedas de contactos y organizaciones
    - **Lusha**: Para búsquedas de contactos y organizaciones
    
    ### 2️⃣ Seleccionar Países
    Marca los países donde deseas buscar contactos.
    
    ### 3️⃣ Cargar Archivos CSV
    - **CSV de Cargos**: Lista de títulos de trabajo a buscar (una columna)
    - **CSV de Empresas**: Lista de nombres de empresas (una columna)
    - **CSV de IDs Organizaciones**: IDs de organizaciones para búsqueda directa
    
    ### 4️⃣ Ejecutar Búsqueda
    Haz clic en el botón correspondiente según lo que necesites:
    - **Apollo/Lusha Contactos**: Requiere archivos de cargos, empresas y países
    - **Apollo/Lusha Organizaciones**: Requiere archivo de IDs de organizaciones
    
    ### 5️⃣ Descargar Resultados
    Una vez completado el proceso, descarga los archivos CSV generados.
    
    ---
    
    ### 🔧 Formato de Archivos CSV
    
    **Cargos CSV:**
    ```
    cargo
    CEO
    CTO
    Director
    ```
    
    **Empresas CSV:**
    ```
    empresa
    Google
    Microsoft
    Amazon
    ```
    
    **IDs Organizaciones CSV:**
    ```
    organization_id
    123456
    789012
    345678
    ```
    
    ---
    
    ### ⚠️ Notas Importantes
    - Los procesos pueden tardar varios minutos dependiendo del volumen de datos
    - Los archivos se generan y están disponibles para descarga inmediatamente
    - Esta aplicación no almacena tus datos ni API keys permanentemente
    """)

# ===== FOOTER =====
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Herramienta de Extracción de Datos v4.0 Web | Desarrollado con Streamlit</p>
</div>
""", unsafe_allow_html=True)
