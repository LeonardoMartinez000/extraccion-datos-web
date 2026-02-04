import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import csv
import threading
import psycopg2 
import re 

# --- IMPORTS DE SCRIPTS ---
import db_operations 
import lusha_script
import apollo_script
import apollo_org
import lusha_org
import signal_script

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.stop_event = threading.Event()

        # --- Definición de UI (Sin cambios) ---
        self.title("Herramienta de Extracción de Datos v3.5 - Refactorizada")
        self.geometry("1100x850") 
        self.minsize(1100,850)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.tab_view = ctk.CTkTabview(self, corner_radius=5)
        self.tab_view.pack(pady=5, padx=5, fill="both", expand=True)
        self.tab1 = self.tab_view.add("Extracción de Contactos")
        #self.tab2 = self.tab_view.add("Limpieza y consolidación de datos")

        # Layout Pestaña 1 (Sin cambios)
        self.tab1.grid_columnconfigure(0, weight=1)
        self.tab1.grid_rowconfigure(1, weight=3) 
        self.tab1.grid_rowconfigure(3, weight=2) 
        
        self.api_frame = ctk.CTkFrame(self.tab1, corner_radius=5)
        self.api_frame.grid(row=0, column=0, pady=5, padx=0, sticky="ew")
        
        self.middle_frame = ctk.CTkFrame(self.tab1, corner_radius=0, fg_color="transparent")
        self.middle_frame.grid(row=1, column=0, pady=5, padx=0, sticky="nsew")
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_columnconfigure(1, weight=1)
        self.middle_frame.grid_rowconfigure(0, weight=1) 
        
        self.action_frame = ctk.CTkFrame(self.tab1, corner_radius=10)
        self.action_frame.grid(row=2, column=0, pady=5, padx=0, sticky="ew")

        self.cancel_frame = ctk.CTkFrame(self.tab1, corner_radius=10)
        self.cancel_frame.grid(row=3, column=0, pady=5, padx=0, sticky="ew")
        
        self.console_frame = ctk.CTkFrame(self.tab1, corner_radius=10)
        self.console_frame.grid(row=4, column=0, pady=(5,0), padx=0, sticky="nsew")

        # --- Layout Pestaña 2 (REFACTORIZADO) ---
        #self.tab2.grid_columnconfigure(0, weight=1)
        #self.tab2.grid_rowconfigure(0, weight=0) # db_frame
        #self.tab2.grid_rowconfigure(1, weight=0) # actions_container_frame (NO se expande)
        #self.tab2.grid_rowconfigure(2, weight=1) # console_frame_tab2 (SÍ se expande)
        
        #self.db_frame = ctk.CTkFrame(self.tab2, corner_radius=5)
        #self.db_frame.grid(row=0, column=0, pady=5, padx=0, sticky="ew")
        
        # --- (NUEVO) Contenedor para las 2 columnas de acciones ---
        #self.actions_container_frame = ctk.CTkFrame(self.tab2, fg_color="transparent")
        #self.actions_container_frame.grid(row=1, column=0, pady=5, padx=0, sticky="nsew")
        # Configura las dos columnas para que tengan el mismo tamaño
        #self.actions_container_frame.grid_columnconfigure((0, 1), weight=1, uniform="tab2_cols")
        
        # Consola (ahora en row=2)
        #self.console_frame_tab2 = ctk.CTkFrame(self.tab2, corner_radius=10)
        #self.console_frame_tab2.grid(row=2, column=0, pady=(5,0), padx=0, sticky="nsew")

        # --- Widgets ---
        self._create_widgets()
        #self._create_widgets_tab2() # <-- Esta función ha sido refactorizada

    # --- Creación de Widgets Pestaña 1 (Sin cambios) ---
    def _create_widgets(self):
        # API Keys (Sin cambios)
        self.apollo_api_label = ctk.CTkLabel(self.api_frame, text="API Key Apollo:")
        self.apollo_api_label.pack(side="left", padx=(5, 5), pady=5)
        self.apollo_api_entry = ctk.CTkEntry(self.api_frame, placeholder_text="...", show="*", width=250)
        self.apollo_api_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        self.lusha_api_label = ctk.CTkLabel(self.api_frame, text="API Key Lusha:")
        self.lusha_api_label.pack(side="left", padx=(5, 5), pady=5)
        self.lusha_api_entry = ctk.CTkEntry(self.api_frame, placeholder_text="...", show="*", width=250)
        self.lusha_api_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        self.signal_api_label = ctk.CTkLabel(self.api_frame, text="API Key SignalHire:")
        self.signal_api_label.pack(side="left", padx=(5, 5), pady=5)
        self.signal_api_entry = ctk.CTkEntry(self.api_frame, placeholder_text="...", show="*", width=250)
        self.signal_api_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        # Países (Sin cambios)
        countries_panel = ctk.CTkFrame(self.middle_frame, corner_radius=5)
        countries_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10)) 
        ctk.CTkLabel(countries_panel, text="Seleccionar Países", font=("Arial", 14, "bold")).pack(pady=10)
        scroll_frame = ctk.CTkScrollableFrame(countries_panel)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        paises = {
            "Norteamérica": ["United States", "Canada", "Mexico"],
            "Centroamérica": ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Nicaragua", "Panama"],
            "Suramérica": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", 
                "Peru", "Suriname", "Uruguay", "Venezuela"]
        }
        self.country_checkboxes = {}
        for region, lista_paises in paises.items():
            ctk.CTkLabel(scroll_frame, text=region, font=("Arial", 11, "bold")).pack(anchor="w", pady=(5, 5), padx=5)
            for pais in lista_paises:
                self.country_checkboxes[pais] = ctk.CTkCheckBox(scroll_frame, text=pais, checkbox_width=14, checkbox_height=14, font=("Arial", 11))
                self.country_checkboxes[pais].pack(anchor="w", padx=10, pady=2)
        
        # Archivos (Sin cambios)
        files_panel = ctk.CTkFrame(self.middle_frame, corner_radius=10)
        files_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0)) 
        self.cargos_entry = self._create_file_selector(files_panel, "Archivo CSV de Cargos", self.browse_cargos_file)
        self.empresas_entry = self._create_file_selector(files_panel, "Archivo CSV de Empresas", self.browse_empresas_file)
        self.id_org_entry = self._create_file_selector(files_panel, "Archivo CSV de Id Organizaciones", self.browse_id_org_file)
        self.output_entry = self._create_folder_selector(files_panel, "Carpeta de Destino para Resultados", self.browse_output_folder)
        
        # Botones (Sin cambios)
        self.apollo_contact_button = ctk.CTkButton(self.action_frame, text="Apollo Contactos", command=lambda: self.start_process("APOLLO_CONTACT"), height=30, font=("Arial", 12, "bold"), fg_color="#867903", hover_color="#E0CC11")
        self.apollo_contact_button.pack(side="left", fill="x", expand=True, padx=(2, 2), pady=2)
        self.apollo_org_button = ctk.CTkButton(self.action_frame, text="Apollo Organizaciones", command=lambda: self.start_process("APOLLO_ORG"), height=30, font=("Arial", 12, "bold"), fg_color="#867903", hover_color="#E0CC11")
        self.apollo_org_button.pack(side="left", fill="x", expand=True, padx=(2, 2), pady=2)
        self.lusha_contact_button = ctk.CTkButton(self.action_frame, text="Lusha Contactos", command=lambda: self.start_process("LUSHA_CONTACT"), height=30, font=("Arial", 12, "bold"), fg_color="#53045F", hover_color="#9E06B6")
        self.lusha_contact_button.pack(side="left", fill="x", expand=True, padx=(2, 2), pady=2)
        self.lusha_org_button = ctk.CTkButton(self.action_frame, text="Lusha Organizaciones", command=lambda: self.start_process("LUSHA_ORG"), height=30, font=("Arial", 12, "bold"), fg_color="#53045F", hover_color="#9E06B6")
        self.lusha_org_button.pack(side="left", fill="x", expand=True, padx=(2, 2), pady=2)
        self.signal_contact_button = ctk.CTkButton(self.action_frame, text="SignalHere Contactos", command=lambda: self.start_process("SIGNAL_CONTACT"), height=30, font=("Arial", 12, "bold"), fg_color="#083588", hover_color="#0A46B6")
        self.signal_contact_button.pack(side="left", fill="x", expand=True, padx=(2, 2), pady=2)
        
        self.cancel_button = ctk.CTkButton(self.cancel_frame, text="Cancelar", command=self.cancel_process, height=30, font=("Arial", 14, "bold"), fg_color="#781A07", hover_color="#B32003", state="disabled")
        self.cancel_button.pack(fill="x", padx=5, pady=5)
        
        # Consola (Sin cambios)
        ctk.CTkLabel(self.console_frame, text="Consola de Ejecución", font=("Arial", 12, "bold")).pack(pady=(5, 5))
        self.console_textbox = ctk.CTkTextbox(self.console_frame, state="disabled", font=("Consolas", 12))
        self.console_textbox.pack(fill="both", expand=True, padx=10, pady=(5, 5))

    # --- Creación de Widgets Pestaña 2 (REFACTORIZADO) ---
    def _create_widgets_tab2(self):
        # === Panel de Conexión (row 0) - Sin cambios ===
        self.db_frame.grid_columnconfigure((1, 3, 5), weight=1) 
        self.db_frame.grid_rowconfigure((0, 1), weight=0)
        ctk.CTkLabel(self.db_frame, text="Host:").grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")
        self.db_host_entry = ctk.CTkEntry(self.db_frame, placeholder_text="localhost")
        self.db_host_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        ctk.CTkLabel(self.db_frame, text="Base de Datos:").grid(row=0, column=2, padx=(10, 5), pady=8, sticky="w")
        self.db_name_entry = ctk.CTkEntry(self.db_frame, placeholder_text="nombre_db")
        self.db_name_entry.grid(row=0, column=3, padx=5, pady=8, sticky="ew")
        ctk.CTkLabel(self.db_frame, text="Puerto:").grid(row=0, column=4, padx=(10, 5), pady=8, sticky="w")
        self.db_port_entry = ctk.CTkEntry(self.db_frame, placeholder_text="5432", width=70) 
        self.db_port_entry.insert(0, "5432") 
        self.db_port_entry.grid(row=0, column=5, padx=(5, 10), pady=8, sticky="ew")
        ctk.CTkLabel(self.db_frame, text="Usuario:").grid(row=1, column=0, padx=(10, 5), pady=8, sticky="w")
        self.db_user_entry = ctk.CTkEntry(self.db_frame, placeholder_text="postgres")
        self.db_user_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        ctk.CTkLabel(self.db_frame, text="Password:").grid(row=1, column=2, padx=(10, 5), pady=8, sticky="w")
        self.db_pass_entry = ctk.CTkEntry(self.db_frame, placeholder_text="...", show="*")
        self.db_pass_entry.grid(row=1, column=3, padx=5, pady=8, sticky="ew")
        self.db_test_button = ctk.CTkButton(self.db_frame, text="Probar Conexión", width=120, height=30, font=("Arial", 14, "bold"), command=self.test_db_connection)
        self.db_test_button.grid(row=1, column=4, columnspan=2, sticky="nsew", padx=(10, 10), pady=8)
        
        
        # === Panel de Acciones (row 1) - Dividido en 2 columnas ===
        
        # --- Columna Izquierda: Carga y Consolidación ---
        self.load_frame = ctk.CTkFrame(self.actions_container_frame, border_width=2)
        self.load_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        ctk.CTkLabel(self.load_frame, text="1. Carga y Consolidación", font=("Arial", 16, "bold")).pack(pady=(10, 5))

        self.apollo_csv_entry = self._create_file_selector(self.load_frame, "Archivo CSV de Apollo", self.browse_apollo_csv)
        self.lusha_csv_entry = self._create_file_selector(self.load_frame, "Archivo CSV de Lusha", self.browse_lusha_csv)
        self.signal_csv_entry = self._create_file_selector(self.load_frame, "Archivo CSV de SignalHire", self.browse_signal_csv)

        self.db_load_button = ctk.CTkButton(self.load_frame, text="Cargar a Base de Datos", height=30, font=("Arial", 14, "bold"), fg_color="#063F80", hover_color="#0854AA", command=self.load_to_db)
        self.db_load_button.pack(fill="x", expand=True, padx=15, pady=10)
        
        self.db_consolidate_button = ctk.CTkButton(self.load_frame, text="Consolidar", height=30, font=("Arial", 14, "bold"), fg_color="#063F80", hover_color="#0854AA", command=self.consolidate_data)
        self.db_consolidate_button.pack(fill="x", expand=True, padx=15, pady=(0, 15))

        # --- Columna Derecha: Limpieza y Gestión ---
        self.clean_frame = ctk.CTkFrame(self.actions_container_frame, border_width=2)
        self.clean_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        ctk.CTkLabel(self.clean_frame, text="2. Limpieza y Gestión", font=("Arial", 16, "bold")).pack(pady=(10, 5))

        self.areas_csv_entry = self._create_file_selector(self.clean_frame, "Archivo CSV de Áreas", self.browse_areas_csv)
        self.cargos_v1_csv_entry = self._create_file_selector(self.clean_frame, "Archivo CSV de Cargos (v1)", self.browse_cargos_v1_csv)
        self.cargos_v2_csv_entry = self._create_file_selector(self.clean_frame, "Archivo CSV de Cargos (v2)", self.browse_cargos_v2_csv)

        self.db_clean_button = ctk.CTkButton(self.clean_frame, text="Limpiar y Estandarizar", height=30, font=("Arial", 14, "bold"), fg_color="#063F80", hover_color="#0854AA", command=self.clean_data)
        self.db_clean_button.pack(fill="x", expand=True, padx=15, pady=10)
        
        self.db_load_gestion_button = ctk.CTkButton(self.clean_frame, text="Cargar Gestión", height=30, font=("Arial", 14, "bold"), fg_color="#063F80", hover_color="#0854AA", command=self.load_gestion_data)
        self.db_load_gestion_button.pack(fill="x", expand=True, padx=15, pady=(0, 15))


        # === Consola (row 2) - Movida al final ===
        ctk.CTkLabel(self.console_frame_tab2, text="Consola de Limpieza y Consolidación", font=("Arial", 12, "bold")).pack(pady=(5, 5))
        self.console_textbox_tab2 = ctk.CTkTextbox(self.console_frame_tab2, state="disabled", font=("Consolas", 12))
        self.console_textbox_tab2.pack(fill="both", expand=True, padx=10, pady=(5, 5))

    # ==========================================================
    # --- FUNCIONES DE LA UI (Ayudantes, Loggers, Browsers) ---
    # ==========================================================

    def log(self, message):
        """Escribe un mensaje en la consola de la Pestaña 1."""
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert("end", message + "\n")
        self.console_textbox.configure(state="disabled")
        self.console_textbox.see("end")

    def log_tab2(self, message):
        """Escribe un mensaje en la consola de la Pestaña 2."""
        self.console_textbox_tab2.configure(state="normal")
        self.console_textbox_tab2.insert("end", message + "\n")
        self.console_textbox_tab2.configure(state="disabled")
        self.console_textbox_tab2.see("end")

    # (Funciones browse_... Pestaña 1)
    def browse_cargos_file(self):
        path = filedialog.askopenfilename(title="Archivo de Cargos", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.cargos_entry.delete(0, "end"); self.cargos_entry.insert(0, path)

    def browse_empresas_file(self):
        path = filedialog.askopenfilename(title="Archivo de Empresas", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.empresas_entry.delete(0, "end"); self.empresas_entry.insert(0, path)

    def browse_id_org_file(self):
        path = filedialog.askopenfilename(title="Archivo Id Organizaciones", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.id_org_entry.delete(0, "end"); self.id_org_entry.insert(0, path)
        
    def browse_output_folder(self):
        path = filedialog.askdirectory(title="Carpeta de Destino")
        if path: self.output_entry.delete(0, "end"); self.output_entry.insert(0, path)

    # (Funciones browse_... Pestaña 2)
    def browse_apollo_csv(self):
        path = filedialog.askopenfilename(title="Archivo CSV de Apollo", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.apollo_csv_entry.delete(0, "end"); self.apollo_csv_entry.insert(0, path)

    def browse_lusha_csv(self):
        path = filedialog.askopenfilename(title="Archivo CSV de Lusha", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.lusha_csv_entry.delete(0, "end"); self.lusha_csv_entry.insert(0, path)
    
    def browse_signal_csv(self):
        path = filedialog.askopenfilename(title="Archivo CSV de SignalHire", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.signal_csv_entry.delete(0, "end"); self.signal_csv_entry.insert(0, path)
    
    # --- (NUEVAS FUNCIONES BROWSE Pestaña 2) ---
    def browse_areas_csv(self):
        path = filedialog.askopenfilename(title="Archivo CSV de Áreas", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.areas_csv_entry.delete(0, "end"); self.areas_csv_entry.insert(0, path)

    def browse_cargos_v1_csv(self):
        path = filedialog.askopenfilename(title="Archivo CSV de Cargos (v1)", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.cargos_v1_csv_entry.delete(0, "end"); self.cargos_v1_csv_entry.insert(0, path)

    def browse_cargos_v2_csv(self):
        path = filedialog.askopenfilename(title="Archivo CSV de Cargos (v2)", filetypes=[("Archivos CSV", "*.csv")])
        if path: self.cargos_v2_csv_entry.delete(0, "end"); self.cargos_v2_csv_entry.insert(0, path)


    # (Funciones _create_..._selector sin cambios)
    def _create_file_selector(self, parent, label_text, command):
        # Esta función ahora devuelve la 'entry' para que podamos referenciarla
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=10, padx=10, fill="x") # Reducido pady de 15 a 10
        ctk.CTkLabel(frame, text=label_text, font=("Arial", 14, "bold")).pack(anchor="w")
        entry = ctk.CTkEntry(frame, placeholder_text="Seleccionar archivo...")
        entry.pack(side="left", fill="x", expand=True, pady=5, padx=(0, 10))
        ctk.CTkButton(frame, text="Examinar", width=100, command=command).pack(side="left")
        return entry

    def _create_folder_selector(self, parent, label_text, command):
        # Esta función ahora devuelve la 'entry' para que podamos referenciarla
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=15, padx=15, fill="x")
        ctk.CTkLabel(frame, text=label_text, font=("Arial", 14, "bold")).pack(anchor="w")
        entry = ctk.CTkEntry(frame, placeholder_text="Seleccionar carpeta...")
        entry.pack(side="left", fill="x", expand=True, pady=5, padx=(0, 10))
        ctk.CTkButton(frame, text="Examinar", width=100, command=command).pack(side="left")
        return entry
    
    def leer_csv_lista(self, filepath):
        """
        Lee la primera columna de un CSV, manejando codificaciones comunes de Excel.
        """
        self.log(f"Leyendo archivo: {os.path.basename(filepath)}...")
        # Intentamos con 'latin-1' que es el estándar de Excel en español
        # Si falla, podrías probar con 'utf-8-sig'
        try:
            with open(filepath, mode='r', encoding='latin-1') as f: 
                reader = csv.reader(f)
                try:
                    next(reader) # Omite encabezado
                except StopIteration:
                    return [] 
                
                return [row[0].strip() for row in reader if row and row[0].strip()]
        except UnicodeDecodeError:
            # Fallback en caso de que sea un UTF-8 real
            with open(filepath, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader)
                return [row[0].strip() for row in reader if row and row[0].strip()]
        except FileNotFoundError:
            self.log(f"❌ ERROR: Archivo no encontrado: {filepath}")
            raise 
        except Exception as e:
            self.log(f"❌ ERROR al leer archivo CSV: {e}")
            raise

    # --- FUNCIONES DE CONTROL DE HILOS (Threads) ---

    def toggle_buttons(self, is_running: bool):
        """
        (NUEVA FUNCIÓN AUXILIAR)
        Habilita o deshabilita los botones de acción de la Pestaña 1.
        """
        state = "disabled" if is_running else "normal"
        self.apollo_contact_button.configure(state=state)
        self.apollo_org_button.configure(state=state)
        self.lusha_contact_button.configure(state=state)
        self.lusha_org_button.configure(state=state)
        self.signal_contact_button.configure(state=state)
        
        cancel_state = "normal" if is_running else "disabled"
        self.cancel_button.configure(text="Cancelar", state=cancel_state)

    def monitor_thread(self, thread):
        """Monitorea el hilo de la Pestaña 1."""
        if thread.is_alive():
            self.after(100, self.monitor_thread, thread)
        else:
            self.on_process_finished()

    def on_process_finished(self):
        """
        (REFACTORIZADO)
        Se llama cuando un hilo de la Pestaña 1 termina.
        """
        self.log("...Proceso detenido o finalizado...")
        self.toggle_buttons(is_running=False) # <- USA LA NUEVA FUNCIÓN
        self.stop_event.clear()

    def cancel_process(self):
        """(Sin cambios)"""
        self.log("...🛑... Intentando cancelar el proceso...")
        self.stop_event.set()
        self.cancel_button.configure(text="Cancelando...", state="disabled")
    
    # --- Pestaña 2 (Helpers con cambios) ---
    def _disable_tab2_buttons(self):
        """Deshabilita los botones de acción de la Pestaña 2."""
        self.db_load_button.configure(state="disabled")
        self.db_clean_button.configure(state="disabled")
        self.db_consolidate_button.configure(state="disabled")
        self.db_test_button.configure(state="disabled")
        self.db_load_gestion_button.configure(state="disabled") # <-- AÑADIDO

    def _enable_tab2_buttons(self):
        """Habilita los botones de acción de la Pestaña 2."""
        self.db_load_button.configure(state="normal")
        self.db_clean_button.configure(state="normal")
        self.db_consolidate_button.configure(state="normal")
        self.db_test_button.configure(state="normal")
        self.db_load_gestion_button.configure(state="normal") # <-- AÑADIDO

    def monitor_tab2_thread(self, thread):
        """Monitorea un hilo de la Pestaña 2 y reactiva los botones al finalizar."""
        if thread.is_alive():
            self.after(100, self.monitor_tab2_thread, thread)
        else:
            self.log_tab2("...Proceso en Pestaña 2 finalizado...")
            self._enable_tab2_buttons()

    def _get_db_params(self):
        """Obtiene los parámetros de conexión de la UI."""
        params = {
            "host": self.db_host_entry.get(),
            "dbname": self.db_name_entry.get(),
            "user": self.db_user_entry.get(),
            "password": self.db_pass_entry.get(),
            "port": self.db_port_entry.get()
        }
        if not all(params.values()):
            self.log_tab2("❌ ERROR: Todos los campos de conexión son obligatorios.")
            messagebox.showwarning("Campos Incompletos", "Por favor, rellene todos los campos de conexión a la base de datos.")
            return None
        return params

    # ==========================================================
    # --- COMANDOS DE BOTONES (Delegan la lógica) ---
    # ==========================================================

    # --- Pestaña 1: Extracción (Sin cambios) ---
    def start_process(self, process_type: str):
        """
        (FUNCIÓN PRINCIPAL REFACTORIZADA)
        Valida y despacha la tarea correcta según el botón presionado.
        """
        self.stop_event.clear()
        
        # 1. Obtener todos los valores de la UI
        ui_values = {
            "apollo_api": self.apollo_api_entry.get(),
            "lusha_api": self.lusha_api_entry.get(),
            "signal_api": self.signal_api_entry.get(),
            "cargos_file": self.cargos_entry.get(),
            "empresas_file": self.empresas_entry.get(),
            "id_org_file": self.id_org_entry.get(),
            "output_folder": self.output_entry.get(),
            "paises": [pais for pais, cb in self.country_checkboxes.items() if cb.get()]
        }

        target_func = None
        args = ()
        validation_ok = False

        try:
            # 2. Despachador: Valida y prepara la tarea
            
            if process_type == "APOLLO_CONTACT":
                # Requeridos: Api Key Apollo, Cargos, empresas, paises, carpeta de destino
                required = [ui_values["apollo_api"], ui_values["cargos_file"], ui_values["empresas_file"], ui_values["paises"], ui_values["output_folder"]]
                if not all(required):
                    self.log("❌ ERROR: Para 'Apollo Contactos' se requiere: API Key Apollo, Archivo Cargos, Archivo Empresas, Países y Carpeta de Destino.")
                    return

                empresas = self.leer_csv_lista(ui_values["empresas_file"])
                cargos = self.leer_csv_lista(ui_values["cargos_file"])
                if not empresas or not cargos:
                    self.log("❌ ERROR: El archivo de empresas o cargos está vacío (después del encabezado).")
                    return

                self.log(f"\n--- Iniciando Proceso: {process_type} ---")
                self.log(f"✅ Validado. {len(empresas)} empresas y {len(cargos)} cargos.")
                
                target_func = apollo_script.run
                args = (ui_values["apollo_api"], empresas, cargos, ui_values["paises"], ui_values["output_folder"], self.log, self.stop_event)
                validation_ok = True

            elif process_type == "APOLLO_ORG":
                # Requeridos: Api Key Apollo, id Organizaciones, carpeta de destino
                required = [ui_values["apollo_api"], ui_values["id_org_file"], ui_values["output_folder"]]
                if not all(required):
                    self.log("❌ ERROR: Para 'Apollo Organizaciones' se requiere: API Key Apollo, Archivo Id Organizaciones y Carpeta de Destino.")
                    return
                
                self.log(f"\n--- Iniciando Proceso: {process_type} ---")
                self.log(f"✅ Validado. Usando archivo: {os.path.basename(ui_values['id_org_file'])}")

                target_func = apollo_org.run # Usa el script refactorizado
                args = (ui_values["apollo_api"], ui_values["id_org_file"], ui_values["output_folder"], self.log, self.stop_event)
                validation_ok = True

            elif process_type == "LUSHA_CONTACT":
                # Requeridos: Api Key lusha, Cargos, empresas, paises, carpeta de destino
                required = [ui_values["lusha_api"], ui_values["cargos_file"], ui_values["empresas_file"], ui_values["paises"], ui_values["output_folder"]]
                if not all(required):
                    self.log("❌ ERROR: Para 'Lusha Contactos' se requiere: API Key Lusha, Archivo Cargos, Archivo Empresas, Países y Carpeta de Destino.")
                    return

                empresas = self.leer_csv_lista(ui_values["empresas_file"])
                cargos = self.leer_csv_lista(ui_values["cargos_file"])
                if not empresas or not cargos:
                    self.log("❌ ERROR: El archivo de empresas o cargos está vacío.")
                    return

                self.log(f"\n--- Iniciando Proceso: {process_type} ---")
                self.log(f"✅ Validado. {len(empresas)} empresas y {len(cargos)} cargos.")

                target_func = lusha_script.run
                args = (ui_values["lusha_api"], empresas, cargos, ui_values["paises"], ui_values["output_folder"], self.log, self.stop_event)
                validation_ok = True

            elif process_type == "LUSHA_ORG":
                # Requeridos: Api Key lusha, id Organizaciones, carpeta de destino
                if not lusha_org:
                    self.log(f"❌ ERROR: El script 'lusha_org.py' no se pudo importar. No se puede ejecutar {process_type}.")
                    return
                
                required = [ui_values["lusha_api"], ui_values["id_org_file"], ui_values["output_folder"]]
                if not all(required):
                    self.log("❌ ERROR: Para 'Lusha Organizaciones' se requiere: API Key Lusha, Archivo Id Organizaciones y Carpeta de Destino.")
                    return

                self.log(f"\n--- Iniciando Proceso: {process_type} ---")
                self.log(f"✅ Validado. Usando archivo: {os.path.basename(ui_values['id_org_file'])}")

                target_func = lusha_org.run # Asumiendo que existe
                args = (ui_values["lusha_api"], ui_values["id_org_file"], ui_values["output_folder"], self.log, self.stop_event)
                validation_ok = True

            elif process_type == "SIGNAL_CONTACT":
                # Requeridos: Api Key SignalHire, Cargos, empresas, paises, carpeta de destino
                if not signal_script:
                    self.log(f"❌ ERROR: El script 'signal_script.py' no se pudo importar. No se puede ejecutar {process_type}.")
                    return

                required = [ui_values["signal_api"], ui_values["cargos_file"], ui_values["empresas_file"], ui_values["paises"], ui_values["output_folder"]]
                if not all(required):
                    self.log("❌ ERROR: Para 'SignalHire Contactos' se requiere: API Key SignalHire, Archivo Cargos, Archivo Empresas, Países y Carpeta de Destino.")
                    return
                
                empresas = self.leer_csv_lista(ui_values["empresas_file"])
                cargos = self.leer_csv_lista(ui_values["cargos_file"])
                if not empresas or not cargos:
                    self.log("❌ ERROR: El archivo de empresas o cargos está vacío.")
                    return

                self.log(f"\n--- Iniciando Proceso: {process_type} ---")
                self.log(f"✅ Validado. {len(empresas)} empresas y {len(cargos)} cargos.")

                target_func = signal_script.run # Asumiendo que existe
                args = (ui_values["signal_api"], empresas, cargos, ui_values["paises"], ui_values["output_folder"], self.log, self.stop_event)
                validation_ok = True

            elif process_type == "SIGNAL_ORG":
                self.log(f"ℹ️ La función '{process_type}' no está implementada todavía.")
                # No hacer nada
                return

            else:
                self.log(f"⚠️ ADVERTENCIA: Tipo de proceso desconocido: {process_type}")
                return

        except Exception as e:
            self.log(f"❌ ERROR FATAL al preparar el proceso: {e}")
            import traceback
            self.log(traceback.format_exc())
            return
        
        # 3. Si la validación fue exitosa, lanzar el hilo
        if validation_ok and target_func:
            self.toggle_buttons(is_running=True)
            thread = threading.Thread(target=target_func, args=args)
            thread.start()
            self.monitor_thread(thread)
        else:
            # Este log es por si algo muy raro pasa
            self.log("ℹ️ Proceso no iniciado. Revise los errores de validación.")


    # --- Pestaña 2: Conexión y Carga (Sin cambios en lógica, solo funciones añadidas) ---

    def test_db_connection(self):
        """(Botón) Llama a la lógica de prueba de conexión en un hilo."""
        db_params = self._get_db_params()
        if db_params is None:
            return
            
        self.log_tab2(f"Intentando conexión a {db_params['host']}:{db_params['port']}...")
        self._disable_tab2_buttons()

        thread = threading.Thread(
            target=db_operations.execute_test_connection,
            args=(db_params, self.log_tab2, self.after)
        )
        thread.start()
        self.monitor_tab2_thread(thread)

    def load_to_db(self):
        apollo_file = self.apollo_csv_entry.get()
        lusha_file = self.lusha_csv_entry.get()
        
        if not apollo_file or not lusha_file:
            self.log_tab2("❌ ERROR: Debe seleccionar los archivos CSV de Apollo y Lusha.")
            messagebox.showwarning("Archivos Faltantes", "Debe seleccionar ambos archivos CSV antes de cargar.")
            return
            
        db_params = self._get_db_params()
        if db_params is None:
            return

        self.log_tab2("\n--- Iniciando Carga a Base de Datos ---")
        self._disable_tab2_buttons()
        
        thread = threading.Thread(
            target=db_operations.execute_load_to_db,
            args=(db_params, apollo_file, lusha_file, self.log_tab2, self.after)
        )
        thread.start()
        self.monitor_tab2_thread(thread)
        
    def clean_data(self):
        # --- (FUTURA MEJORA) Pasar los archivos de areas/cargos ---
        areas_file = self.areas_csv_entry.get()
        cargos_v1_file = self.cargos_v1_csv_entry.get()
        cargos_v2_file = self.cargos_v2_csv_entry.get()

        if not all([areas_file, cargos_v1_file, cargos_v2_file]):
            self.log_tab2("❌ ERROR: Debe seleccionar los 3 archivos (Áreas, Cargos v1, Cargos v2) para limpiar.")
            messagebox.showwarning("Archivos Faltantes", "Debe seleccionar los archivos de Áreas y Cargos para estandarizar.")
            return
        
        self.log_tab2("\n--- Iniciando Limpieza y Estandarización ---")
        self.log_tab2(f"Usando Áreas: {os.path.basename(areas_file)}")
        self.log_tab2(f"Usando Cargos v1: {os.path.basename(cargos_v1_file)}")
        self.log_tab2(f"Usando Cargos v2: {os.path.basename(cargos_v2_file)}")
        
        self._disable_tab2_buttons()
        
        # (NOTA: db_operations.execute_clean_data necesita ser actualizado para aceptar estos archivos)
        thread = threading.Thread(
            target=db_operations.execute_clean_data,
            # args=(self.log_tab2, areas_file, cargos_v1_file, cargos_v2_file) # <-- Así debería ser
            args=(self.log_tab2,) # <-- Temporalmente como estaba
        )
        self.log_tab2("ADVERTENCIA: La lógica de 'clean_data' aún no usa los archivos seleccionados.")
        thread.start()
        self.monitor_tab2_thread(thread)

    def consolidate_data(self):
        self.log_tab2("\n--- Iniciando Consolidación de Datos ---")
        self._disable_tab2_buttons()
        
        thread = threading.Thread(
            target=db_operations.execute_consolidate_data,
            args=(self.log_tab2,)
        )
        thread.start()
        self.monitor_tab2_thread(thread)

    # --- (NUEVA FUNCIÓN DE BOTÓN) ---
    def load_gestion_data(self):
        self.log_tab2("\n--- Iniciando Carga de Gestión ---")
        self.log_tab2("ℹ️ Esta función ('load_gestion_data') aún debe ser implementada en db_operations.py")

if __name__ == "__main__":
    app = App()
    app.mainloop()

