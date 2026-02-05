import requests
import json
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Motor de extracción optimizado. Corrige inconsistencias de formato 
    y asegura paridad con los resultados de Postman.
    """
    log_callback("🚀 Iniciando motor de extracción optimizado para Apollo...")
    
    # URL validada en Postman
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
    # Apollo puede fallar con demasiados cargos. 10 es el estándar de oro.
    chunk_size = 10
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    
    # Aseguramos que los países sean una lista limpia (ej: ["Colombia"])
    # Si viene como string separado por comas, lo convertimos a lista
    if isinstance(paises, str):
        lista_paises = [p.strip() for p in paises.split(',') if p.strip()]
    else:
        lista_paises = [str(p).strip() for p in paises if p]

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
        if stop_event.is_set():
            return [], empresa

        # Payload ajustado para máxima compatibilidad con el endpoint v1
        payload = {
            "q_organization_name": empresa.strip(),
            "person_titles": chunk_cargos,
            "organization_locations": lista_paises, # Cambio a parámetro estándar
            "page": 1,
            "per_page": 50
        }

        try:
            # Timeout añadido para evitar que el script se cuelgue
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            
            if response.status_code == 200:
                data = response.json()
                found = data.get('people', [])
                if found:
                    log_callback(f"  ✅ {empresa}: {len(found)} contactos hallados.")
                return found, empresa
            else:
                # Log de error detallado para depuración
                log_callback(f"  ⚠️ {empresa}: Error {response.status_code} - {response.text[:100]}")
                return [], empresa
        except Exception as e:
            log_callback(f"  ❌ Error de red en {empresa}: {str(e)}")
            return [], empresa

    # --- EJECUCIÓN CONCURRENTE ---
    log_callback(f"⚡ Ejecutando {len(chunks_de_cargos)} bloques de búsqueda por empresa...")
    
    # workers=3 para evitar bloqueos por parte de Apollo al detectar tráfico inusual
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for empresa in empresas:
            for chunk in chunks_de_cargos:
                futures.append(executor.submit(procesar_busqueda, empresa, chunk))

        for future in as_completed(futures):
            if stop_event.is_set():
                executor.shutdown(wait=False)
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

    # --- GUARDADO FINAL ---
    if resultados:
        try:
            # utf-8-sig es CRUCIAL para que Excel reconozca tildes de Colombia/México
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
                writer.writeheader()
                writer.writerows(resultados)
            log_callback(f"✅ FINALIZADO: {len(resultados)} contactos guardados en CSV.")
        except Exception as e:
            log_callback(f"❌ Error al escribir CSV: {str(e)}")
    else:
        log_callback("❌ No se obtuvieron datos. Verifique los nombres de las empresas y países.")

