import pandas as pd
from WebScrappinSatrack import scrape_satrack
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import signal

# Agregar variable global para controlar la interrupción
interrupted = False

def signal_handler(signum, frame):
    """Manejador de señal para Ctrl+C"""
    global interrupted
    print("\nSeñal de interrupción recibida. Guardando progreso actual...")
    interrupted = True

def process_coordinates(coordinates_str):
    """
    Procesa el string de coordenadas y retorna latitud y longitud.
    """
    try:
        if not coordinates_str or coordinates_str == 'No disponible':
            return '', ''
            
        # Limpiar el string de coordenadas
        coords_clean = coordinates_str.replace(' ', '').strip()
        
        # Intentar diferentes formatos de separación
        if ',' in coords_clean:
            lat, lon = coords_clean.split(',', 1)
        elif ';' in coords_clean:
            lat, lon = coords_clean.split(';', 1)
        else:
            print(f"Formato de coordenadas no reconocido: {coordinates_str}")
            return '', ''
            
        # Validar que sean números
        try:
            float(lat)
            float(lon)
            return lat.strip(), lon.strip()
        except ValueError:
            print(f"Coordenadas no válidas: lat={lat}, lon={lon}")
            return '', ''
            
    except Exception as e:
        print(f"Error procesando coordenadas '{coordinates_str}': {str(e)}")
        return '', ''

def process_credentials(credentials):
    """Procesa un conjunto de credenciales con su propia instancia de navegador"""
    try:
        usuario = credentials['USUARIO GPS']
        password = credentials['CONTRASEÑA GPS']
        
        print(f"\nProcesando credenciales: {usuario}")
        resultado_satrack = scrape_satrack(usuario, password)
        
        if resultado_satrack and 'vehicles' in resultado_satrack:
            vehicles_data = []
            for vehicle in resultado_satrack['vehicles']:
                lat, lon = process_coordinates(vehicle['coordinates'])
                vehicles_data.append({
                    'PLACA': vehicle['plate'].strip(),
                    'UBICACION': vehicle['location'],
                    'LATITUD': lat,
                    'LONGITUD': lon
                })
            return vehicles_data
        return []
    except Exception as e:
        print(f"Error procesando credencial {usuario}: {str(e)}")
        return []

def get_output_filename(vm_id, ruta_archivo):
    """Determina el nombre del archivo de salida según el ID de la VM"""
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    base_name = ruta_archivo.rsplit('.', 1)[0]  # Nombre base sin extensión
    
    vm_names = {
        0: "NORTE",
        1: "SUR",
        2: "ORIENTE",
        3: "OCCIDENTE"
    }
    
    vm_name = vm_names.get(vm_id, f"VM{vm_id}")
    return f"{base_name}_satrack_{vm_name}_{timestamp}.xlsx"

def leer_excel(ruta_archivo, vm_id, total_vms=4, threads=3):
    """
    Args:
        ruta_archivo: Ruta al archivo Excel
        vm_id: ID de la máquina virtual (0-3)
        total_vms: Número total de VMs
        threads: Número de threads por VM
    """
    signal.signal(signal.SIGINT, signal_handler)
    
    tiempo_inicio = datetime.now()
    print(f"\nInicio del proceso VM_{vm_id}: {tiempo_inicio.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Leer todo el archivo
        df = pd.read_excel(ruta_archivo, engine='xlrd')
        df_filtrado = df[df['ENTIDAD GPS'] == 'SATRACK']
        
        # Calcular el rango para esta VM
        total_registros = len(df_filtrado)
        registros_por_vm = total_registros // total_vms
        start_index = vm_id * registros_por_vm
        end_index = start_index + registros_por_vm if vm_id < total_vms - 1 else len(df_filtrado)
        
        # Obtener el subset para esta VM
        df_vm = df_filtrado.iloc[start_index:end_index]
        
        print(f"\nVM_{vm_id} procesando registros {start_index} a {end_index} ({end_index-start_index} registros)")
        print(f"Usando {threads} threads")
        
        all_vehicles_data = []
        credenciales_procesadas = 0
        
        # Ajustar ThreadPoolExecutor al número de threads especificado
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            credentials_list = df_vm.to_dict('records')
            
            for credentials in credentials_list:
                if interrupted:
                    break
                futures.append(executor.submit(process_credentials, credentials))
            
            total_credenciales = len(credentials_list)
            for future in futures:
                try:
                    vehicles = future.result()
                    all_vehicles_data.extend(vehicles)
                    credenciales_procesadas += 1
                    print(f"VM_{vm_id} Progreso: {credenciales_procesadas}/{total_credenciales} "
                          f"({(credenciales_procesadas/total_credenciales)*100:.1f}%)")
                except Exception as e:
                    credenciales_procesadas += 1
                    print(f"Error en proceso VM_{vm_id}: {str(e)}")

        # Guardar resultados con identificador de VM
        if all_vehicles_data:
            df_final = pd.DataFrame(all_vehicles_data)
            nombre_archivo = get_output_filename(vm_id, ruta_archivo)
            df_final.to_excel(nombre_archivo, index=False)
            print(f"\nVM_{vm_id} - Archivo guardado como: {nombre_archivo}")
            print(f"Total de vehículos guardados: {len(all_vehicles_data)}")
        
        tiempo_fin = datetime.now()
        tiempo_total = tiempo_fin - tiempo_inicio
        print(f"\nVM_{vm_id} - Tiempo total de ejecución: {tiempo_total}")
        
        return True
            
    except Exception as e:
        tiempo_fin = datetime.now()
        tiempo_total = tiempo_fin - tiempo_inicio
        print(f"Error en VM_{vm_id}: {str(e)}")
        print(f"\nTiempo hasta el error: {tiempo_total}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python ManejadorWeb.py <vm_id> [ruta_archivo]")
        sys.exit(1)
    
    vm_id = int(sys.argv[1])  # 0, 1, 2, o 3
    ruta_archivo = sys.argv[2] if len(sys.argv) > 2 else "ruta/al/archivo.xls"
    
    # Configuración para cada VM
    TOTAL_VMS = 4
    THREADS_PER_VM = 3
    
    if vm_id < 0 or vm_id >= TOTAL_VMS:
        print(f"VM ID debe estar entre 0 y {TOTAL_VMS-1}")
        sys.exit(1)
    
    leer_excel(ruta_archivo, vm_id, TOTAL_VMS, THREADS_PER_VM)
