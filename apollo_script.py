import requests
import json
import csv
import os
import re
import time

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
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ]', '', texto)
    
    # 3. Eliminar espacios múltiples y espacios en los extremos
    texto = ' '.join(texto.split())
    
    return texto.strip()

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Ejecuta la extracción de contactos de Apollo con la estructura completa de campos.
    Actualiza la consola de Streamlit en tiempo real.
    """
    log_callback("🚀 Iniciando búsqueda de contactos con estructura completa...")
    
    url = "https://api.apollo.io/api/v1/contacts/search"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'x-api-key': api_key
    }
    
    output_file = os.path.join(output_folder, "resultados_apollo.csv")
    
    # LIMPIEZA INICIAL DEL ARCHIVO PREVIO
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except:
            pass

    resultados = []
    ids_encontrados = set()
    
    # ESTRUCTURA COMPLETA SOLICITADA
    campos = [
        "empresa_buscada", "origen", "id", "first_name", "last_name", "name", "linkedin_url", "title", "headline",
        "email_status", "email", "state", "city", "country", "organization_name", "organization_id", "raw_number",
        "sanitized_number", "contact_email"
    ]

    def safe_get(dct, *keys):
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

    # Validación de datos
    if not cargos or not empresas or not paises:
        log_callback("❌ ERROR: Faltan datos de entrada.")
        return

    log_callback(f"📊 Procesando: {len(empresas)} empresas | {len(cargos)} cargos.")

    ubicacion_query = paises[0] if isinstance(paises, list) and len(paises) == 1 else paises
    chunk_size = 10 
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    
    request_delay = 1.0  # Balance entre velocidad y seguridad

    for empresa in empresas:
        if stop_event.is_set():
            log_callback("🛑 Proceso cancelado por el usuario.")
            break

        empresa_clean = empresa.strip()
        log_callback(f"🔎 Buscando en Apollo: {empresa_clean}...")
        encuentros_empresa = 0

        for i, chunk in enumerate(chunks_de_cargos):
            if stop_event.is_set(): break
            
            payload = {
                "q_organization_name": empresa_clean,
                "organization_locations": ubicacion_query,
                "person_titles": chunk,
                "page": 1,
                "per_page": 100  # Máximo rendimiento por petición
            }
            
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        contacts = data.get('contacts', [])
                        nuevos_en_lote = 0
                        
                        for person in contacts:
                            person_id = person.get("id")
                            if person_id and person_id not in ids_encontrados:
                                ids_encontrados.add(person_id)
                                nuevos_en_lote += 1
                                
                                # MAPEO COMPLETO DE LA ESTRUCTURA ORIGINAL
                                resultados.append({
                                    "empresa_buscada": limpiar_texto(empresa_clean),
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
                        
                        encuentros_empresa += nuevos_en_lote
                        log_callback(f"   -> Lote {i+1}/{len(chunks_de_cargos)}: ✅ {nuevos_en_lote} contactos encontrados.")
                        success = True
                        time.sleep(request_delay)
                    
                    elif response.status_code == 429:
                        retry_count += 1
                        wait = 10 * retry_count
                        log_callback(f"   -> ⚠️ Rate Limit (429). Esperando {wait}s...")
                        time.sleep(wait)
                    else:
                        log_callback(f"   -> ⚠️ Error {response.status_code} en lote {i+1}. Saltando.")
                        break
                except Exception as e:
                    log_callback(f"   -> ❌ Error de conexión: {str(e)}")
                    break
        
        log_callback(f"📊 Total acumulado para {empresa_clean}: {encuentros_empresa}")

    # GUARDADO FINAL CON ESTRUCTURA COMPLETA
    try:
        if resultados:
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(resultados)
            
            log_callback(f"\n✅ Proceso finalizado. Total registros: {len(resultados)}")
            return output_file
        else:
            log_callback("\n⚠️ No se encontraron resultados.")
            return None
    except Exception as e:
        log_callback(f"\n❌ Error al guardar el archivo: {e}")
        return None
