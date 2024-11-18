import pandas as pd
from WebScrappinSatrack import scrape_satrack
import time

def leer_excel(ruta_archivo):
    try:
        # Leer el archivo Excel usando pandas con engine='xlrd'
        df = pd.read_excel(ruta_archivo, engine='xlrd')
        
        # Filtrar solo las filas donde ENTIDAD GPS es SATRACK y tomar los primeros 10
        df_filtrado = df[df['ENTIDAD GPS'] == 'SATRACK'].head(10)
        
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
            print(f"Intentando con usuario: {usuario}")
            
            resultado_satrack = scrape_satrack(usuario, password)
            
            if isinstance(resultado_satrack, dict) and 'vehicles' in resultado_satrack:
                print("¡Credenciales válidas encontradas!")
                
                # Procesar los vehículos encontrados
                for vehicle in resultado_satrack['vehicles']:
                    # Separar las coordenadas en latitud y longitud
                    coords = vehicle['coordinates'].replace(' ', '').split(',') if vehicle['coordinates'] != 'No disponible' else ['', '']
                    lat = coords[0] if len(coords) > 0 else ''
                    lon = coords[1] if len(coords) > 1 else ''
                    
                    all_vehicles_data.append({
                        'PLACA': vehicle['plate'].strip(),
                        'UBICACION': vehicle['location'],
                        'LATITUD': lat,
                        'LONGITUD': lon
                    })
                
                print(f"Vehículos encontrados con este usuario: {len(resultado_satrack['vehicles'])}")
                print(f"Total de vehículos acumulados: {len(all_vehicles_data)}")
                print(f"Progreso: {credenciales_procesadas}/{total_filas} credenciales procesadas")
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
