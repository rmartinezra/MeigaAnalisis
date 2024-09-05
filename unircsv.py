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
    df_acumulado = None
    for archivo in archivos_csv:
        try:
            # Especificar la codificación 'utf-8' o 'latin-1' según sea necesario
            df = pd.read_csv(archivo, encoding='utf-8')
            # Agrupar por las columnas que representan las combinaciones y sumar las frecuencias
            df_grouped = df.groupby(list(df.columns[:-1]), as_index=False).sum()
            if df_acumulado is None:
                df_acumulado = df_grouped
            else:
                df_acumulado = pd.concat([df_acumulado, df_grouped]).groupby(list(df.columns[:-1]), as_index=False).sum()
        except Exception as e:
            print(f"Error al leer archivo {archivo}: {str(e)}")

    # Guardar el DataFrame acumulado en un nuevo archivo CSV
    try:
        if df_acumulado is not None:
            df_acumulado.to_csv(os.path.join(carpeta, 'archivo_concatenado_sumado.csv'), index=False)
            print("Archivos CSV sumados y concatenados exitosamente.")
        else:
            print("No se pudieron leer los archivos CSV.")
    except Exception as e:
        print(f"Error al guardar el archivo concatenado: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Concatenar y sumar frecuencias de archivos CSV en una carpeta.')
    parser.add_argument('carpeta', type=str, help='Ruta a la carpeta que contiene los archivos CSV')
    args = parser.parse_args()

    main(args.carpeta)

