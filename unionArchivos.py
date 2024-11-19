import pandas as pd

# Leer los archivos
df_satrack = pd.read_excel('/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/ARCHIVOS/BASE DE DATOS TERCERO_satrack_completo_20241118_230539.xlsx')
df_original = pd.read_excel('/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/ARCHIVOS/BASE DE DATOS TERCERO.xls')

# Normalizar placas (eliminar espacios y convertir a mayúsculas)
df_satrack['PLACA'] = df_satrack['PLACA'].str.strip().str.upper()
df_original['PLACA'] = df_original['PLACA'].str.strip().str.upper()

# Diagnóstico: Contar placas únicas en cada archivo
print("Placas en archivo Satrack:")
print(df_satrack['PLACA'].value_counts())
print("\nPlacas en archivo Original:")
print(df_original['PLACA'].value_counts())

# Encontrar placas que están en un archivo pero no en el otro
placas_satrack = set(df_satrack['PLACA'])
placas_original = set(df_original['PLACA'])

print("\nPlacas que están en Satrack pero no en Original:")
print(placas_satrack - placas_original)

print("\nPlacas que están en Original pero no en Satrack:")
print(placas_original - placas_satrack)

# Crear las nuevas columnas en df_original con valores NaN
df_original['LATITUD'] = None
df_original['LONGITUD'] = None

# Actualizar las coordenadas para las placas que coinciden
coincidencias = 0
for index, row in df_satrack.iterrows():
    placa = row['PLACA']
    mask = df_original['PLACA'] == placa
    if mask.any():
        df_original.loc[mask, 'LATITUD'] = row['LATITUD']
        df_original.loc[mask, 'LONGITUD'] = row['LONGITUD']
        coincidencias += 1

# Agregar las placas que están en Satrack pero no en Original
placas_faltantes = placas_satrack - placas_original
for placa in placas_faltantes:
    # Obtener los datos de Satrack para esta placa
    datos_placa = df_satrack[df_satrack['PLACA'] == placa].iloc[0]
    
    # Crear una nueva fila con todos los valores None excepto PLACA, LATITUD y LONGITUD
    nueva_fila = pd.Series(index=df_original.columns)
    nueva_fila[:] = None
    nueva_fila['PLACA'] = placa
    nueva_fila['LATITUD'] = datos_placa['LATITUD']
    nueva_fila['LONGITUD'] = datos_placa['LONGITUD']
    
    # Agregar la nueva fila al DataFrame original
    df_original = pd.concat([df_original, pd.DataFrame([nueva_fila])], ignore_index=True)

# Guardar el archivo actualizado
df_original.to_excel('/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/ARCHIVOS/BASE DE DATOS TERCERO_actualizado.xlsx', index=False)

# Imprimir información de diagnóstico
print(f"\nTotal de coincidencias encontradas: {coincidencias}")
print(f"Total de placas actualizadas con coordenadas: {df_original['LATITUD'].notna().sum()}")
print(f"Total de placas agregadas de Satrack: {len(placas_faltantes)}")
