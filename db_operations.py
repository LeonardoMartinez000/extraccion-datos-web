import psycopg2
import csv
import re
import threading
from tkinter import messagebox # Todavía se necesita para los pop-ups

# ==========================================================
# --- LÓGICA DE BASE DE DATOS (Aislada de la UI) ---
# ==========================================================

def execute_test_connection(db_params, log_callback, after_callback):

    try:
        conn = psycopg2.connect(**db_params, connect_timeout=5)
        conn.close()
        log_callback("✅ ¡Conexión exitosa!")
        after_callback(0, lambda: messagebox.showinfo("Conexión Exitosa","La conexión a la base de datos PostgreSQL fue exitosa."))
    except Exception as e:
        log_callback(f"❌ ERROR de conexión: {e}")
        after_callback(0, lambda: messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos.\n\nError: {e}"))

def execute_load_to_db(db_params, apollo_file, lusha_file, log_callback, after_callback):
    
    conn = None
    try:
        log_callback("Conectando a la base de datos...")
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        log_callback("✅ Conexión exitosa.")

        # --- Eliminar tablas antiguas ---
        log_callback("Eliminando tablas antiguas (si existen)...")
        cur.execute("DROP TABLE IF EXISTS resultados_apollo;")
        cur.execute("DROP TABLE IF EXISTS resultados_lusha;")
        log_callback("Tablas 'resultados_apollo' y 'resultados_lusha' eliminadas.")
        
        # --- Procesar Archivo Apollo ---
        log_callback(f"Iniciando carga de {apollo_file}...")
        _process_csv_to_db(cur, apollo_file, "resultados_apollo", log_callback)
        
        # --- Procesar Archivo Lusha ---
        log_callback(f"Iniciando carga de {lusha_file}...")
        _process_csv_to_db(cur, lusha_file, "resultados_lusha", log_callback)

        conn.commit()
        cur.close()
        log_callback("✅ Carga de datos completada exitosamente.")
        after_callback(0, lambda: messagebox.showinfo("Proceso Completado", 
                       "Los datos de Apollo y Lusha se han cargado exitosamente."))

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        error_msg = str(error).replace('\n', ' ')
        log_callback(f"❌ ERROR durante la carga a la BD: {error_msg}")
        after_callback(0, lambda: messagebox.showerror("Error en Base de Datos", 
                       f"Ocurrió un error: {error_msg}"))
    finally:
        if conn:
            conn.close()
            log_callback("Conexión cerrada.")

def _process_csv_to_db(cur, filepath, table_name, log_callback):
 
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # 1. Leer y limpiar encabezado
            header = next(reader)
            clean_headers = []
            for h in header:
                clean_h = h.lower().strip()
                clean_h = re.sub(r'[\s\.\-\/]+', '_', clean_h)
                clean_h = re.sub(r'[^\w_]', '', clean_h)
                if clean_h and clean_h[0].isdigit():
                    clean_h = f"_{clean_h}"
                clean_headers.append(f'"{clean_h}"')
            
            log_callback(f"Columnas detectadas para {table_name}: {', '.join(clean_headers)}")

            # 2. Crear la tabla
            cols_sql = ', '.join([f'{h} TEXT' for h in clean_headers])
            create_sql = f'CREATE TABLE {table_name} ({cols_sql});'
            log_callback(f"Ejecutando: CREATE TABLE {table_name}...")
            cur.execute(create_sql)

            # 3. Preparar e insertar datos
            data = list(reader)
            if not data:
                log_callback(f"Advertencia: El archivo {filepath} no tiene datos después del encabezado.")
                return

            placeholders = ', '.join(['%s'] * len(clean_headers))
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders});"
            
            cur.executemany(insert_sql, data)
            log_callback(f"✅ {len(data)} registros insertados en {table_name}.")

    except StopIteration:
        log_callback(f"❌ ERROR: El archivo {filepath} está vacío o no tiene encabezado.")
        raise Exception(f"El archivo {filepath} está vacío.")
    except Exception as e:
        log_callback(f"❌ ERROR al procesar {filepath}: {e}")
        raise e # Relanzar la excepción para que sea capturada

def execute_clean_data(log_callback):
    """(Hilo) Simulación de limpieza."""
    log_callback("... (Simulación) Ejecutando scripts de limpieza en la BD...")
    # Simular un trabajo que toma tiempo
    threading.Event().wait(2) 
    log_callback("... (Simulación) Proceso de limpieza finalizado.")

def execute_consolidate_data(log_callback):
    """(Hilo) Simulación de consolidación."""
    log_callback("... (Simulación) Ejecutando lógica de consolidación en la BD...")
    # Simular un trabajo que toma tiempo
    threading.Event().wait(3) 
    log_callback("... (Simulación) Proceso de consolidación finalizado.")