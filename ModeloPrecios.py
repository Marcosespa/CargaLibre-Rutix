import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from geopy.distance import geodesic
# Ruta al archivo JSON con tus credenciales de servicio
SERVICE_ACCOUNT_FILE = '/Users/marcosrodrigo/Desktop/CodeStrack/chatbot-441820-2e2f6ba91e6b.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Autenticación con la API de Google Sheets
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# ID de las hojas de Google Sheets
SPREADSHEET_ID_VEHICULOS = '1EMtswwTMaAwg8WYd_4TurpcqcZgJ4UEQcLNmcD1WeC4'
SPREADSHEET_ID_TARIFAS = '1I-LfPQGD8_lTpPgj-ewnaXnmcO7NEZD_qjAL4SNIrkw'

# Conectar a la hoja de vehículos
sheet_vehiculos = client.open_by_key(SPREADSHEET_ID_VEHICULOS).sheet1
data_vehiculos = sheet_vehiculos.get_all_values()
df_vehiculos = pd.DataFrame(data_vehiculos[1:], columns=data_vehiculos[0])

# Eliminar caracteres no deseados como comillas simples, espacios, etc.
df_vehiculos['Latitud'] = df_vehiculos['Latitud'].str.replace("'", "", regex=False).str.strip()
df_vehiculos['Longuitud'] = df_vehiculos['Longuitud'].str.replace("'", "", regex=False).str.strip()

# Convertir a numéricos después de limpiar
df_vehiculos['Latitud'] = pd.to_numeric(df_vehiculos['Latitud'], errors='coerce')
df_vehiculos['Longuitud'] = pd.to_numeric(df_vehiculos['Longuitud'], errors='coerce')
#Direcciones de las ciudades (actualizado con coordenadas correctas)
ciudades = {
    'BOGOTA': (4.7110, -74.0721),
    'CALI': (3.4516, -76.5320),
    'MEDELLIN': (6.2442, -75.5812),
    'PASTO': (1.2136, -77.2811),
    'ARMENIA': (4.5339, -75.6811),
    'BUCARAMANGA': (7.1193, -73.1227),
    'BARRANQUILLA': (10.9685, -74.7813),
    'CARTAGENA': (10.3910, -75.4794),
    'SANTA MARTA': (11.2408, -74.1990),
    'MANIZALES': (5.0703, -75.5138),
    'PEREIRA': (4.8087, -75.6906),
    'IBAGUE': (4.4389, -75.2323),
    'NEIVA': (2.9273, -75.2819),
    'VILLAVICENCIO': (4.1420, -73.6266),
    'CUCUTA': (7.8939, -72.5078),
    'TUNJA': (5.5353, -73.3678),
    'MONTERIA': (8.7479, -75.8814),
    'VALLEDUPAR': (10.4631, -73.2532),
    'POPAYAN': (2.4419, -76.6067),
    'SINCELEJO': (9.3047, -75.3978),
    'RIOHACHA': (11.5444, -72.9072),
    'QUIBDO': (5.6947, -76.6583),
    'FLORENCIA': (1.6144, -75.6062),
    'YOPAL': (5.3378, -72.3959),
    'MOSQUERA': (4.7059, -74.2302),
    'ESPINAL': (4.1489, -74.8838),
    'CARTAGO': (4.7471, -75.9116),
    'TULUA': (4.0847, -76.1962),
    'SAN GIL': (6.5554, -73.1374),
    'RIONEGRO': (6.1462, -75.3737),
    'CAJICA': (4.9185, -74.0268),
    'PALMIRA': (3.5394, -76.3036),
    'DUITAMA': (5.8268, -73.0334),
    'COTA': (4.8137, -74.1027),
    'GIRARDOT': (4.3045, -74.8031),
    'BUENAVENTURA': (3.8833, -77.0333),
    'SOGAMOSO': (5.7158, -72.9345),
    'FUSAGASUGA': (4.3371, -74.3638),
    'MADRID': (4.7321, -74.2642)
}

# Agregar después del diccionario de ciudades
tipos_vehiculos = {
    'Mini Mula': 'MINIMULA 17 TON.- 70m3',
    'Turbo': 'TURBO 4.5 TON. - 25m3',
    'Sencillo': 'SENCILLO 8.5 TON. - 40m3',
    'Tracto Mula': 'TRACTO MULA 34 TON. 70m3'
}

