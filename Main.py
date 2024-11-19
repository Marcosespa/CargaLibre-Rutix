def mostrar_menu():
    print("\n=== CARGA LIBRE RUTIX - MENÚ PRINCIPAL ===")
    print("1. Manejador Web")
    print("2. Unión de Archivos")
    print("3. Modelo de Precios")
    print("4. Salir")

def ejecutar_manejador_web():
    try:
        from ManejadorWeb import leer_excel
        ruta_archivo = input("\nIngrese la ruta del archivo Excel: ")
        if leer_excel(ruta_archivo):
            print("\nProceso completado exitosamente.")
        else:
            print("\nEl proceso no se completó correctamente.")
    except Exception as e:
        print(f"Error en el Manejador Web: {str(e)}")

def ejecutar_union_archivos():
    try:
        ruta_satrack = input("\nIngrese la ruta del archivo Satrack: ")
        ruta_original = input("Ingrese la ruta del archivo original: ")
        ruta_salida = input("Ingrese la ruta para guardar el archivo actualizado: ")
        
        import pandas as pd
        
        # Leer los archivos
        df_satrack = pd.read_excel(ruta_satrack)
        df_original = pd.read_excel(ruta_original)
        
        # Normalizar placas
        df_satrack['PLACA'] = df_satrack['PLACA'].str.strip().str.upper()
        df_original['PLACA'] = df_original['PLACA'].str.strip().str.upper()
        
        # Crear las nuevas columnas en df_original
        df_original['LATITUD'] = None
        df_original['LONGITUD'] = None
        
        # Actualizar coordenadas
        for index, row in df_satrack.iterrows():
            mask = df_original['PLACA'] == row['PLACA']
            if mask.any():
                df_original.loc[mask, 'LATITUD'] = row['LATITUD']
                df_original.loc[mask, 'LONGITUD'] = row['LONGITUD']
        
        # Guardar archivo
        df_original.to_excel(ruta_salida, index=False)
        print(f"\nArchivo guardado exitosamente en: {ruta_salida}")
        
    except Exception as e:
        print(f"Error en la Unión de Archivos: {str(e)}")

def ejecutar_modelo_precios():
    try:
        from ModeloPrecios import consultar_tarifa_especifica
        while True:
            print("\n=== MODELO DE PRECIOS ===")
            print("1. Consultar tarifa específica")
            print("2. Volver al menú principal")
            
            sub_opcion = input("\nSeleccione una opción (1-2): ")
            
            if sub_opcion == "1":
                origen = input("\nCiudad de origen: ").upper()
                destino = input("Ciudad de destino: ").upper()
                print("\nTipos de vehículo disponibles:")
                print("- Turbo")
                print("- Sencillo")
                print("- Mini Mula")
                print("- Tracto Mula")
                tipo_vehiculo = input("\nTipo de vehículo: ")
                consultar_tarifa_especifica(origen, destino, tipo_vehiculo)
            
            elif sub_opcion == "2":
                break
            
            else:
                print("\nOpción no válida. Por favor, seleccione 1 o 2.")
                
    except Exception as e:
        print(f"Error en el Modelo de Precios: {str(e)}")

def main():
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione una opción (1-4): ")
        
        if opcion == "1":
            ejecutar_manejador_web()
        
        elif opcion == "2":
            ejecutar_union_archivos()
        
        elif opcion == "3":
            ejecutar_modelo_precios()
        
        elif opcion == "4":
            print("\n¡Gracias por usar CargaLibre Rutix!")
            break
        
        else:
            print("\nOpción no válida. Por favor, seleccione una opción entre 1 y 4.")

if __name__ == "__main__":
    main()
