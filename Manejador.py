import pandas as pd
from WebScrappinSatrack import scrape_satrack
import time

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

def leer_excel(ruta_archivo):
    try:
        # Leer el archivo Excel usando pandas con engine='xlrd'
        df = pd.read_excel(ruta_archivo, engine='xlrd')
        
        # Filtrar solo las filas donde ENTIDAD GPS es SATRACK y tomar los primeros 10
        df_filtrado = df[df['ENTIDAD GPS'] == 'SATRACK'].head(20)
        
        # Mostrar el total de filas encontradas después del filtro
        total_filas = len(df_filtrado)
        print(f"\nProcesando {total_filas} filas con SATRACK\n")
        
        # Lista para acumular todos los vehículos
        all_vehicles_data = []
        credenciales_procesadas = 0
        
        # Intentar con cada conjunto de credenciales
        for index, fila in df_filtrado.iterrows():
            credenciales_procesadas += 1
            usuario = fila['USUARIO GPS']
            password = fila['CONTRASEÑA GPS']
            print(f"\nProcesando credencial {credenciales_procesadas} de {total_filas}")
            print(f"Intentando con usuario: {usuario} Y contraseña {password}")
            
            resultado_satrack = scrape_satrack(usuario, password)

            # Imprimir el resultado completo de WebScrapping
            print("\nResultado completo de WebScrapping:")
            if resultado_satrack:
                print("\nDatos obtenidos exitosamente:")
                print(resultado_satrack)
   

            
            if isinstance(resultado_satrack, dict) and 'vehicles' in resultado_satrack:
                print("\n¡Credenciales válidas encontradas!")
                print("Vehículos encontrados:", len(resultado_satrack['vehicles']))
                
                # Imprimir cada vehículo en detalle
                print("\nDetalle de cada vehículo:")
                for i, vehicle in enumerate(resultado_satrack['vehicles'], 1):
                    print(f"\nVehículo {i}:")
                    for key, value in vehicle.items():
                        print(f"{key}: {value}")
                
                # Procesar los vehículos encontrados
                for vehicle in resultado_satrack['vehicles']:
                    # Procesar coordenadas
                    lat, lon = process_coordinates(vehicle['coordinates'])
                    
                    # Imprimir información de debug
                    print(f"Placa: {vehicle['plate']}")
                    print(f"Coordenadas originales: {vehicle['coordinates']}")
                    print(f"Latitud procesada: {lat}")
                    print(f"Longitud procesada: {lon}")
                    
                    all_vehicles_data.append({
                        'PLACA': vehicle['plate'].strip(),
                        'UBICACION': vehicle['location'],
                        'LATITUD': lat,
                        'LONGITUD': lon
                    })
                
                print(f"\nVehículos encontrados con este usuario: {len(resultado_satrack['vehicles'])}")
                print(f"Total de vehículos acumulados: {len(all_vehicles_data)}")
                print("\nLista actual de vehículos acumulados:")
                for idx, vehicle in enumerate(all_vehicles_data, 1):
                    print(f"{idx}. Placa: {vehicle['PLACA']}, Lat: {vehicle['LATITUD']}, Lon: {vehicle['LONGITUD']}")
                print(f"\nProgreso: {credenciales_procesadas}/{total_filas} credenciales procesadas")
            else:
                print(f"Las credenciales no fueron válidas o no se obtuvieron datos")
        
        # Al final, guardar todos los vehículos en un solo archivo
        if all_vehicles_data:
            # Crear DataFrame con todos los vehículos acumulados
            df_final = pd.DataFrame(all_vehicles_data)
            
            # Guardar el DataFrame final
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            nombre_archivo = ruta_archivo.replace('.xls', f'_satrack_completo_{timestamp}.xlsx')
            df_final.to_excel(nombre_archivo, index=False)
            print(f"\nArchivo final guardado como: {nombre_archivo}")
            print(f"Total de vehículos guardados: {len(all_vehicles_data)}")
        else:
            print("\nNo se encontraron vehículos con ninguna credencial")
            
        print(f"\nProceso completado. Se procesaron {credenciales_procesadas} conjuntos de credenciales")
        return True
            
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        return False

# Ejemplo de uso
if __name__ == "__main__":
    ruta_archivo = "/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/BASE DE DATOS TERCERO.xls"
    leer_excel(ruta_archivo)
