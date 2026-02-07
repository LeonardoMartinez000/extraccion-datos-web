import requests
import json
import csv
import os
import re
import time

def limpiar_texto(texto):
    """
    Limpia el texto eliminando saltos de línea, emojis y caracteres especiales.
    """
    if texto is None or not isinstance(texto, str):
        return texto if texto is not None else ""
    
    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ]', '', texto)
    texto = ' '.join(texto.split())
    
    return texto.strip()

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Versión Optimizada: Mayor rendimiento y limpieza de archivos residuales.
    """
    log_callback("🚀 Iniciando Apollo Contactos (Motor Optimizado)...")
    
    # 1. LIMPIEZA INICIAL: Evita arrastrar datos de ejecuciones anteriores
    output_file = os.path.join(output_folder, "resultados_apollo.csv")
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except:
            pass

    resultados = []
    ids_encontrados = set()
    url = "https://api.apollo.io/api/v1/contacts/search"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'x-api-key': api_key
    }
    
    campos = [
        "empresa_buscada", "origen", "id", "first_name", "last_name", "name", "linkedin_url", "title", "headline",
        "email_status", "email", "state", "city", "country", "organization_name", "organization_id", "raw_number",
        "sanitized_number", "contact_email"
    ]

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

    # Validación de entradas
    if not cargos or not empresas or not paises:
        log_callback("❌ ERROR: Faltan parámetros (cargos, empresas o países).")
        return

    # Lógica de ubicación
    ubicacion_query = paises[0] if len(paises) == 1 else paises
    
    # Fragmentación de cargos (Lotes de 10 para evitar Error 422)
    chunk_size = 10 
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    
    # Variables de control
    request_delay = 0.8  # Optimización: Delay reducido para mayor velocidad
    
    for empresa in empresas:
        if stop_event.is_set(): break
        empresa_clean = empresa.strip()
        log_callback(f"\n🔎 Buscando: {empresa_clean}...")

        for i, chunk in enumerate(chunks_de_cargos):
            if stop_event.is_set(): break
            
            payload = {
                "q_organization_name": empresa_clean,
                "organization_locations": ubicacion_query,
                "person_titles": chunk,
                "page": 1,
                "per_page": 100 # Optimización: Pedimos 100 de una vez en lugar de 50
            }
            
            success = False
            retries = 0
            while retries < 3 and not success:
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=25)
                    
                    if response.status_code == 200:
                        data = response.json()
                        contacts = data.get('contacts', [])
                        
                        for person in contacts:
                            p_id = person.get("id")
                            if p_id and p_id not in ids_encontrados:
                                ids_encontrados.add(p_id)
                                resultados.append({
                                    "empresa_buscada": limpiar_texto(empresa_clean),
                                    "origen": "apollo_api",
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
                                    "organization_name": limpiar_texto(safe_get(person, "organization", "name")),
                                    "organization_id": safe_get(person, "organization", "id"),
                                    "raw_number": limpiar_texto(safe_get(person, "phone_numbers", 0, "raw_number")),
                                    "sanitized_number": limpiar_texto(safe_get(person, "phone_numbers", 0, "sanitized_number")),
                                    "contact_email": person.get("contact_email")
                                })
                        
                        log_callback(f"  -> Lote {i+1}/{len(chunks_de_cargos)}: ✅ {len(contacts)} encontrados.")
                        success = True
                        time.sleep(request_delay)

                    elif response.status_code == 429:
                        wait = 10 * (retries + 1)
                        log_callback(f"  -> ⚠️ Rate limit. Esperando {wait}s...")
                        time.sleep(wait)
                        retries += 1
                    else:
                        log_callback(f"  -> ⚠️ Error {response.status_code}. Saltando lote.")
                        break
                except Exception as e:
                    log_callback(f"  -> ❌ Error conexión: {str(e)}")
                    break

    # Escritura de resultados (Solo si hay datos)
    if resultados:
        try:
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(resultados)
            log_callback(f"\n✅ Finalizado. {len(resultados)} registros únicos extraídos.")
        except Exception as e:
            log_callback(f"❌ Error al guardar CSV: {e}")
    else:
        log_callback("\n⚠️ No se halló información. No se generó archivo nuevo.")
