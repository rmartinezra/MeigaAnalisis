import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tqdm
import gc
from itertools import product

def procesar_csv(nombre_archivo):
    nombre_base = os.path.splitext(os.path.basename(nombre_archivo))[0]
    directorio_graficas = f"graficas_{nombre_base}"
    os.makedirs(directorio_graficas, exist_ok=True)

    chunk_size = 10**5
    df = pd.DataFrame()

    # Lectura del archivo CSV en chunks
    print("Leyendo el archivo CSV en chunks...")
    for chunk in tqdm.tqdm(pd.read_csv(nombre_archivo, chunksize=chunk_size), desc="Procesando CSV", unit="chunk"):
        df = pd.concat([df, chunk], ignore_index=True)
        del chunk
        gc.collect()

    print("Archivo CSV leído completamente.")

    # Definir los nombres de las columnas de los canales según la estructura ch00-ch59
    ch_columns = [f'ch{i:02d}' for i in range(60)]

    # Crear DataFrames para almacenar coincidencias de activaciones
    coincidencias_df_ch00_ch14_vs_ch15_ch29 = pd.DataFrame(index=ch_columns[:15], columns=ch_columns[15:30], data=0)
    coincidencias_df_ch30_ch44_vs_ch45_ch59 = pd.DataFrame(index=ch_columns[30:45], columns=ch_columns[45:], data=0)

    print("Calculando coincidencias de activaciones ch00-ch14 vs ch15-ch29...")
    # Iterar sobre todas las combinaciones posibles de pares de canales ch00-ch14 vs ch15-ch29
    for ch1, ch2 in tqdm.tqdm(product(ch_columns[:15], ch_columns[15:30]), desc="Calculando coincidencias ch00-ch14 vs ch15-ch29", total=len(ch_columns[:15]) * len(ch_columns[15:30])):
        # Filtrar el DataFrame para eventos donde ambos canales están activados
        df_filtrado = df[(df[ch1] != 0) & (df[ch2] != 0)]

        # Contar el número de eventos donde ambos canales están activados simultáneamente
        num_coincidencias = len(df_filtrado)

        # Guardar el número de coincidencias en el DataFrame de coincidencias
        coincidencias_df_ch00_ch14_vs_ch15_ch29.loc[ch1, ch2] = num_coincidencias

    print("Coincidencias de activaciones ch00-ch14 vs ch15-ch29 calculadas.")

    print("Calculando coincidencias de activaciones ch30-ch44 vs ch45-ch59...")
    # Iterar sobre todas las combinaciones posibles de pares de canales ch30-ch44 vs ch45-ch59
    for ch1, ch2 in tqdm.tqdm(product(ch_columns[30:45], ch_columns[45:]), desc="Calculando coincidencias ch30-ch44 vs ch45-ch59", total=len(ch_columns[30:45]) * len(ch_columns[45:])):
        # Filtrar el DataFrame para eventos donde ambos canales están activados
        df_filtrado = df[(df[ch1] != 0) & (df[ch2] != 0)]

        # Contar el número de eventos donde ambos canales están activados simultáneamente
        num_coincidencias = len(df_filtrado)

        # Guardar el número de coincidencias en el DataFrame de coincidencias
        coincidencias_df_ch30_ch44_vs_ch45_ch59.loc[ch1, ch2] = num_coincidencias

    print("Coincidencias de activaciones ch30-ch44 vs ch45-ch59 calculadas.")

    # Guardar los DataFrames de coincidencias como CSV
    print("Guardando DataFrames de coincidencias como CSV...")
    coincidencias_df_ch00_ch14_vs_ch15_ch29.to_csv(os.path.join(directorio_graficas, 'coincidencias_activaciones_ch00_ch14_vs_ch15_ch29.csv'))
    coincidencias_df_ch30_ch44_vs_ch45_ch59.to_csv(os.path.join(directorio_graficas, 'coincidencias_activaciones_ch30_ch44_vs_ch45_ch59.csv'))
    print("DataFrames de coincidencias guardados.")

    # Crear los heatmaps de las coincidencias seleccionadas
    print("Creando heatmaps de coincidencias seleccionadas...")
    plt.figure(figsize=(18, 12))

    plt.subplot(1, 2, 1)
    sns.heatmap(coincidencias_df_ch00_ch14_vs_ch15_ch29, annot=True, cmap='viridis', fmt='d', linewidths=.1)
    plt.title(f'Coincidencias de Activaciones entre Pares de Canales (ch00-ch14 vs ch15-ch29) - {nombre_base}')
    plt.xlabel('Canales ch15-ch29')
    plt.ylabel('Canales ch00-ch14')

    plt.subplot(1, 2, 2)
    sns.heatmap(coincidencias_df_ch30_ch44_vs_ch45_ch59, annot=True, cmap='viridis', fmt='d', linewidths=.1)
    plt.title(f'Coincidencias de Activaciones entre Pares de Canales (ch30-ch44 vs ch45-ch59) - {nombre_base}')
    plt.xlabel('Canales ch45-ch59')
    plt.ylabel('Canales ch30-ch44')

    plt.tight_layout()
    plt.savefig(os.path.join(directorio_graficas, 'heatmaps_coincidencias_seleccionados.png'))
    plt.close()
    print("Heatmaps creados y guardados.")

    del df
    gc.collect()
    print("Proceso completado.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python coincidenciasmeiga.py <nombre_del_archivo_csv>")
    else:
        nombre_archivo = sys.argv[1]
        procesar_csv(nombre_archivo)
