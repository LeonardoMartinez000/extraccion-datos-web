import requests
import json
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Versión optimizada de extracción de Apollo con alto rendimiento.
    """
    log_callback("🚀 Iniciando motor de extracción optimizado para Apollo...")
    
    url = "https://api.apollo.io/api/v1/contacts/search"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'x-api-key': api_key
    }
    
    output_file = os.path.join(output_folder, "resultados_apollo.csv")
    resultados = []
    ids_encontrados = set()
    
    # --- CONFIGURACIÓN DE RENDIMIENTO ---
    # Dividimos cargos en bloques según el límite de la API (generalmente 10-15)
    chunk_size = 10
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    
    # Aseguramos que los países sean una lista (formato exacto de Postman)
    lista_paises = paises if isinstance(paises, list) else [paises]

    def safe_get(dct, *keys):
        for key in keys:
            if isinstance(dct, (dict, list)):
                try:
                    if isinstance(dct, list):
                        dct = dct[int(key)]
                    else:
                        dct = dct.get(key)
                except (IndexError, TypeError, KeyError, ValueError):
                    return None
            else:
                return None
            if dct is None: return None
        return dct

    def procesar_busqueda(empresa, chunk_cargos):
        """Función interna para realizar una sola petición API"""
        if stop_event.is_set():
            return []

        payload = {
            "q_organization_name": empresa.strip(),
            "organization_locations": lista_paises, # Coincide con tu Postman
            "person_titles": chunk_cargos,         # Coincide con tu Postman
            "page": 1,
            "per_page": 50
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                data = response.json()
                return data.get('people', []), empresa
            elif response.status_code == 429:
                log_callback(f"⚠️ Rate limit excedido para {empresa}. Reintentando...")
                return [], empresa
            else:
                return [], empresa
        except Exception as e:
            log_callback(f"❌ Error en petición ({empresa}): {str(e)}")
            return [], empresa

    # --- EJECUCIÓN CONCURRENTE (MÁXIMO RENDIMIENTO) ---
    # Usamos ThreadPoolExecutor para lanzar múltiples peticiones al mismo tiempo
    log_callback(f"⚡ Ejecutando búsquedas concurrentes para {len(empresas)} empresas...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for empresa in empresas:
            for chunk in chunks_de_cargos:
                futures.append(executor.submit(procesar_busqueda, empresa, chunk))

        for future in as_completed(futures):
            if stop_event.is_set():
                break
            
            people, emp_nombre = future.result()
            
            for person in people:
                p_id = person.get("id")
                if p_id and p_id not in ids_encontrados:
                    ids_encontrados.add(p_id)
                    resultados.append({
                        "empresa_buscada": emp_nombre,
                        "id": p_id,
                        "name": person.get("name"),
                        "first_name": person.get("first_name"),
                        "last_name": person.get("last_name"),
                        "title": person.get("title"),
                        "email": person.get("email"),
                        "email_status": person.get("email_status"),
                        "linkedin_url": person.get("linkedin_url"),
                        "country": person.get("country"),
                        "city": person.get("city"),
                        "organization_name": safe_get(person, "organization", "name"),
                        "raw_number": safe_get(person, "phone_numbers", 0, "raw_number"),
                        "contact_email": person.get("contact_email")
                    })

    # --- ESCRITURA DE RESULTADOS ---
    if resultados:
        campos = resultados[0].keys()
        try:
            # Usamos utf-8-sig para que Excel lo abra correctamente con tildes
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(resultados)
            log_callback(f"✅ ÉXITO: {len(resultados)} contactos únicos guardados en {os.path.basename(output_file)}")
        except Exception as e:
            log_callback(f"❌ ERROR al guardar CSV: {str(e)}")
    else:
        log_callback("⚠️ No se encontraron resultados con los criterios proporcionados.")
