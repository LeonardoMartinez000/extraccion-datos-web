import requests
import json
import csv
import os

# --- CAMBIO: Aceptar el 'stop_event' como argumento ---
def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Ejecuta el proceso de extracción de Apollo.
    """
    log_callback("🚀 Iniciando búsqueda de contactos en Apollo...")
    
    #url = "https://api.apollo.io/api/v1/mixed_people/search"
    url = "https://api.apollo.io/api/v1/mixed_people/api_search"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'x-api-key': api_key
    }
    output_file = os.path.join(output_folder, "resultados_apollo.csv")
    
    resultados = []
    campos = [
        "empresa_buscada", "origen", "id", "first_name", "last_name", "name", "linkedin_url", "title", "headline",
        "email_status", "email", "state", "city", "country", "organization_name", "organization_id", "raw_number",
        "sanitized_number", "contact_email"
    ]

    # --- NUEVO: Set para controlar IDs de personas ya encontradas y evitar duplicados ---
    ids_encontrados = set()

    def safe_get(dct, *keys):
        for key in keys:
            if isinstance(dct, list):
                try:
                    dct = dct[key]
                except (IndexError, TypeError):
                    return None
            elif isinstance(dct, dict):
                dct = dct.get(key)
            else:
                return None
                
            if dct is None: return None
        return dct

    # --- NUEVO: Dividir la lista de cargos en lotes (chunks) ---
    # La API de Apollo tiene un límite de filtros. 10 es un número seguro.
    chunk_size = 10 
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    log_callback(f"ℹ️ Dividiendo {len(cargos)} cargos en {len(chunks_de_cargos)} búsquedas por empresa (de {chunk_size} cargos cada una).")


    for empresa in empresas:
        # --- CAMBIO: Chequear cancelación antes de cada empresa ---
        if stop_event.is_set():
            log_callback("🛑 Proceso cancelado por el usuario.")
            break

        log_callback(f"\n🔎 Buscando en Apollo: {empresa}...")

        # --- NUEVO: Bucle interno para iterar sobre los lotes de cargos ---
        for i, chunk in enumerate(chunks_de_cargos):
            
            # Chequear cancelación antes de cada lote
            if stop_event.is_set():
                log_callback("🛑 Proceso cancelado por el usuario.")
                break
            
            # Mostramos solo los 3 primeros cargos del lote para no saturar la consola
            log_callback(f"  -> Lote {i+1}/{len(chunks_de_cargos)} (Cargos: {', '.join(chunk[:3])}...)")

            payload = {
                "q_organization_name": empresa,
                "person_titles": chunk,  # <-- CAMBIO: Usar el 'chunk' en lugar de la lista completa 'cargos'
                "organization_locations": paises,
                "page": 1,
                "per_page": 25 # 40 es un valor aceptable
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    people = data.get('people', [])
                    log_callback(f"    -> Se encontraron {len(people)} contactos en este lote.")
                    
                    for person in people:
                        
                        person_id = person.get("id")
                        
                        # --- NUEVO: Control de duplicados ---
                        if person_id and person_id not in ids_encontrados:
                            # Añadir el ID al set para no volver a agregarlo
                            ids_encontrados.add(person_id)
                            
                            # Añadir el resultado
                            resultados.append({
                                "empresa_buscada": empresa, "origen": "people",
                                "id": person_id, "first_name": person.get("first_name"),
                                "last_name": person.get("last_name"), "name": person.get("name"),
                                "linkedin_url": person.get("linkedin_url"), "title": person.get("title"),
                                "headline": person.get("headline"), "email_status": person.get("email_status"),
                                "email": person.get("email"), "state": person.get("state"),
                                "city": person.get("city"), "country": person.get("country"),
                                "organization_name": safe_get(person, "organization", "name"),
                                "organization_id": safe_get(person, "organization", "id"),
                                "raw_number": safe_get(person, "phone_numbers", 0, "raw_number"),
                                "sanitized_number": safe_get(person, "phone_numbers", 0, "sanitized_number"),
                                "contact_email": person.get("contact_email")
                            })
                        elif not person_id:
                             # Si no tiene ID (raro), no podemos chequear duplicados, lo agregamos
                             resultados.append({
                                "empresa_buscada": empresa, "origen": "people",
                                "id": None, "first_name": person.get("first_name"),
                                # ... (resto de campos) ...
                                "organization_name": safe_get(person, "organization", "name"),
                                "organization_id": safe_get(person, "organization", "id"),
                                "raw_number": safe_get(person, "phone_numbers", 0, "raw_number"),
                                "sanitized_number": safe_get(person, "phone_numbers", 0, "sanitized_number"),
                                "contact_email": person.get("contact_email")
                             })
                             
                elif response.status_code == 422:
                     # Si el error 422 persiste, es por otra razón (quizás 'chunk_size' sigue siendo muy grande)
                     log_callback(f"    -> ❌ Error 422 en lote: {response.text}. Prueba reducir el 'chunk_size' en el script.")
                else:
                    log_callback(f"    -> ❌ Error al buscar en lote: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                log_callback(f"    -> ❌ Error de conexión: {e}")
        
        # Fin del bucle de lotes (chunks)
    # Fin del bucle de empresas

    # Escribir resultados al final
    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(resultados)
        
        if stop_event.is_set():
            log_callback(f"\n🚫 Proceso de Apollo cancelado. Se guardaron {len(resultados)} resultados parciales en '{os.path.basename(output_file)}'.")
        else:
            log_callback(f"\n✅ Proceso de Apollo completado. Se encontraron {len(resultados)} contactos únicos. Revisa el archivo '{os.path.basename(output_file)}'.")
            
    except IOError as e:
        log_callback(f"❌ ERROR FATAL: No se pudo escribir en el archivo de salida. Causa: {e}")