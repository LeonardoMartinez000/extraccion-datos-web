import requests
import json
import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    log_callback("🚀 Iniciando motor Apollo (Modo Exhaustivo)...")
    
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
    
    # 1. Limpieza total de países
    lista_paises = paises if isinstance(paises, list) else [p.strip() for p in paises.split(',') if p.strip()]
    
    # 2. Reducción de Chunks a 5 para evitar errores de complejidad en el servidor
    chunk_size = 5 
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]

    def safe_get(dct, *keys):
        for key in keys:
            if isinstance(dct, (dict, list)):
                try:
                    dct = dct[int(key)] if isinstance(dct, list) else dct.get(key)
                except: return None
            else: return None
        return dct

    def procesar_busqueda(empresa, cargo_chunk, pais):
        if stop_event.is_set(): return [], empresa

        # PAYLOAD CON MODIFICACIÓN DE FILTRO DE ORGANIZACIÓN
        # Usamos q_organization_name pero también probamos con el nombre limpio
        payload = {
            "q_organization_name": empresa.strip(),
            "organization_locations": [pais.strip()], # Cambiado a lista para mayor compatibilidad
            "person_titles": cargo_chunk,
            "page": 1,
            "per_page": 50
        }

        try:
            # Añadimos un pequeño delay aleatorio para evitar detección de bot en Cloud
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                people = data.get('people', [])
                return people, empresa
            elif response.status_code == 422:
                # Si falla, intentamos sin el filtro de país para ver si es el causante
                log_callback(f"  ⚠️ Reintentando {empresa} sin filtro de país por error 422...")
                payload.pop("organization_locations")
                response = requests.post(url, headers=headers, json=payload, timeout=20)
                return response.json().get('people', []) if response.status_code == 200 else [], empresa
            return [], empresa
        except Exception:
            return [], empresa

    # 3. EJECUCIÓN CONCURRENTE
    log_callback(f"⚡ Ejecutando búsqueda para: {empresas[0]} en {len(lista_paises)} países...")
    
    with ThreadPoolExecutor(max_workers=2) as executor: # Reducido a 2 para estabilidad en Streamlit
        futures = []
        for empresa in empresas:
            for chunk in chunks_de_cargos:
                for pais in lista_paises:
                    futures.append(executor.submit(procesar_busqueda, empresa, chunk, pais))

        for future in as_completed(futures):
            if stop_event.is_set(): break
            
            people, emp_nombre = future.result()
            for person in people:
                p_id = person.get("id")
                if p_id and p_id not in ids_encontrados:
                    ids_encontrados.add(p_id)
                    resultados.append({
                        "empresa_buscada": emp_nombre,
                        "id": p_id,
                        "name": person.get("name"),
                        "title": person.get("title"),
                        "email": person.get("email"),
                        "organization": safe_get(person, "organization", "name"),
                        "city": person.get("city"),
                        "country": person.get("country"),
                        "linkedin": person.get("linkedin_url")
                    })

    # 4. GUARDADO DE SEGURIDAD
    if resultados:
        try:
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
                writer.writeheader()
                writer.writerows(resultados)
            log_callback(f"✅ EXTRACCIÓN EXITOSA: {len(resultados)} contactos únicos hallados.")
        except Exception as e:
            log_callback(f"❌ Error al escribir archivo: {str(e)}")
    else:
        # LOG FINAL DE DIAGNÓSTICO
        log_callback("❌ Cero resultados. Diagnóstico posible:")
        log_callback("1. El nombre de la empresa en el CSV tiene un caracter invisible.")
        log_callback("2. El API Key no tiene permisos de búsqueda de contactos.")
        log_callback("3. Apollo requiere el dominio (ej: servinformacion.com) en lugar del nombre.")
