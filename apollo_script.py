import requests
import json
import csv
import os
import re
import time

def limpiar_texto(texto):
    if texto is None or not isinstance(texto, str):
        return texto if texto is not None else ""
    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ]', '', texto)
    texto = ' '.join(texto.split())
    return texto.strip()

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    log_callback("🚀 Iniciando búsqueda detallada por Empresa y País...")
    
    url = "https://api.apollo.io/api/v1/contacts/search"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'x-api-key': api_key
    }
    
    output_file = os.path.join(output_folder, "resultados_apollo.csv")
    if os.path.exists(output_file):
        try: os.remove(output_file)
        except: pass

    resultados = []
    ids_encontrados = set()
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

    # Fragmentación de cargos en lotes de 10
    chunk_size = 10 
    chunks_de_cargos = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    
    request_delay = 0.8 # Optimizado para fluidez

    for empresa in empresas:
        if stop_event.is_set(): break
        empresa_clean = empresa.strip()
        log_callback(f"🏢 Empresa: {empresa_clean}")

        # NUEVO: Bucle para recorrer país por país y mostrarlo en consola
        for pais in paises:
            if stop_event.is_set(): break
            log_callback(f"   🌎 País: {pais}")
            encuentros_pais = 0

            for i, chunk in enumerate(chunks_de_cargos):
                if stop_event.is_set(): break
                
                payload = {
                    "q_organization_name": empresa_clean,
                    "organization_locations": [pais], # Buscamos específicamente este país
                    "person_titles": chunk,
                    "page": 1,
                    "per_page": 100
                }
                
                success = False
                retry_count = 0
                
                while retry_count < 3 and not success:
                    try:
                        response = requests.post(url, headers=headers, json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            contacts = data.get('contacts', [])
                            nuevos_lote = 0
                            
                            for person in contacts:
                                p_id = person.get("id")
                                if p_id and p_id not in ids_encontrados:
                                    ids_encontrados.add(p_id)
                                    nuevos_lote += 1
                                    resultados.append({
                                        "empresa_buscada": limpiar_texto(empresa_clean),
                                        "origen": "contacts_api",
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
                            
                            encuentros_pais += nuevos_lote
                            # Solo mostrar log si realmente encontró algo en ese lote para no saturar la consola
                            if nuevos_lote > 0:
                                log_callback(f"      -> Lote {i+1}: ✅ {nuevos_lote} encontrados")
                            
                            success = True
                            time.sleep(request_delay)
                        
                        elif response.status_code == 429:
                            retry_count += 1
                            time.sleep(5 * retry_count)
                        else:
                            break
                    except:
                        break
            
            if encuentros_pais > 0:
                log_callback(f"   📍 Subtotal {pais}: {encuentros_pais} contactos.")

    # Guardado final
    if resultados:
        with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(resultados)
        log_callback(f"\n✅ Finalizado. Total registros únicos: {len(resultados)}")
        return output_file
    return None
