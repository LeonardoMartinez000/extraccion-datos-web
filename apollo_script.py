import requests
import json
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    log_callback("🚀 Iniciando motor Apollo (Búsqueda por Dominio/Nombre)...")
    
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
    
    # 1. Limpieza de Países
    lista_paises = paises if isinstance(paises, list) else [p.strip() for p in paises.split(',') if p.strip()]
    
    # 2. Bloques de cargos pequeños (máxima efectividad)
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

        empresa_clean = empresa.strip().lower()
        
        # PAYLOAD OPTIMIZADO: 
        # Si el dato tiene un "." (punto), lo tratamos como dominio, si no, como nombre.
        payload = {
            "person_titles": cargo_chunk,
            "location_countries": [pais.strip()],
            "page": 1,
            "per_page": 50
        }
        
        if "." in empresa_clean:
            payload["q_organization_domains"] = empresa_clean
        else:
            payload["q_organization_name"] = empresa_clean

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json().get('people', []), empresa
            return [], empresa
        except Exception:
            return [], empresa

    # 3. EJECUCIÓN CONCURRENTE
    log_callback(f"⚡ Consultando {len(empresas)} entidades en {len(lista_paises)} países...")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
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
                        "nombre": person.get("name"),
                        "cargo": person.get("title"),
                        "email": person.get("email"),
                        "linkedin": person.get("linkedin_url"),
                        "organizacion": safe_get(person, "organization", "name"),
                        "pais": person.get("country")
                    })

    # 4. GUARDADO
    if resultados:
        try:
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
                writer.writeheader()
                writer.writerows(resultados)
            log_callback(f"✅ EXTRACCIÓN EXITOSA: {len(resultados)} contactos únicos.")
        except Exception as e:
            log_callback(f"❌ Error al guardar CSV: {str(e)}")
    else:
        log_callback("⚠️ Cero resultados. Acción recomendada: Usa el dominio (ej: google.com) en tu archivo CSV.")
