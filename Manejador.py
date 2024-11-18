import pandas as pd

def leer_excel(ruta_archivo):
    # Leer el archivo Excel
    try:
        # Leer el archivo Excel usando pandas
        df = pd.read_excel(ruta_archivo)
        
        # Iterar sobre cada fila del DataFrame
        for indice, fila in df.iterrows():
            print(f"Fila {indice + 1}:")
            # Imprimir cada columna de la fila
            for columna in df.columns:
                print(f"{columna}: {fila[columna]}")
            print("-" * 50)  # Separador entre filas
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'")
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")

# Ejemplo de uso
if __name__ == "__main__":
    ruta_archivo = "/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/BASE DE DATOS TERCERO.xls"  # Cambia esto por la ruta de tu archivo
    leer_excel(ruta_archivo)
