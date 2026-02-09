import requests
import json
import csv
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import threading

def limpiar_texto(texto):
    if texto is None or not isinstance(texto, str):
        return texto if texto is not None else ""
    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ]', '', texto)
    texto = ' '.join(texto.split())
    return texto.strip()

class ApolloScraper:
    def __init__(self, api_key, output_folder, log_callback, stop_event):
        self.api_key = api_key
        self.output_folder = output_folder
        self.log_callback = log_callback
        self.stop_event = stop_event
        
        self.url = "https://api.apollo.io/api/v1/contacts/search"
        self.headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'accept': 'application/json',
            'x-api-key': api_key
        }
        
        self.resultados = []
        self.ids_encontrados = set()
        self.write_lock = Lock()
        self.stats_lock = Lock()
        
        self.total_encontrados = 0
        self.total_requests = 0
        self.empresas_procesadas = 0
        
        self.campos = [
            "empresa_buscada", "origen", "id", "first_name", "last_name", "name", "linkedin_url", 
            "title", "headline", "email_status", "email", "state", "city", "country", 
            "organization_name", "organization_id", "raw_number", "sanitized_number", "contact_email"
        ]
        
        self.output_file = os.path.join(output_folder, "resultados_apollo.csv")
        self._inicializar_csv()
    
    def _inicializar_csv(self):
        """Crea el archivo CSV con encabezados"""
        if os.path.exists(self.output_file):
            try: 
                os.remove(self.output_file)
            except: 
                pass
        
        with open(self.output_file, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=self.campos)
            writer.writeheader()
    
    def _escribir_resultados(self, nuevos_resultados):
        """Escribe resultados de forma incremental y thread-safe"""
        if not nuevos_resultados:
            return
        
        with self.write_lock:
            with open(self.output_file, mode="a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=self.campos)
                writer.writerows(nuevos_resultados)
    
    def safe_get(self, dct, *keys):
        for key in keys:
            if isinstance(dct, list):
                try: 
                    dct = dct[key]
                except: 
                    return None
            elif isinstance(dct, dict):
                dct = dct.get(key)
            else: 
                return None
            if dct is None: 
                return None
        return dct
    
    def _hacer_request(self, payload, retry_count=0, max_retries=3):
        """Realiza un request con manejo de errores y retry logic"""
        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 429:
                if retry_count < max_retries:
                    wait_time = min(2 ** retry_count, 10)  # Backoff exponencial, máx 10s
                    time.sleep(wait_time)
                    return self._hacer_request(payload, retry_count + 1, max_retries)
                return None
            
            else:
                return None
                
        except Exception as e:
            if retry_count < max_retries:
                time.sleep(1)
                return self._hacer_request(payload, retry_count + 1, max_retries)
            return None
    
    def _procesar_contactos(self, contacts, empresa_buscada):
        """Procesa lista de contactos y retorna solo los nuevos"""
        nuevos_resultados = []
        
        for person in contacts:
            p_id = person.get("id")
            
            # Verificación thread-safe de IDs duplicados
            with self.stats_lock:
                if p_id and p_id not in self.ids_encontrados:
                    self.ids_encontrados.add(p_id)
                else:
                    continue  # Skip duplicados
            
            nuevos_resultados.append({
                "empresa_buscada": limpiar_texto(empresa_buscada),
                "origen": "contacts_api",
                "id": p_id,
                "first_name": limpiar_texto(person.get("first_name")),
                "last_name": limpiar_texto(person.get("last_name")),
                "name": limpiar_texto(person.get("name")),
                "linkedin_url": person.get("linkedin_url"),
                "title": limpiar_texto(person.get("title")),
                "headline": limpiar_texto(person.get("headline")),
                "email_status": person.get("email_status"),
                "email": person.get("email"),
                "state": limpiar_texto(person.get("state")),
                "city": limpiar_texto(person.get("city")),
                "country": limpiar_texto(person.get("country")),
                "organization_name": limpiar_texto(self.safe_get(person, "organization", "name")),
                "organization_id": self.safe_get(person, "organization", "id"),
                "raw_number": limpiar_texto(self.safe_get(person, "phone_numbers", 0, "raw_number")),
                "sanitized_number": limpiar_texto(self.safe_get(person, "phone_numbers", 0, "sanitized_number")),
                "contact_email": person.get("contact_email")
            })
        
        return nuevos_resultados
    
    def _procesar_tarea(self, empresa, pais, chunk_cargos, chunk_idx):
        """Procesa una tarea individual (empresa + país + chunk de cargos)"""
        if self.stop_event.is_set():
            return 0
        
        payload = {
            "q_organization_name": empresa,
            "organization_locations": [pais],
            "person_titles": chunk_cargos,
            "page": 1,
            "per_page": 100
        }
        
        data = self._hacer_request(payload)
        
        with self.stats_lock:
            self.total_requests += 1
        
        if not data:
            return 0
        
        contacts = data.get('contacts', [])
        nuevos_resultados = self._procesar_contactos(contacts, empresa)
        
        # Escritura incremental
        if nuevos_resultados:
            self._escribir_resultados(nuevos_resultados)
            with self.stats_lock:
                self.total_encontrados += len(nuevos_resultados)
        
        return len(nuevos_resultados)
    
    def ejecutar_busqueda(self, empresas, cargos, paises, max_workers=10):
        """
        Ejecuta la búsqueda con procesamiento paralelo
        max_workers: número de threads paralelos (ajusta según tu plan de Apollo)
        """
        self.log_callback(f"🚀 Iniciando búsqueda optimizada...")
        self.log_callback(f"📊 {len(empresas)} empresas × {len(paises)} países × {len(cargos)} cargos")
        
        # Preparar chunks de cargos
        chunk_size = 10
        chunks_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
        
        # Crear lista de todas las tareas
        tareas = []
        for empresa in empresas:
            empresa_clean = empresa.strip()
            for pais in paises:
                for idx, chunk in enumerate(chunks_cargos):
                    tareas.append((empresa_clean, pais, chunk, idx))
        
        total_tareas = len(tareas)
        self.log_callback(f"⚙️  Total de requests a realizar: {total_tareas}")
        self.log_callback(f"🔄 Procesando con {max_workers} workers paralelos...\n")
        
        tareas_completadas = 0
        ultimo_reporte = 0
        
        # Procesamiento paralelo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todas las tareas
            futures = {
                executor.submit(self._procesar_tarea, empresa, pais, chunk, idx): (empresa, pais)
                for empresa, pais, chunk, idx in tareas
            }
            
            # Procesar resultados a medida que completan
            for future in as_completed(futures):
                if self.stop_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                empresa, pais = futures[future]
                try:
                    encontrados = future.result()
                    tareas_completadas += 1
                    
                    # Reportar progreso cada 5%
                    progreso = (tareas_completadas / total_tareas) * 100
                    if progreso - ultimo_reporte >= 5:
                        with self.stats_lock:
                            self.log_callback(
                                f"📈 Progreso: {progreso:.0f}% | "
                                f"Requests: {self.total_requests}/{total_tareas} | "
                                f"Contactos únicos: {self.total_encontrados}"
                            )
                        ultimo_reporte = progreso
                    
                except Exception as e:
                    self.log_callback(f"❌ Error en {empresa} - {pais}: {str(e)}")
        
        # Reporte final
        self.log_callback(f"\n{'='*60}")
        self.log_callback(f"✅ PROCESO COMPLETADO")
        self.log_callback(f"{'='*60}")
        self.log_callback(f"📊 Total requests realizados: {self.total_requests}")
        self.log_callback(f"👥 Total contactos únicos encontrados: {self.total_encontrados}")
        self.log_callback(f"📁 Archivo generado: {self.output_file}")
        self.log_callback(f"{'='*60}\n")
        
        return self.output_file if self.total_encontrados > 0 else None


def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Función principal compatible con la interfaz existente
    
    Parámetros:
    - max_workers: ajusta según tu plan de Apollo
        * Plan básico: 3-5 workers
        * Plan profesional: 10-15 workers  
        * Plan enterprise: 20+ workers
    """
    scraper = ApolloScraper(api_key, output_folder, log_callback, stop_event)
    
    # AJUSTA max_workers según tu plan de Apollo para evitar rate limits
    # Valores recomendados: 5 (conservador), 10 (balanceado), 15 (agresivo)
    return scraper.ejecutar_busqueda(empresas, cargos, paises, max_workers=10)