# Al inicio del archivo, después de las importaciones
# Constantes de configuración para los factores de ajuste
FACTORES_DISPONIBILIDAD = {
    'muy_baja': {'limite': 3, 'factor': 1.15},
    'baja': {'limite': 5, 'factor': 1.08},
    'alta': {'limite': 15, 'factor': 0.97},
    'muy_alta': {'limite': float('inf'), 'factor': 0.95}
}

FACTORES_DIA = {
    'fin_semana': {'dias': [4, 5], 'factor': 1.05},  # Viernes y Sábado
    'domingo': {'dias': [6], 'factor': 0.97},
    'entre_semana': {'dias': [0, 1, 2, 3], 'factor': 1.0}
}

FACTORES_TEMPORADA = {
    'alta': {'meses': [12, 1, 6, 7], 'factor': 1.08},
    'media': {'meses': [4, 5, 9, 10], 'factor': 1.03},
    'baja': {'meses': [2, 3, 8, 11], 'factor': 1.0}
}

def obtener_ciudad(latitud, longitud):
    if pd.isna(latitud) or pd.isna(longitud):
        return 'Desconocido'
    
    # Calcular la distancia a cada ciudad y devolver la más cercana
    ubicacion_usuario = (latitud, longitud)
    ciudad_mas_cercana = None
    distancia_minima = float('inf')
    
    for ciudad, coordenadas in ciudades.items():
        distancia = geodesic(ubicacion_usuario, coordenadas).kilometers
        if distancia < distancia_minima:
            distancia_minima = distancia
            ciudad_mas_cercana = ciudad
            
    return ciudad_mas_cercana

# Generar la columna 'Ciudad' usando las coordenadas
df_vehiculos['Ciudad'] = df_vehiculos.apply(lambda row: obtener_ciudad(row['Latitud'], row['Longuitud']), axis=1)
print("\nDatos después de asignar la ciudad:")
print(df_vehiculos[['Nombre', 'Latitud', 'Longuitud', 'Ciudad']].head())

# Conectar a la hoja de tarifas y leer datos
sheet_tarifas = client.open_by_key(SPREADSHEET_ID_TARIFAS)
worksheet_cliente = sheet_tarifas.get_worksheet(0)
worksheet_conductor = sheet_tarifas.get_worksheet(1)

# Definir encabezados y leer datos
headers = ['ORIGEN', 'DESTINO', 'TURBO 4.5 TON. - 25m3', 'SENCILLO 8.5 TON. - 40m3', 'MINIMULA 17 TON.- 70m3', 'TRACTO MULA 34 TON. 70m3']
df_tarifas_cliente = pd.DataFrame(worksheet_cliente.get_values('A2:F36'), columns=headers)
df_tarifas_conductor = pd.DataFrame(worksheet_conductor.get_values('A2:F36'), columns=headers)

# Limpiar valores monetarios
def limpiar_valor(valor):
    return pd.to_numeric(valor.replace('$', '').replace(',', '').strip(), errors='coerce')

for col in headers[2:]:
    df_tarifas_cliente[col] = df_tarifas_cliente[col].apply(limpiar_valor)
    df_tarifas_conductor[col] = df_tarifas_conductor[col].apply(limpiar_valor)

# Crear diccionario de tarifas
tarifas_dict = {'cliente': {}, 'conductor': {}}

# Mapeo para clientes
for _, row in df_tarifas_cliente.iterrows():
    origen = row['ORIGEN']
    destino = row['DESTINO']
    
    if origen not in tarifas_dict['cliente']:
        tarifas_dict['cliente'][origen] = {}
    
    tarifas_dict['cliente'][origen][destino] = {
        'TURBO 4.5 TON. - 25m3': row['TURBO 4.5 TON. - 25m3'],
        'SENCILLO 8.5 TON. - 40m3': row['SENCILLO 8.5 TON. - 40m3'],
        'MINIMULA 17 TON.- 70m3': row['MINIMULA 17 TON.- 70m3'],
        'TRACTO MULA 34 TON. 70m3': row['TRACTO MULA 34 TON. 70m3']
    }

