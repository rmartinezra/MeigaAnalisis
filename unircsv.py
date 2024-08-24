import pandas as pd
import glob
import os
import argparse

def main(carpeta):
    # Obtener la lista de archivos CSV en la carpeta
    archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))

    # Verificar si se encontraron archivos CSV
    if not archivos_csv:
        print("No se encontraron archivos CSV en la carpeta especificada.")
        return

    # Leer y cargar cada archivo CSV en un DataFrame
    dataframes = []
    for archivo in archivos_csv:
        try:
            # Especificar la codificación 'utf-8' o 'latin-1' según sea necesario
            df = pd.read_csv(archivo, encoding='utf-8')
            dataframes.append(df)
        except Exception as e:
            print(f"Error al leer archivo {archivo}: {str(e)}")

    # Concatenar todos los DataFrames en uno solo
    try:
        if dataframes:
            df_concatenado = pd.concat(dataframes, ignore_index=True)
            # Guardar el DataFrame concatenado en un nuevo archivo CSV
            df_concatenado.to_csv(os.path.join(carpeta, 'archivo_concatenado.csv'), index=False)
            print("Archivos CSV concatenados exitosamente.")
        else:
            print("No se pudieron leer los archivos CSV.")
    except Exception as e:
        print(f"Error al concatenar DataFrames: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Concatenar archivos CSV en una carpeta.')
    parser.add_argument('carpeta', type=str, help='Ruta a la carpeta que contiene los archivos CSV')
    args = parser.parse_args()

    main(args.carpeta)
