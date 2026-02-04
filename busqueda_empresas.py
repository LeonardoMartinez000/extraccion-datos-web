import customtkinter as ctk
from tkinter import filedialog
import os

# --- Clase Principal de la Aplicación ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. Configuración de la Ventana Principal ---
        self.title("Herramienta de Extracción de Datos v2.1")
        self.geometry("850x750") # Aumentamos un poco la altura
        self.minsize(800, 650)

        ctk.set_appearance_mode("Dark") 
        ctk.set_default_color_theme("blue")

        # --- 2. Creación de Frames Principales ---
        self.api_frame = ctk.CTkFrame(self, corner_radius=10)
        self.api_frame.pack(pady=10, padx=20, fill="x")

        self.middle_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.middle_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.middle_frame.grid_columnconfigure(0, weight=1) 
        self.middle_frame.grid_columnconfigure(1, weight=1) 

        self.action_frame = ctk.CTkFrame(self, corner_radius=10)
        self.action_frame.pack(pady=10, padx=20, fill="x")
        
        self.console_frame = ctk.CTkFrame(self, corner_radius=10)
        self.console_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # --- 3. Widgets del Frame de API Keys ---
        self.apollo_api_label = ctk.CTkLabel(self.api_frame, text="API Key Apollo:", font=("Arial", 12))
        self.apollo_api_label.pack(side="left", padx=(15, 5), pady=10)
        self.apollo_api_entry = ctk.CTkEntry(self.api_frame, placeholder_text="Ingrese la API Key de Apollo", show="*", width=250)
        self.apollo_api_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        
        self.lusha_api_label = ctk.CTkLabel(self.api_frame, text="API Key Lusha:", font=("Arial", 12))
        self.lusha_api_label.pack(side="left", padx=(15, 5), pady=10)
        self.lusha_api_entry = ctk.CTkEntry(self.api_frame, placeholder_text="Ingrese la API Key de Lusha", show="*", width=250)
        self.lusha_api_entry.pack(side="left", fill="x", expand=True, padx=(5, 15), pady=10)
        
        # --- 4. Widgets del Frame Central ---
        # Panel Izquierdo: Lista de Países
        self.countries_panel = ctk.CTkFrame(self.middle_frame, corner_radius=10)
        self.countries_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.countries_label = ctk.CTkLabel(self.countries_panel, text="Seleccionar Países", font=("Arial", 14, "bold"))
        self.countries_label.pack(pady=10)
        
        self.scrollable_countries_frame = ctk.CTkScrollableFrame(self.countries_panel, label_text="")
        self.scrollable_countries_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        paises = {
            "Norteamérica": ["United States", "Canada", "Mexico"],
            "Centroamérica": ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Nicaragua", "Panama"],
            "Suramérica": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"]
        }
        
        self.country_checkboxes = {}
        for region, lista_paises in paises.items():
            region_label = ctk.CTkLabel(self.scrollable_countries_frame, text=region, font=("Arial", 12, "bold"))
            region_label.pack(anchor="w", pady=(10, 5), padx=5)
            for pais in lista_paises:
                checkbox = ctk.CTkCheckBox(self.scrollable_countries_frame, text=pais)
                checkbox.pack(anchor="w", padx=15, pady=2)
                self.country_checkboxes[pais] = checkbox

        # Panel Derecho: Carga de Archivos
        self.files_panel = ctk.CTkFrame(self.middle_frame, corner_radius=10)
        self.files_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Sección para archivo de CARGOS
        self.cargos_frame = ctk.CTkFrame(self.files_panel, fg_color="transparent")
        self.cargos_frame.pack(pady=15, padx=15, fill="x")
        self.cargos_label = ctk.CTkLabel(self.cargos_frame, text="Archivo CSV de Cargos", font=("Arial", 14, "bold"))
        self.cargos_label.pack(anchor="w")
        self.cargos_entry = ctk.CTkEntry(self.cargos_frame, placeholder_text="Seleccionar archivo...")
        self.cargos_entry.pack(side="left", fill="x", expand=True, pady=5, padx=(0,10))
        self.cargos_button = ctk.CTkButton(self.cargos_frame, text="Examinar", width=100, command=self.browse_cargos_file)
        self.cargos_button.pack(side="left")

        # Sección para archivo de EMPRESAS
        self.empresas_frame = ctk.CTkFrame(self.files_panel, fg_color="transparent")
        self.empresas_frame.pack(pady=15, padx=15, fill="x")
        self.empresas_label = ctk.CTkLabel(self.empresas_frame, text="Archivo CSV de Empresas", font=("Arial", 14, "bold"))
        self.empresas_label.pack(anchor="w")
        self.empresas_entry = ctk.CTkEntry(self.empresas_frame, placeholder_text="Seleccionar archivo...")
        self.empresas_entry.pack(side="left", fill="x", expand=True, pady=5, padx=(0,10))
        self.empresas_button = ctk.CTkButton(self.empresas_frame, text="Examinar", width=100, command=self.browse_empresas_file)
        self.empresas_button.pack(side="left")

        # --- INICIO DEL CAMBIO: Sección para la carpeta de destino ---
        self.output_frame = ctk.CTkFrame(self.files_panel, fg_color="transparent")
        self.output_frame.pack(pady=15, padx=15, fill="x")
        self.output_label = ctk.CTkLabel(self.output_frame, text="Carpeta de Destino para Resultados", font=("Arial", 14, "bold"))
        self.output_label.pack(anchor="w")
        self.output_entry = ctk.CTkEntry(self.output_frame, placeholder_text="Seleccionar carpeta de destino...")
        self.output_entry.pack(side="left", fill="x", expand=True, pady=5, padx=(0,10))
        self.output_button = ctk.CTkButton(self.output_frame, text="Examinar", width=100, command=self.browse_output_folder)
        self.output_button.pack(side="left")
        # --- FIN DEL CAMBIO ---

        # --- 5. Widgets del Frame de Acciones ---
        self.apollo_button = ctk.CTkButton(self.action_frame, text="Ejecutar con Apollo", command=lambda: self.run_process("Apollo"), height=40, font=("Arial", 14, "bold"))
        self.apollo_button.pack(side="left", fill="x", expand=True, padx=(10,5), pady=10)
        self.lusha_button = ctk.CTkButton(self.action_frame, text="Ejecutar con Lusha", command=lambda: self.run_process("Lusha"), height=40, font=("Arial", 14, "bold"), fg_color="#6A8A0A", hover_color="#88B00D")
        self.lusha_button.pack(side="left", fill="x", expand=True, padx=(5,10), pady=10)
        
        # --- 6. Widgets del Frame de Consola ---
        self.console_label = ctk.CTkLabel(self.console_frame, text="Consola de Ejecución", font=("Arial", 14, "bold"))
        self.console_label.pack(pady=(10, 5))
        self.console_textbox = ctk.CTkTextbox(self.console_frame, state="disabled", font=("Consolas", 12))
        self.console_textbox.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    # --- 7. Funciones de la Aplicación ---
    def browse_cargos_file(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo de Cargos", filetypes=[("Archivos CSV", "*.csv")])
        if file_path:
            self.cargos_entry.delete(0, "end")
            self.cargos_entry.insert(0, file_path)
            self.log(f"Archivo de Cargos seleccionado: {os.path.basename(file_path)}")

    def browse_empresas_file(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo de Empresas", filetypes=[("Archivos CSV", "*.csv")])
        if file_path:
            self.empresas_entry.delete(0, "end")
            self.empresas_entry.insert(0, file_path)
            self.log(f"Archivo de Empresas seleccionado: {os.path.basename(file_path)}")
    
    # --- INICIO DEL CAMBIO: Nueva función para seleccionar la carpeta de destino ---
    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(title="Seleccionar Carpeta de Destino")
        if folder_path:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder_path)
            self.log(f"Carpeta de destino seleccionada: {folder_path}")
    # --- FIN DEL CAMBIO ---

    def run_process(self, platform):
        self.log(f"\n--- Iniciando Proceso con {platform} ---")

        # Recopilar y validar datos
        api_key = self.lusha_api_entry.get() if platform == "Lusha" else self.apollo_api_entry.get()
        selected_countries = [pais for pais, checkbox in self.country_checkboxes.items() if checkbox.get() == 1]
        cargos_file = self.cargos_entry.get()
        empresas_file = self.empresas_entry.get()
        output_folder = self.output_entry.get() # <-- Obtener la nueva ruta

        # Validaciones
        if not api_key:
            self.log(f"❌ ERROR: La API Key de {platform} no puede estar vacía.")
            return
        if not selected_countries:
            self.log("❌ ERROR: Debes seleccionar al menos un país.")
            return
        if not cargos_file or not empresas_file:
            self.log("❌ ERROR: Debes seleccionar ambos archivos CSV (Cargos y Empresas).")
            return
        # --- INICIO DEL CAMBIO: Validar la carpeta de destino ---
        if not output_folder:
            self.log("❌ ERROR: Debes seleccionar una carpeta para guardar los resultados.")
            return
        # --- FIN DEL CAMBIO ---
        
        self.log(f"✅ Validaciones correctas.")
        self.log(f"🔑 API Key de {platform} cargada.")
        self.log(f"🌍 Países seleccionados: {len(selected_countries)}")
        self.log(f"📄 Archivo de Cargos: {os.path.basename(cargos_file)}")
        self.log(f"📄 Archivo de Empresas: {os.path.basename(empresas_file)}")
        self.log(f"📂 Carpeta de Destino: {output_folder}") # <-- Mostrar en el log
        self.log("🚀 Ejecutando script de extracción...")
        
        #
        # AQUÍ DEBES INTEGRAR TU SCRIPT DE EXTRACCIÓN
        # if platform == "Lusha":
        #     import lusha_script
        #     # Pasar la nueva ruta a tu función
        #     lusha_script.run(api_key, selected_countries, cargos_file, empresas_file, output_folder)
        #
        
        self.log("✅ Proceso finalizado (simulación).")
        self.log("-----------------------------------------")

    def log(self, message):
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert("end", message + "\n")
        self.console_textbox.configure(state="disabled")
        self.console_textbox.see("end")

# --- Ejecución de la App ---
if __name__ == "__main__":
    app = App()
    app.mainloop()