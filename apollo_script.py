import requests
import json
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Versión final con paridad total de Payload respecto a Postman.
    """
    log_callback("🚀 Iniciando extracción con validación de Payload Postman...")
    
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
    
    # --- AJUSTE CLAVE: Formato de Localización ---
    # Si 'paises' es una lista con un solo elemento, lo extraemos como string
    # para que sea "Colombia" y no ["Colombia"], tal como en tu Postman.
    valor_ubicacion = paises[0] if isinstance(paises, list) and len(paises) == 1 else paises
    if isinstance(valor_ubicacion, list):
        # Si son varios, los unimos por coma o enviamos la lista según soporte
        valor_ubicacion = ", ".join(valor_ubicacion)

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

    def procesar_busqueda(empresa, chunk_cargos):
        if stop_event.is_set(): return [], empresa

        # PAYLOAD IDÉNTICO A TU POSTMAN
        payload = {
            "q_organization_name": empresa.strip(),
            "organization_locations": valor_ubicacion, # Enviado como String
            "person_titles": chunk_cargos,             # Enviado como Lista
            "page": 1,
            "per_page": 50
        }

        try:
            # Mostramos el payload en el log para que lo confirmes
            log_callback(f"🔎 Consultando: {empresa.strip()} | Ubicación: {valor_ubicacion}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            
            if response.status_code == 200:
                data = response.json()
                people = data.get('people', [])
                return people, empresa
            else:
                log_callback(f"  ⚠️ Error {response.status_code} en {empresa}")
                return [], empresa
        except Exception as e:
            log_callback(f"  ❌ Error de conexión: {str(e)}")
            return [], empresa

    # --- EJECUCIÓN ---
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(procesar_busqueda, emp, chk): emp for emp in empresas for chk in chunks_de_cargos}

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

    if resultados:
        with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        log_callback(f"✅ Proceso terminado. {len(resultados)} contactos únicos guardados.")
    else:
        log_callback("⚠️ El servidor no retornó resultados. Revisa que el nombre de la empresa coincida con Apollo.")