# Mapeo para conductores (similar al de clientes)
for _, row in df_tarifas_conductor.iterrows():
    origen = row['ORIGEN']
    destino = row['DESTINO']
    
    if origen not in tarifas_dict['conductor']:
        tarifas_dict['conductor'][origen] = {}
    
    tarifas_dict['conductor'][origen][destino] = {
        'TURBO 4.5 TON. - 25m3': row['TURBO 4.5 TON. - 25m3'],
        'SENCILLO 8.5 TON. - 40m3': row['SENCILLO 8.5 TON. - 40m3'],
        'MINIMULA 17 TON.- 70m3': row['MINIMULA 17 TON.- 70m3'],
        'TRACTO MULA 34 TON. 70m3': row['TRACTO MULA 34 TON. 70m3']
    }

# Primero, veamos qué columnas tenemos en las hojas de tarifas
# print("Columnas en df_tarifas_cliente:")
# print(df_tarifas_cliente.columns)
# print("\nColumnas en df_tarifas_conductor:")
# print(df_tarifas_conductor.columns)

def obtener_tarifa(tipo, origen, destino, disponibilidad, tipo_tarifa='cliente'):
    """
    Calcula la tarifa ajustada basada en múltiples factores.
    
    Args:
        tipo (str): Tipo de vehículo
        origen (str): Ciudad de origen
        destino (str): Ciudad de destino
        disponibilidad (int): Cantidad de vehículos disponibles
        tipo_tarifa (str): 'cliente' o 'conductor'
    
    Returns:
        float: Tarifa ajustada o str en caso de error
    """
    try:
        from datetime import datetime
        
        # Validaciones básicas
        if not all([tipo, origen, destino, disponibilidad]):
            return "Faltan datos requeridos"
        
        tipo_estandarizado = tipos_vehiculos.get(tipo)
        if tipo_estandarizado is None:
            return "Tipo de vehículo no reconocido"
            
        # Obtener tarifa base
        origen = origen.upper()
        destino = destino.upper()
        tarifa_base = tarifas_dict[tipo_tarifa].get(origen, {}).get(destino, {}).get(tipo_estandarizado)
        
        if tarifa_base is None:
            return "Ruta no disponible"
        
        # Convertir a número si es string
        if isinstance(tarifa_base, str):
            tarifa_base = float(tarifa_base.replace('$', '').replace(',', '').strip())
        
        # 1. Factor de disponibilidad (reducido)
        if disponibilidad < FACTORES_DISPONIBILIDAD['muy_baja']['limite']:
            factor_disponibilidad = FACTORES_DISPONIBILIDAD['muy_baja']['factor']
        elif disponibilidad < FACTORES_DISPONIBILIDAD['baja']['limite']:
            factor_disponibilidad = FACTORES_DISPONIBILIDAD['baja']['factor']
        elif disponibilidad > FACTORES_DISPONIBILIDAD['alta']['limite']:
            factor_disponibilidad = FACTORES_DISPONIBILIDAD['alta']['factor']
        elif disponibilidad > FACTORES_DISPONIBILIDAD['muy_alta']['limite']:
            factor_disponibilidad = FACTORES_DISPONIBILIDAD['muy_alta']['factor']
        else:
            factor_disponibilidad = 1.0
        
        # 2. Factor día de la semana (reducido)
        dia_actual = datetime.now().weekday()
        if dia_actual in FACTORES_DIA['fin_semana']['dias']:  # Viernes y Sábado
            factor_dia = FACTORES_DIA['fin_semana']['factor']
        elif dia_actual in FACTORES_DIA['domingo']['dias']:  # Domingo
            factor_dia = FACTORES_DIA['domingo']['factor']
        else:
            factor_dia = FACTORES_DIA['entre_semana']['factor']
        
        # 3. Factor temporada (reducido)
        mes_actual = datetime.now().month
        if mes_actual in FACTORES_TEMPORADA['alta']['meses']:  # Temporada alta
            factor_temporada = FACTORES_TEMPORADA['alta']['factor']
        elif mes_actual in FACTORES_TEMPORADA['media']['meses']:  # Temporada media
            factor_temporada = FACTORES_TEMPORADA['media']['factor']
        else:  # Temporada baja
            factor_temporada = FACTORES_TEMPORADA['baja']['factor']
        
        # 4. Factor distancia (ajustado)
        origen_coords = ciudades.get(origen)
        destino_coords = ciudades.get(destino)
        
        if origen_coords and destino_coords:
            distancia = geodesic(origen_coords, destino_coords).kilometers
            
            if distancia > 800:
                factor_distancia = 0.90 if tipo_tarifa == 'cliente' else 1.10  # Ajustado de 0.80/1.20
            elif distancia > 500:
                factor_distancia = 0.92 if tipo_tarifa == 'cliente' else 1.08  # Ajustado de 0.85/1.15
            elif distancia > 300:
                factor_distancia = 0.95 if tipo_tarifa == 'cliente' else 1.05  # Ajustado de 0.90/1.10
            elif distancia > 100:
                factor_distancia = 0.97 if tipo_tarifa == 'cliente' else 1.03  # Ajustado de 0.95/1.05
            else:
                factor_distancia = 1.05 if tipo_tarifa == 'cliente' else 0.95  # Ajustado de 1.10/0.90
            
            # Debug info específica para distancia
            # print(f"\nDistancia {origen} -> {destino}: {distancia:.1f}km")
            # print(f"Tipo de ruta: {tipo_ruta}")
            # print(f"Factor distancia aplicado: {factor_distancia}")
        else:
            factor_distancia = 1.0
            # print(f"No se pudo calcular la distancia entre {origen} y {destino}")
        
        # Calcular tarifa final
        tarifa_ajustada = tarifa_base * factor_disponibilidad * factor_dia * factor_temporada * factor_distancia
        
        # Redondear a miles para tener precios más comerciales
        tarifa_ajustada = round(tarifa_ajustada / 1000) * 1000
        
        # # Debug info
        # if tipo_tarifa == 'cliente':
        #     print(f"\nFactores aplicados para {destino}:")
        #     print(f"Disponibilidad: {factor_disponibilidad:.2f}")
        #     print(f"Día: {factor_dia:.2f}")
        #     print(f"Temporada: {factor_temporada:.2f}")
        #     print(f"Distancia: {factor_distancia:.2f}")
        #     print(f"Tarifa base: ${tarifa_base:,.0f}")
        #     print(f"Tarifa final: ${tarifa_ajustada:,.0f}")
        
        return tarifa_ajustada
    except Exception as e:
        return f"Error al calcular tarifa: {str(e)}"

