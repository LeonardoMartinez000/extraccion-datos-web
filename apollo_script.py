import requests
import json
import csv
import os
import re

def limpiar_texto(texto):
    """
    Limpia el texto eliminando saltos de línea, emojis y caracteres especiales,
    preservando tildes, eñes y puntuación básica.
    """
    if texto is None or not isinstance(texto, str):
        return texto if texto is not None else ""
    
    # 1. Reemplazar saltos de línea y tabulaciones por un espacio simple
    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # 2. Mantener solo caracteres ASCII imprimibles y caracteres latinos (tildes/ñ)
    # Rango \x20-\x7E incluye letras, números y símbolos estándar.
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ]', '', texto)
    
    # 3. Eliminar espacios múltiples y espacios en los extremos
    texto = ' '.join(texto.split())
    
    return texto.strip()

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Ejecuta la extracción de contactos de Apollo con limpieza de datos.
    """
    log_callback("🚀 Iniciando búsqueda de contactos con limpieza de caracteres...")
    
    url = "https://api.apollo.io/api/v1/contacts/search"
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

    ids_encontrados = set()

    def safe_get(dct, *keys):
        for key in keys:
            if isinstance(dct, list):
                try: dct = dct[key]
                except: return None
            elif isinstance(dct, dict):
                dct = dct.get(key)
            else: return None
            if dct is None: return None
        return dct

    # Configuración de ubicación (String simple para máxima compatibilidad)
    ubicacion_query = paises[0] if isinstance(paises, list) and len(paises) == 1 else paises
    
    # Fragmentación de cargos en lotes de 10
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
                    contacts = data.get('contacts', []) # Usamos 'contacts' según validación Postman
                    
                    for person in contacts:
                        person_id = person.get("id")
                        
                        if person_id and person_id not in ids_encontrados:
                            ids_encontrados.add(person_id)
                            
                            # Construcción del registro con limpieza aplicada
                            resultados.append({
                                "empresa_buscada": limpiar_texto(empresa),
                                "origen": "contacts_api",
                                "id": person_id,
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
                                "organization_name": limpiar_texto(safe_get(person, "organization", "name")),
                                "organization_id": safe_get(person, "organization", "id"),
                                "raw_number": limpiar_texto(safe_get(person, "phone_numbers", 0, "raw_number")),
                                "sanitized_number": limpiar_texto(safe_get(person, "phone_numbers", 0, "sanitized_number")),
                                "contact_email": person.get("contact_email")
                            })
                else:
                    log_callback(f"  ⚠️ Error {response.status_code} en lote {i+1}")

            except Exception as e:
                log_callback(f"  ❌ Error de conexión: {str(e)}")

    # Guardado final en CSV
    try:
        if resultados:
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(resultados)
            log_callback(f"✅ Proceso completado. {len(resultados)} contactos únicos guardados.")
        else:
            log_callback("⚠️ No se encontraron resultados para los criterios ingresados.")
    except Exception as e:
        log_callback(f"❌ ERROR al guardar el archivo: {e}")
