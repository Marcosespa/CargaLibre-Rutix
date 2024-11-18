import pandas as pd
from WebScrappinSatrack import scrape_satrack

def leer_excel(ruta_archivo):
    try:
        # Leer el archivo Excel usando pandas con engine='xlrd'
        df = pd.read_excel(ruta_archivo, engine='xlrd')
        
        # Filtrar solo las filas donde ENTIDAD GPS es SATRACK
        df_filtrado = df[df['ENTIDAD GPS'] == 'SATRACK'].head(3)
        
        # Mostrar el total de filas encontradas después del filtro
        total_filas = len(df_filtrado)
        print(f"\nProcesando {total_filas} filas con SATRACK\n")
        
        # Crear nuevas columnas para la información de Satrack
        df_filtrado['UBICACION_SATRACK'] = ''
        df_filtrado['COORDENADAS_SATRACK'] = ''
        df_filtrado['ESTADO_SATRACK'] = ''
        
        # Intentar con cada conjunto de credenciales hasta que uno funcione
        for index, fila in df_filtrado.iterrows():
            usuario = fila['USUARIO GPS']
            password = fila['CONTRASEÑA GPS']
            print(f"\nIntentando con usuario: {usuario}")
            
            resultado_satrack = scrape_satrack(usuario, password)
            
            if isinstance(resultado_satrack, dict) and 'error' in resultado_satrack:
                print(f"Error con las credenciales: {resultado_satrack['message']}")
                print("Intentando con el siguiente usuario...")
                continue
            
            if resultado_satrack and 'vehicles' in resultado_satrack:
                print("¡Credenciales válidas encontradas!")
                # Actualizar DataFrame con la información de Satrack
                satrack_data = {vehicle['plate']: vehicle for vehicle in resultado_satrack['vehicles']}
                
                # Crear un nuevo DataFrame solo para las placas encontradas
                placas_encontradas = []
                
                for idx, fila in df_filtrado.iterrows():
                    placa = fila['PLACA']
                    if placa in satrack_data:
                        vehicle_info = satrack_data[placa]
                        df_filtrado.at[idx, 'UBICACION_SATRACK'] = vehicle_info['location']
                        df_filtrado.at[idx, 'COORDENADAS_SATRACK'] = vehicle_info['coordinates']
                        df_filtrado.at[idx, 'ESTADO_SATRACK'] = vehicle_info['status']
                        placas_encontradas.append(idx)
                        print(f"Actualizada información para placa: {placa}")
                
                # Filtrar solo las filas con placas encontradas
                df_final = df_filtrado.loc[placas_encontradas]
                
                # Guardar el DataFrame actualizado
                nombre_archivo = ruta_archivo.replace('.xls', '_actualizado.xlsx')
                df_final.to_excel(nombre_archivo, index=False)
                print(f"\nArchivo actualizado guardado como: {nombre_archivo}")
                print(f"Total de placas encontradas y actualizadas: {len(placas_encontradas)}")
                return True
                
        print("Se agotaron todos los intentos de inicio de sesión")
        return False
            
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        return False

# Ejemplo de uso
if __name__ == "__main__":
    ruta_archivo = "/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/BASE DE DATOS TERCERO.xls"
    leer_excel(ruta_archivo)