# Calcular tarifas ajustadas
resultados_cliente = []
resultados_conductor = []

for _, row in df_vehiculos.iterrows():
    ciudad = row['Ciudad']
    tipo = row['Tipo de carro']
    disponibilidad = df_vehiculos[df_vehiculos['Ciudad'] == ciudad].shape[0]
    
    if ciudad == 'BOGOTA':
        destinos_disponibles = set(df_tarifas_cliente['DESTINO'].unique())
        
        for destino in destinos_disponibles:
            if destino != 'BOGOTA':
                # Obtener el tipo estandarizado para buscar en el diccionario
                tipo_estandarizado = tipos_vehiculos.get(tipo)
                
                # Obtener precio base del diccionario de tarifas
                precio_base_cliente = tarifas_dict['cliente'].get('BOGOTA', {}).get(destino, {}).get(tipo_estandarizado, "No disponible")
                precio_base_conductor = tarifas_dict['conductor'].get('BOGOTA', {}).get(destino, {}).get(tipo_estandarizado, "No disponible")
                
                # Obtener tarifas ajustadas
                tarifa_cliente = obtener_tarifa(tipo, 'BOGOTA', destino, disponibilidad, 'cliente')
                tarifa_conductor = obtener_tarifa(tipo, 'BOGOTA', destino, disponibilidad, 'conductor')
                
                # Agregar a resultados de cliente
                resultados_cliente.append({
                    'Tipo_Vehiculo': tipo,
                    'Ciudad_Destino': destino,
                    'Precio_Base': precio_base_cliente,
                    'Tarifa_Ajustada': tarifa_cliente,
                    'Diferencia': tarifa_cliente - precio_base_cliente if isinstance(tarifa_cliente, (int, float)) and isinstance(precio_base_cliente, (int, float)) else "No calculable"
                })
                
                # Agregar a resultados de conductor
                resultados_conductor.append({
                    'Tipo_Vehiculo': tipo,
                    'Ciudad_Destino': destino,
                    'Precio_Base': precio_base_conductor,
                    'Tarifa_Ajustada': tarifa_conductor,
                    'Diferencia': tarifa_conductor - precio_base_conductor if isinstance(tarifa_conductor, (int, float)) and isinstance(precio_base_conductor, (int, float)) else "No calculable"
                })

