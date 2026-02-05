import requests
import json
import csv
import os
import io # Para manejo de archivos en memoria si fuera necesario
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Versión optimizada para Streamlit Cloud.
    """
    log_callback("🚀 Iniciando motor Apollo en entorno Cloud...")
    
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
    
    # AJUSTE PARA PARIDAD CON POSTMAN
    # Extraemos el país como string simple si solo hay uno seleccionado
    ubicacion_query = paises[0] if isinstance(paises, list) and len(paises) > 0 else paises

    # Fragmentación de cargos (chunks)
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

        # Payload idéntico a tu validación en Postman
        payload = {
            "q_organization_name": empresa.strip(),
            "organization_locations": ubicacion_query, 
            "person_titles": chunk_cargos,             
            "page": 1,
            "per_page": 50
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                data = response.json()
                return data.get('people', []), empresa
            else:
                return [], empresa
        except Exception as e:
            return [], empresa

    # Ejecución concurrente controlada (Streamlit Cloud tiene límites de memoria)
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
                        "empresa": emp_nombre,
                        "id": p_id,
                        "nombre": person.get("name"),
                        "cargo": person.get("title"),
                        "email": person.get("email"),
                        "linkedin": person.get("linkedin_url"),
                        "organizacion": safe_get(person, "organization", "name"),
                        "pais": person.get("country")
                    })

    # Guardado de resultados
    if resultados:
        # En la web, asegúrate de que output_folder sea una ruta válida en el contenedor
        try:
            with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
                writer.writeheader()
                writer.writerows(resultados)
            log_callback(f"✅ Proceso finalizado. {len(resultados)} contactos únicos hallados.")
        except Exception as e:
            log_callback(f"❌ Error al escribir archivo: {str(e)}")
    else:
        log_callback("⚠️ No se encontraron resultados. Revisa los filtros aplicados.")
