import requests
import json
import csv
import os

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Versión adaptada para la Web que mantiene la lógica probada de escritorio.
    """
    log_callback("🚀 Iniciando búsqueda de contactos en Apollo (Modo Web)...")
    
    # URL validada por el usuario
    url = "https://api.apollo.io/api/v1/contacts/search"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'x-api-key': api_key
    }
    
    # Definición de ruta de salida
    output_file = os.path.join(output_folder, "resultados_apollo.csv")
    
    resultados = []
    campos = [
        "empresa_buscada", "origen", "id", "first_name", "last_name", "name", "linkedin_url", "title", "headline",
        "email_status", "email", "state", "city", "country", "organization_name", "organization_id", "raw_number",
        "sanitized_number", "contact_email"
    ]

    ids_encontrados = set()

    # Función auxiliar para extracción segura de JSON anidado
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

    # Manejo de países: Apollo API prefiere strings o listas según el endpoint.
    # Forzamos a que sea un string plano si es un solo país para máxima compatibilidad.
    ubicacion_query = paises[0] if isinstance(paises, list) and len(paises) == 1 else paises

    # Fragmentación de cargos (chunks de 10)
    chunk_size = 10 
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    
    log_callback(f"ℹ️ Procesando {len(empresas)} empresas con {len(chunks_de_cargos)} bloques de cargos.")

    for empresa in empresas:
        if stop_event.is_set():
            log_callback("🛑 Proceso cancelado por el usuario.")
            break

        log_callback(f"🔎 Buscando en Apollo: {empresa.strip()}...")

        for i, chunk in enumerate(chunks_de_cargos):
            if stop_event.is_set(): break
            
            # Payload idéntico al probado en Postman/Escritorio
            payload = {
                "q_organization_name": empresa.strip(),
                "organization_locations": ubicacion_query,
                "person_titles": chunk,
                "page": 1,
                "per_page": 50 
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    people = data.get('people', [])
                    log_callback(f"  -> Lote {i+1}: {len(people)} contactos encontrados.")
                    
                    for person in people:
                        person_id = person.get("id")
                        
                        if person_id and person_id not in ids_encontrados:
                            ids_encontrados.add(person_id)
                            
                            resultados.append({
                                "empresa_buscada": empresa.strip(),
                                "origen": "people",
                                "id": person_id,
                                "first_name": person.get("first_name"),
                                "last_name": person.get("last_name"),
                                "name": person.get("name"),
                                "linkedin_url": person.get("linkedin_url"),
                                "title": person.get("title"),
                                "headline": person.get("headline"),
                                "email_status": person.get("email_status"),
                                "email": person.get("email"),
                                "state": person.get("state"),
                                "city": person.get("city"),
                                "country": person.get("country"),
                                "organization_name": safe_get(person, "organization", "name"),
                                "organization_id": safe_get(person, "organization", "id"),
                                "raw_number": safe_get(person, "phone_numbers", 0, "raw_number"),
                                "sanitized_number": safe_get(person, "phone_numbers", 0, "sanitized_number"),
                                "contact_email": person.get("contact_email")
                            })
                else:
                    log_callback(f"  ⚠️ Error {response.status_code}: {response.text[:100]}")

            except requests.exceptions.RequestException as e:
                log_callback(f"  ❌ Error de conexión: {e}")

    # Escritura final de resultados con compatibilidad Excel (UTF-8-SIG)
    try:
        if resultados:
            # Importante: 'utf-8-sig' para que Excel en la web abra bien las tildes
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(resultados)
            
            log_callback(f"✅ Proceso completado. {len(resultados)} contactos únicos en '{os.path.basename(output_file)}'.")
        else:
            log_callback("⚠️ El proceso terminó sin encontrar resultados.")
            
    except Exception as e:
        log_callback(f"❌ ERROR FATAL al guardar archivo: {e}")
