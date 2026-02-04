import requests
import json
import csv
import os
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run(api_key, empresas, cargos, paises, output_folder, log_callback, stop_event):
    """
    Ejecuta el proceso de extracción de Lusha.
    
    Args:
        api_key (str): La clave de API para Lusha.
        empresas (list): Lista de nombres de empresas.
        cargos (list): Lista de cargos a buscar.
        paises (list): Lista de países seleccionados.
        output_folder (str): Ruta de la carpeta para guardar el resultado.
        log_callback (function): Función para enviar mensajes a la consola de la GUI.
        stop_event (threading.Event): Evento para señalar la cancelación.
    """
    log_callback("🚀 Iniciando búsqueda filtrada de contactos en Lusha...")
    
    url = "https://api.lusha.com/prospecting/contact/search"
    output_file = os.path.join(output_folder, "resultados_lusha.csv")
    
    fieldnames = [
        'empresa_buscada', 'pais_buscado', 'name', 'contactId', 'jobTitle', 'companyId', 'companyName', 'fqdn',
        'personId', 'logoUrl', 'hasEmails', 'hasPhones', 'hasDirectPhone', 'hasWorkEmail', 'hasPrivateEmail',
        'hasMobilePhone', 'hasSocialLink'
    ]

    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            log_callback(f"✅ Archivo de salida '{os.path.basename(output_file)}' creado.")

            for empresa in empresas:
                # --- CAMBIO: Chequear cancelación antes de cada empresa ---
                if stop_event.is_set():
                    log_callback("🛑 Proceso cancelado por el usuario.")
                    break # Sale del bucle de empresas
                
                for pais in paises:
                    # --- CAMBIO: Chequear cancelación antes de cada país ---
                    if stop_event.is_set():
                        log_callback(f"🛑 Cancelado. Omitiendo países restantes para {empresa}.")
                        break # Sale del bucle de países

                    log_callback(f"\n🔎 Buscando en Lusha: {empresa} en {pais}...")
                    
                    payload = {
                        "pages": {"page": 0, "size": 50},
                        "filters": {
                            "contacts": {
                                "include": {
                                    "jobTitles": cargos,
                                    "locations": [{"country": pais}],
                                    "existing_data_points": ["phone", "work_email", "mobile_phone"]
                                }
                            },
                            "companies": {"include": {"names": [empresa]}}
                        }
                    }
                    headers = {'Content-Type': 'application/json', 'api_key': api_key}

                    try:
                        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30, verify=False)
                        data = response.json()

                        if isinstance(data, dict):
                            if response.status_code not in [200, 201]:
                                log_callback(f"  -> ⚠️ Advertencia: Error {response.status_code}: {response.text}")
                                continue
                            contacts = data.get('data', [])
                            if not contacts:
                                log_callback("  -> No se encontraron contactos que cumplan los filtros.")
                            else:
                                log_callback(f"  -> ¡Éxito! Se encontraron {len(contacts)} contactos.")
                                for contact in contacts:
                                    writer.writerow({
                                        'empresa_buscada': empresa, 'pais_buscado': pais,
                                        'name': contact.get('name', 'N/A'),
                                        'contactId': contact.get('contactId', 'N/A'),
                                        'jobTitle': contact.get('jobTitle', 'N/A'),
                                        'companyId': contact.get('companyId', 'N/A'),
                                        'companyName': contact.get('companyName', 'N/A'),
                                        'fqdn': contact.get('fqdn', 'N/A'),
                                        'personId': contact.get('personId', 'N/A'),
                                        'logoUrl': contact.get('logoUrl', 'N/A'),
                                        'hasEmails': contact.get('hasEmails', False),
                                        'hasPhones': contact.get('hasPhones', False),
                                        'hasDirectPhone': contact.get('hasDirectPhone', False),
                                        'hasWorkEmail': contact.get('hasWorkEmail', False),
                                        'hasPrivateEmail': contact.get('hasPrivateEmail', False),
                                        'hasMobilePhone': contact.get('hasMobilePhone', False),
                                        'hasSocialLink': contact.get('hasSocialLink', False)
                                    })
                        else:
                            log_callback("  -> No se encontraron contactos (respuesta en formato de lista).")
                    except requests.exceptions.RequestException as e:
                        log_callback(f"  -> ❌ Error de conexión: {e}")
                    except json.JSONDecodeError:
                        log_callback("  -> ❌ Error: La respuesta no es un JSON válido.")
                    
                    # Salir si se cancela durante la petición
                    if stop_event.is_set():
                        break
                    time.sleep(1)

        # --- CAMBIO: Mensaje final condicional ---
        if stop_event.is_set():
            log_callback(f"\n🚫 Proceso de Lusha cancelado. El archivo '{os.path.basename(output_file)}' puede estar incompleto.")
        else:
            log_callback(f"\n✅ Proceso de Lusha completado. Revisa el archivo '{os.path.basename(output_file)}'.")

    except IOError as e:
        log_callback(f"❌ ERROR FATAL: No se pudo escribir en el archivo de salida. Causa: {e}")