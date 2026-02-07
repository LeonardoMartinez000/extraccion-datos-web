import requests
import json
import csv
import os
import re
import time

def limpiar_texto(texto):
    if texto is None or not isinstance(texto, str): return ""
    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ]', '', texto)
    return ' '.join(texto.split()).strip()

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    log_callback("⚙️ Configurando motor de búsqueda...")
    
    output_file = os.path.join(output_folder, "resultados_apollo.csv")
    if not os.path.exists(output_folder): os.makedirs(output_folder)
    
    resultados = []
    ids_encontrados = set()
    url = "https://api.apollo.io/api/v1/contacts/search"
    headers = {'Content-Type': 'application/json', 'x-api-key': api_key}
    
    # Fragmentar cargos
    chunk_size = 10 
    chunks = [cargos[i:i + chunk_size] for i in range(0, len(cargos), chunk_size)]
    ubicacion = paises[0] if len(paises) == 1 else paises

    for empresa in empresas:
        if stop_event.is_set(): break
        empresa_clean = empresa.strip()
        
        # LOG DE INICIO DE EMPRESA
        log_callback(f"🔎 Buscando en: {empresa_clean}...")
        contactos_esta_empresa = 0

        for i, chunk in enumerate(chunks):
            payload = {
                "q_organization_name": empresa_clean,
                "organization_locations": ubicacion,
                "person_titles": chunk,
                "per_page": 100
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    contacts = response.json().get('contacts', [])
                    nuevos = 0
                    for p in contacts:
                        p_id = p.get("id")
                        if p_id and p_id not in ids_encontrados:
                            ids_encontrados.add(p_id)
                            nuevos += 1
                            resultados.append({
                                "empresa_buscada": empresa_clean,
                                "name": limpiar_texto(p.get("name")),
                                "title": limpiar_texto(p.get("title")),
                                "email": p.get("email"),
                                "organization_name": limpiar_texto(p.get("organization", {}).get("name", ""))
                                # (Agrega aquí el resto de campos que necesites)
                            })
                    
                    contactos_esta_empresa += nuevos
                    # LOG DE CADA LOTE (Esto se verá en tiempo real en la web)
                    if nuevos > 0:
                        log_callback(f"   -> Lote {i+1}: ✅ {nuevos} contactos nuevos.")
                    
                    time.sleep(0.5)
                elif response.status_code == 429:
                    log_callback("   -> ⚠️ Rate limit. Esperando 10s...")
                    time.sleep(10)
            except Exception as e:
                log_callback(f"   -> ❌ Error: {str(e)}")

        # RESUMEN POR EMPRESA
        log_callback(f"📊 {empresa_clean}: {contactos_esta_empresa} totales encontrados.")

    # Guardado Final
    if resultados:
        keys = resultados[0].keys()
        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(resultados)
        return output_file
    return None
