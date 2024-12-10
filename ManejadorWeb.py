import pandas as pd
from WebScrappinSatrack import scrape_satrack
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

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

def leer_excel(ruta_archivo, inicio, fin):
    tiempo_inicio = datetime.now()
    print(f"\nInicio del proceso: {tiempo_inicio.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        df = pd.read_excel(ruta_archivo, engine='xlrd')
        df_filtrado = df[df['ENTIDAD GPS'] == 'SATRACK'].iloc[inicio:fin]
        
        total_filas = len(df_filtrado)
        print(f"\nProcesando {total_filas} filas con SATRACK (filas {inicio} a {fin})\n")
        
        all_vehicles_data = []
        
        # Procesar credenciales en paralelo
        with ThreadPoolExecutor(max_workers=3) as executor:
            credentials_list = df_filtrado.to_dict('records')
            # Usar map en lugar de submit para mantener el orden
            results = list(executor.map(process_credentials, credentials_list))
            
            # Combinar resultados
            for vehicles in results:
                all_vehicles_data.extend(vehicles)
        
        # Guardar resultados
        if all_vehicles_data:
            df_final = pd.DataFrame(all_vehicles_data)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            nombre_archivo = ruta_archivo.replace('.xls', f'_satrack_parte_{inicio}_{fin}_{timestamp}.xlsx')
            df_final.to_excel(nombre_archivo, index=False)
            print(f"\nArchivo final guardado como: {nombre_archivo}")
            print(f"Total de vehículos guardados: {len(all_vehicles_data)}")
        
        tiempo_fin = datetime.now()
        tiempo_total = tiempo_fin - tiempo_inicio
        print(f"\nTiempo total de ejecución: {tiempo_total}")
        
        return True
            
    except Exception as e:
        tiempo_fin = datetime.now()
        tiempo_total = tiempo_fin - tiempo_inicio
        print(f"Error al procesar el archivo: {str(e)}")
        print(f"\nTiempo hasta el error: {tiempo_total}")
        return False

    
if __name__ == "__main__":
    import sys
    #ruta_archivo = "/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/ARCHIVOS/BASE DE DATOS TERCERO.xls"

    # Ruta del archivo y parámetros para dividir el procesamiento
    ruta_archivo = "/home/labs/CargaLibre-Rutix/ARCHIVOS/BASE DE DATOS TERCERO.xls"
    inicio = int(sys.argv[1])  # Fila inicial
    fin = int(sys.argv[2])     # Fila final

    leer_excel(ruta_archivo, inicio, fin)