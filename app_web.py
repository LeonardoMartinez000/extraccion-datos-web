import streamlit as st
import pandas as pd
import os
import csv
import threading
import time
from io import StringIO, BytesIO
import zipfile

# [Mantener los mismos imports de scripts que ya tienes]
apollo_script = None
apollo_org = None
lusha_script = None
lusha_org = None
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
    page_title="Extractor de Datos v4.0",
    page_icon="🔍",
    layout="wide"
)

# ===== CSS AJUSTADO PARA BOTONES Y TÍTULOS =====
st.markdown("""
<style>
    /* Ajuste del Título Principal */
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        white-space: nowrap;
    }
    /* Estilo de Secciones */
    .section-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-bottom: 0.5rem;
    }
    /* Botones: Asegurar que el texto sea visible y completo */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: auto;
        padding: 10px 5px;
        font-weight: bold;
        font-size: 0.95rem;
        white-space: normal; /* Permite que el texto baje de línea si es muy largo en vez de cortarse */
        word-wrap: break-word;
    }
    /* Reducción de márgenes generales */
    .block-container {padding-top: 1.5rem;}
</style>
""", unsafe_allow_html=True)

# [Mantenemos la lógica de Session State igual para no afectar funcionalidad]
if 'console_log' not in st.session_state: st.session_state.console_log = []
if 'stop_event' not in st.session_state: st.session_state.stop_event = threading.Event()
if 'process_running' not in st.session_state: st.session_state.process_running = False
if 'output_files' not in st.session_state: st.session_state.output_files = []

def log_message(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.console_log.append(f"[{timestamp}] {message}")

# ===== SIDEBAR =====
st.sidebar.title("🔑 Configuración")
apollo_api = st.sidebar.text_input("Apollo API Key", type="password")
lusha_api = st.sidebar.text_input("Lusha API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("🌎 Países")
# [Aquí va tu lógica de checkboxes de países]
selected_countries = [] # ... lógica de países

# ===== ÁREA PRINCIPAL =====
st.markdown('<div class="main-header">🔍 Herramienta de Extracción de Datos</div>', unsafe_allow_html=True)

# Layout de dos grandes bloques
col_files, col_actions = st.columns([1, 1.2])

with col_files:
    st.markdown('<div class="section-header">📁 Carga de Archivos CSV</div>', unsafe_allow_html=True)
    c_file = st.file_uploader("Cargos", type=['csv'])
    e_file = st.file_uploader("Empresas", type=['csv'])
    i_file = st.file_uploader("IDs Organizaciones", type=['csv'])

with col_actions:
    st.markdown('<div class="section-header">🚀 Acciones de Extracción</div>', unsafe_allow_html=True)
    
    # Grid de botones más espacioso para que quepan los nombres
    btn_row1_col1, btn_row1_col2 = st.columns(2)
    with btn_row1_col1:
        if st.button("🟡 Apollo Contactos"):
            # Lógica de Apollo Contactos
            pass
        if st.button("🟣 Lusha Contactos"):
            # Lógica de Lusha Contactos
            pass

    with btn_row1_col2:
        if st.button("🟡 Apollo Organizaciones"):
            # Lógica de Apollo Org
            pass
        if st.button("🟣 Lusha Organizaciones"):
            # Lógica de Lusha Org
            pass

# ===== CONSOLA Y DESCARGAS EN LA PARTE INFERIOR =====
st.markdown("---")
col_log, col_dl = st.columns([1.5, 1])

with col_log:
    st.markdown('<div class="section-header">📋 Consola de Progreso</div>', unsafe_allow_html=True)
    if st.session_state.console_log:
        console_text = "\n".join(st.session_state.console_log[-10:])
        st.code(console_text, language=None)
    else:
        st.info("Esperando inicio de proceso...")

with col_dl:
    if st.session_state.output_files:
        st.markdown('<div class="section-header">💾 Descargar Resultados</div>', unsafe_allow_html=True)
        for filename, content in st.session_state.output_files:
            st.download_button(label=f"📥 Descargar {filename}", data=content, file_name=filename, mime="text/csv")
        
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.output_files = []
            st.rerun()
