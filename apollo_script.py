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
    # Rango \x20-\x7E incluye letras, números y símbolos estándar.
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ]', '', texto)
    
    # 3. Eliminar espacios múltiples y espacios en los extremos
    texto = ' '.join(texto.split())
    
    return texto.strip()

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Ejecuta la extracción de contactos de Apollo con limpieza de datos.
    Incluye protección contra Error 429 y retry automático.
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

    # ===== NUEVO: Validación de datos =====
    if not cargos:
        log_callback("❌ ERROR: La lista de cargos está vacía.")
        return
    
    if not empresas:
        log_callback("❌ ERROR: La lista de empresas está vacía.")
        return
    
    if not paises:
        log_callback("❌ ERROR: No se seleccionaron países.")
        return

    log_callback(f"📊 Datos validados:")
    log_callback(f"   - Empresas: {len(empresas)}")
    log_callback(f"   - Cargos: {len(cargos)}")
    log_callback(f"   - Países: {len(paises)}")

    # Configuración de ubicación (String simple para máxima compatibilidad)
    ubicacion_query = paises[0] if isinstance(paises, list) and len(paises) == 1 else paises
    
    # Fragmentación de cargos en lotes de 10
    chunk_size = 10 
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    
    log_callback(f"ℹ️ Procesando {len(empresas)} empresas con {len(chunks_de_cargos)} bloques de cargos.")

    # ===== NUEVO: Variables para control de rate limiting =====
    consecutive_429_errors = 0
    max_429_errors = 3  # Máximo de errores 429 consecutivos antes de pausar más tiempo
    base_retry_delay = 5  # Segundos base de espera
    request_delay = 1.5  # Delay entre requests normales (AUMENTADO)

    for empresa in empresas:
        if stop_event.is_set():
            log_callback("🛑 Proceso cancelado por el usuario.")
            break

        log_callback(f"\n🔎 Buscando en Apollo: {empresa.strip()}...")

        for i, chunk in enumerate(chunks_de_cargos):
            if stop_event.is_set():
                log_callback("🛑 Proceso cancelado por el usuario.")
                break
            
            log_callback(f"  -> Lote {i+1}/{len(chunks_de_cargos)} (Cargos: {', '.join(chunk[:3])}{'...' if len(chunk) > 3 else ''})")
            
            payload = {
                "q_organization_name": empresa.strip(),
                "organization_locations": ubicacion_query,
                "person_titles": chunk,
                "page": 1,
                "per_page": 50 
            }
            
            # ===== NUEVO: Retry logic con backoff exponencial =====
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        contacts = data.get('contacts', [])  # Usamos 'contacts' según validación Postman
                        
                        log_callback(f"    -> ✅ {len(contacts)} contactos encontrados.")
                        
                        # ===== NUEVO: Reset contador de errores 429 si la request fue exitosa =====
                        consecutive_429_errors = 0
                        
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
                        
                        success = True
                        
                        # ===== NUEVO: Delay normal entre requests =====
                        time.sleep(request_delay)
                    
                    # ===== NUEVO: Manejo específico de Error 429 =====
                    elif response.status_code == 429:
                        consecutive_429_errors += 1
                        retry_count += 1
                        
                        # Backoff exponencial: 5s, 10s, 20s
                        retry_delay = base_retry_delay * (2 ** (retry_count - 1))
                        
                        # Si hay muchos errores 429 consecutivos, aumentar el delay
                        if consecutive_429_errors >= max_429_errors:
                            retry_delay = 30  # Esperar 30 segundos
                            log_callback(f"    -> ⚠️ Múltiples errores 429. Esperando {retry_delay}s antes de reintentar...")
                        else:
                            log_callback(f"    -> ⚠️ Error 429 (Rate Limit). Intento {retry_count}/{max_retries}. Esperando {retry_delay}s...")
                        
                        time.sleep(retry_delay)
                        
                        if retry_count >= max_retries:
                            log_callback(f"    -> ❌ Máximo de reintentos alcanzado. Continuando con siguiente lote...")
                    
                    # ===== NUEVO: Manejo de otros errores HTTP =====
                    elif response.status_code == 422:
                        log_callback(f"    -> ❌ Error 422: {response.text}")
                        log_callback(f"    -> Intenta reducir el número de cargos por lote")
                        break  # No reintentar en error 422
                        
                    elif response.status_code == 401:
                        log_callback(f"    -> ❌ Error 401: API Key inválida o expirada")
                        return  # Detener todo el proceso
                    
                    else:
                        log_callback(f"    -> ⚠️ Error {response.status_code} en lote {i+1}")
                        log_callback(f"    -> Respuesta: {response.text[:200]}")
                        break  # No reintentar otros errores
                
                # ===== NUEVO: Manejo de timeout =====
                except requests.exceptions.Timeout:
                    retry_count += 1
                    log_callback(f"    -> ⏱️ Timeout. Reintentando ({retry_count}/{max_retries})...")
                    time.sleep(base_retry_delay)
                
                # ===== NUEVO: Manejo de otros errores de conexión =====
                except requests.exceptions.RequestException as e:
                    log_callback(f"    -> ❌ Error de conexión: {str(e)}")
                    break  # No reintentar errores de conexión
                
                except Exception as e:
                    log_callback(f"    -> ❌ Error inesperado: {str(e)}")
                    break

    # Guardado final en CSV
    try:
        if resultados:
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(resultados)
            
            if stop_event.is_set():
                log_callback(f"\n🚫 Proceso cancelado. {len(resultados)} contactos guardados.")
            else:
                log_callback(f"\n✅ Proceso completado exitosamente!")
                log_callback(f"   📊 Total de contactos únicos: {len(resultados)}")
                log_callback(f"   📁 Archivo: '{os.path.basename(output_file)}'")
        else:
            log_callback("\n⚠️ No se encontraron resultados para los criterios ingresados.")
    
    except Exception as e:
        log_callback(f"\n❌ ERROR al guardar el archivo: {e}")