# Crear DataFrames separados
df_tarifas_cliente = pd.DataFrame(resultados_cliente)
df_tarifas_conductor = pd.DataFrame(resultados_conductor)

# Formatear los resultados para mejor visualización
def format_dataframe(df):
    # Ordenar por tipo de vehículo y ciudad
    df = df.sort_values(['Tipo_Vehiculo', 'Ciudad_Destino'])
    
    # Formatear columnas numéricas
    for col in ['Precio_Base', 'Tarifa_Ajustada', 'Diferencia']:
        df[col] = df[col].apply(lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) else x)
    
    return df

#CONSULTA ESPECIFICA
def consultar_tarifa_especifica(origen, destino, tipo_vehiculo, mostrar_detalles=True):
    """
    Consulta la tarifa específica para una ruta y tipo de vehículo.
    
    Args:
        origen (str): Ciudad de origen
        destino (str): Ciudad de destino
        tipo_vehiculo (str): Tipo de vehículo
        mostrar_detalles (bool): Si se deben mostrar los detalles del cálculo
    
    Returns:
        dict: Diccionario con las tarifas y detalles
    """
    try:
        if not all([origen, destino, tipo_vehiculo]):
            raise ValueError("Todos los parámetros son requeridos")
            
        origen = origen.upper()
        destino = destino.upper()
        
        if origen not in ciudades or destino not in ciudades:
            raise ValueError("Ciudad de origen o destino no válida")
            
        # Verificar disponibilidad de vehículos
        disponibilidad = df_vehiculos[
            (df_vehiculos['Ciudad'] == origen) & 
            (df_vehiculos['Tipo de carro'] == tipo_vehiculo)
        ].shape[0]
        
        # Obtener tipo estandarizado y precios base
        tipo_estandarizado = tipos_vehiculos.get(tipo_vehiculo)
        precio_base_cliente = tarifas_dict['cliente'].get(origen, {}).get(destino, {}).get(tipo_estandarizado)
        precio_base_conductor = tarifas_dict['conductor'].get(origen, {}).get(destino, {}).get(tipo_estandarizado)
        
        # Obtener tarifas ajustadas
        tarifa_cliente = obtener_tarifa(tipo_vehiculo, origen, destino, disponibilidad, 'cliente')
        tarifa_conductor = obtener_tarifa(tipo_vehiculo, origen, destino, disponibilidad, 'conductor')
        
        if mostrar_detalles:
            print(f"\n=== Consulta de Tarifa ===")
            print(f"Ruta: {origen} → {destino}")
            print(f"Vehículo: {tipo_vehiculo}")
            print(f"Disponibilidad: {disponibilidad} vehículos")
            print(f"Precio Base Cliente: ${precio_base_cliente:,.0f}")
            print(f"Tarifa Cliente: ${tarifa_cliente:,.0f}")
            print(f"Precio Base Conductor: ${precio_base_conductor:,.0f}")
            print(f"Tarifa Conductor: ${tarifa_conductor:,.0f}")
            print(f"Margen: ${(tarifa_cliente - tarifa_conductor):,.0f}")
        
        return {
            'precio_base_cliente': precio_base_cliente,
            'precio_base_conductor': precio_base_conductor,
            'cliente': tarifa_cliente,
            'conductor': tarifa_conductor,
            'disponibilidad': disponibilidad,
            'margen': tarifa_cliente - tarifa_conductor
        }
    except Exception as e:
        print(f"Error al consultar tarifa: {str(e)}")
        return None

#  Mostrar resultados
# print("\nTarifas para Clientes desde Bogotá:")
# print(format_dataframe(df_tarifas_cliente))

# print("\nTarifas para Conductores desde Bogotá:")
# print(format_dataframe(df_tarifas_conductor))

# Opcional: Si quieres ver las columnas disponibles
# print("\nColumnas en DataFrame de clientes:")
# print(df_tarifas_cliente.columns)
# print("\nColumnas en DataFrame de conductores:")
# print(df_tarifas_conductor.columns)


ciudades_destino = ['VALLEDUPAR', 'CALI', 'BARRANQUILLA']
for destino in ciudades_destino:
    consultar_tarifa_especifica('BOGOTA', destino, 'Turbo')