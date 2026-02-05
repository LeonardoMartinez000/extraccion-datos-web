import requests
import json
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    log_callback("🚀 Iniciando motor Apollo (Modo Multi-País)...")
    
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
    
    # 1. Aseguramos que 'paises' sea una lista limpia
    lista_paises = paises if isinstance(paises, list) else [p.strip() for p in paises.split(',')]
    
    # 2. Fragmentamos cargos (chunks de 10 para evitar saturar el filtro)
    chunk_size = 10
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

        # REPLICA EXACTA DE TU POSTMAN: "organization_locations" como STRING
        payload = {
            "q_organization_name": empresa.strip(),
            "organization_locations": pais, # Enviamos uno por uno
            "person_titles": cargo_chunk,
            "page": 1,
            "per_page": 50
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                data = response.json()
                return data.get('people', []), empresa
            return [], empresa
        except Exception:
            return [], empresa

    # 3. EJECUCIÓN CONCURRENTE: Empresa x Cargos x País
    log_callback(f"⚡ Ejecutando búsquedas cruzadas ({len(lista_paises)} países detectados)...")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
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
                        "country": person.get("country")
                    })

    # 4. GUARDADO
    if resultados:
        try:
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
                writer.writeheader()
                writer.writerows(resultados)
            log_callback(f"✅ EXTRACCIÓN EXITOSA: {len(resultados)} contactos únicos hallados.")
        except Exception as e:
            log_callback(f"❌ Error al guardar archivo: {str(e)}")
    else:
        log_callback("⚠️ No se encontraron resultados. Intenta reducir la cantidad de cargos o revisar el nombre de la empresa.")
