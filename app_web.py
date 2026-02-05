import streamlit as st
import pandas as pd
import os
import csv
import threading
import time
from io import StringIO, BytesIO
import zipfile

# --- IMPORTACIÓN DE SCRIPTS (Manejo de errores) ---
apollo_script = apollo_org = lusha_script = lusha_org = None
try: import apollo_script
except ImportError: pass
try: import apollo_org
except ImportError: pass
try: import lusha_script
except ImportError: pass
try: import lusha_org
except ImportError: pass

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(
    page_title="Extractor v4.0",
    page_icon="🔍",
    layout="wide"
)

# ===== ESTILOS CSS PARA COMPACTAR Y AJUSTAR BOTONES =====
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .main-header {font-size: 1.8rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 1rem;}
    .section-header {font-size: 1.1rem; font-weight: bold; color: #ff7f0e; margin-bottom: 0.8rem; border-bottom: 1px solid #eee;}
    
    /* Botones: Texto completo y sin cortes */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: auto;
        min-height: 2.8rem;
        font-weight: bold;
        font-size: 0.9rem;
        white-space: normal;
        word-wrap: break-word;
        padding: 5px;
    }
    
    /* Ajuste de la consola para que no crezca demasiado */
    .stCodeBlock { height: 400px; overflow-y: auto; }
    
    /* Compactar inputs */
    div[data-testid="stExpander"] { margin-bottom: 0.1rem; }
</style>
""", unsafe_allow_html=True)

# ===== INICIALIZACIÓN DE ESTADO =====
if 'console_log' not in st.session_state: st.session_state.console_log = []
if 'stop_event' not in st.session_state: st.session_state.stop_event = threading.Event()
if 'process_running' not in st.session_state: st.session_state.process_running = False
if 'output_files' not in st.session_state: st.session_state.output_files = []

def log_message(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.console_log.append(f"[{timestamp}] {message}")

def clear_log(): st.session_state.console_log = []

# ===== CUERPO PRINCIPAL (Layout 3 Columnas) =====
st.markdown('<div class="main-header">🔍 Herramienta de Extracción de Datos v4.0</div>', unsafe_allow_html=True)

col_config, col_action, col_console = st.columns([1, 1.2, 1])

# --- COLUMNA 1: CONFIGURACIÓN (IZQUIERDA) ---
with col_config:
    st.markdown('<div class="section-header">🔑 Configuración API</div>', unsafe_allow_html=True)
    apollo_api = st.text_input("Apollo API Key", type="password")
    lusha_api = st.text_input("Lusha API Key", type="password")
    
    st.markdown('<div class="section-header">🌎 Selección de Países</div>', unsafe_allow_html=True)
    paises_dict = {
        "Norteamérica": ["United States", "Canada", "Mexico"],
        "Centroamérica": ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Panama"],
        "Suramérica": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Peru", "Uruguay", "Venezuela"]
    }
    
    selected_countries = []
    for region, countries in paises_dict.items():
        with st.expander(f"📍 {region}", expanded=False):
            for country in countries:
                if st.checkbox(country, key=f"web_{country}"):
                    selected_countries.append(country)
    st.caption(f"Seleccionados: {len(selected_countries)}")

# --- COLUMNA 2: ARCHIVOS Y ACCIONES (CENTRO) ---
with col_action:
    st.markdown('<div class="section-header">📁 Carga de Datos</div>', unsafe_allow_html=True)
    c_file = st.file_uploader("Cargos (CSV)", type=['csv'])
    e_file = st.file_uploader("Empresas (CSV)", type=['csv'])
    i_file = st.file_uploader("ID Organizaciones (CSV)", type=['csv'])
    
    st.markdown('<div class="section-header">🚀 Acciones</div>', unsafe_allow_html=True)
    
    # Grid de botones en la parte inferior de la columna central
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🟡 Apollo Contactos"):
            # Lógica de ejecución Apollo Contactos
            pass
        if st.button("🟣 Lusha Contactos"):
            # Lógica de ejecución Lusha Contactos
            pass
            
    with btn_col2:
        if st.button("🟡 Apollo Organizaciones"):
            # Lógica de ejecución Apollo Org
            pass
        if st.button("🟣 Lusha Organizaciones"):
            # Lógica de ejecución Lusha Org
            pass

# --- COLUMNA 3: CONSOLA Y DESCARGAS (DERECHA) ---
with col_console:
    st.markdown('<div class="section-header">📋 Consola de Procesos</div>', unsafe_allow_html=True)
    if st.session_state.console_log:
        # Mostramos los últimos 15 mensajes para que la consola sea útil pero compacta
        console_text = "\n".join(st.session_state.console_log[-15:])
        st.code(console_text, language=None)
    else:
        st.info("Esperando inicio de proceso...")
    
    if st.session_state.output_files:
        st.markdown('<div class="section-header">💾 Resultados</div>', unsafe_allow_html=True)
        for filename, content in st.session_state.output_files:
            st.download_button(label=f"📥 {filename}", data=content, file_name=filename, mime="text/csv")
        
        if st.button("🗑️ Limpiar Todo"):
            st.session_state.output_files = []
            st.session_state.console_log = []
            st.rerun()

# ===== FOOTER =====
st.markdown("---")
st.caption("v4.0 Cloud Edition | Basado en lógica de escritorio optimizada para Web")
