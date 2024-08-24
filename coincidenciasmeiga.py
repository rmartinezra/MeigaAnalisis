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

    chunk_size = 10**6
    df = pd.DataFrame()

    # Lectura del archivo CSV en chunks
    for chunk in tqdm.tqdm(pd.read_csv(nombre_archivo, chunksize=chunk_size), desc="Procesando CSV", unit="chunk"):
        df = pd.concat([df, chunk])
        del chunk
        gc.collect()

    # Definir los nombres de las columnas de los canales según la estructura ch00-ch59
    ch_columns = [f'ch{i:02d}' for i in range(60)]

    # Crear DataFrames para almacenar coincidencias de activaciones
    coincidencias_df_ch00_ch14_vs_ch15_ch29 = pd.DataFrame(index=ch_columns[:15], columns=ch_columns[15:30], data=0)
    coincidencias_df_ch30_ch44_vs_ch45_ch59 = pd.DataFrame(index=ch_columns[30:45], columns=ch_columns[45:], data=0)

    # Iterar sobre todas las combinaciones posibles de pares de canales ch00-ch14 vs ch15-ch29
    for ch1, ch2 in tqdm.tqdm(product(ch_columns[:15], ch_columns[15:30]), desc="Calculando coincidencias ch00-ch14 vs ch15-ch29"):
        # Filtrar el DataFrame para eventos donde ambos canales están activados
        df_filtrado = df[(df[ch1] != 0) & (df[ch2] != 0)]

        # Contar el número de eventos donde ambos canales están activados simultáneamente
        num_coincidencias = len(df_filtrado)

        # Guardar el número de coincidencias en el DataFrame de coincidencias
        coincidencias_df_ch00_ch14_vs_ch15_ch29.loc[ch1, ch2] = num_coincidencias

    # Iterar sobre todas las combinaciones posibles de pares de canales ch30-ch44 vs ch45-ch59
    for ch1, ch2 in tqdm.tqdm(product(ch_columns[30:45], ch_columns[45:]), desc="Calculando coincidencias ch30-ch44 vs ch45-ch59"):
        # Filtrar el DataFrame para eventos donde ambos canales están activados
        df_filtrado = df[(df[ch1] != 0) & (df[ch2] != 0)]

        # Contar el número de eventos donde ambos canales están activados simultáneamente
        num_coincidencias = len(df_filtrado)

        # Guardar el número de coincidencias en el DataFrame de coincidencias
        coincidencias_df_ch30_ch44_vs_ch45_ch59.loc[ch1, ch2] = num_coincidencias
        
    # Crear DataFrame para almacenar coincidencias de cuaternas de activaciones
    cuaternas_indices = []
    for ch1, ch2, ch3, ch4 in tqdm.tqdm(product(ch_columns[:15], ch_columns[15:30], ch_columns[30:45], ch_columns[45:]), desc="Generando combinaciones válidas"):
        if not df.empty:
            if df[(df[ch1] != 0) & (df[ch2] != 0) & (df[ch3] != 0) & (df[ch4] != 0)].empty:
                continue
            cuaternas_indices.append((ch1, ch2, ch3, ch4))

    coincidencias_df_cuaternas = pd.DataFrame(index=pd.MultiIndex.from_tuples(cuaternas_indices, names=['Ch00-14', 'Ch15-29', 'Ch30-44', 'Ch45-59']), columns=['Frecuencia'], data=0)

    # Iterar sobre las combinaciones válidas de cuaternas de canales
    for ch1, ch2, ch3, ch4 in tqdm.tqdm(cuaternas_indices, desc="Calculando coincidencias de cuaternas"):
        try:
            # Filtrar el DataFrame para eventos donde todos los cuatro canales están activados
            df_filtrado = df[(df[ch1] != 0) & (df[ch2] != 0) & (df[ch3] != 0) & (df[ch4] != 0)]

            # Contar el número de eventos donde la cuaterna de canales está activada simultáneamente
            num_coincidencias = len(df_filtrado)

            # Guardar la frecuencia de coincidencias en el DataFrame de coincidencias de cuaternas
            coincidencias_df_cuaternas.loc[(ch1, ch2, ch3, ch4), 'Frecuencia'] = num_coincidencias
        except KeyError:
           # Manejo de combinaciones no encontradas
            print(f"Combinación no encontrada: ({ch1}, {ch2}, {ch3}, {ch4})")

    # Guardar el DataFrame de coincidencias de cuaternas como CSV
    coincidencias_df_cuaternas.reset_index().to_csv(os.path.join(directorio_graficas, 'coincidencias_cuaternas_activaciones.csv'), index=False)

    # Reestructurar el DataFrame para el heatmap
    coincidencias_heatmap_df = coincidencias_df_cuaternas['Frecuencia'].unstack(level=[0, 1])

    # Crear el heatmap de las coincidencias de cuaternas seleccionadas
    plt.figure(figsize=(24, 18))
    sns.heatmap(coincidencias_heatmap_df, cmap='viridis', annot=False, fmt='.0f', linewidths=.1)
    plt.title(f'Frecuencia de Coincidencias para Cuaternas de Canales - {nombre_base}')
    plt.xlabel('Pares de Canales (ch30:ch44, ch45:ch59)')
    plt.ylabel('Pares de Canales (ch00:ch14, ch15:ch29)')

    plt.tight_layout()
    plt.savefig(os.path.join(directorio_graficas, 'heatmap_coincidencias_cuaternas.png'))
    plt.close()

    gc.collect()

    # Guardar los DataFrames de coincidencias como CSV
    coincidencias_df_ch00_ch14_vs_ch15_ch29.to_csv(os.path.join(directorio_graficas, 'coincidencias_activaciones_ch00_ch14_vs_ch15_ch29.csv'))
    coincidencias_df_ch30_ch44_vs_ch45_ch59.to_csv(os.path.join(directorio_graficas, 'coincidencias_activaciones_ch30_ch44_vs_ch45_ch59.csv'))

    # Filtrar eventos con al menos 4 canales activados
    df_filtrado_4_canales = df[(df[ch_columns[:60]] != 0).sum(axis=1) >= 4]

    # Guardar el DataFrame filtrado en CSV
    df_filtrado_4_canales.to_csv(os.path.join(directorio_graficas, 'eventos_con_al_menos_4_canales_activados.csv'), index=False)

    # Crear los heatmaps de las coincidencias seleccionadas
    plt.figure(figsize=(18, 12))

    plt.subplot(1, 2, 1)
    sns.heatmap(coincidencias_df_ch00_ch14_vs_ch15_ch29, annot=True, cmap='viridis', fmt='d', linewidth=.1)
    plt.title(f'Coincidencias de Activaciones entre Pares de Canales (ch00-ch14 vs ch15-ch29) - {nombre_base}')
    plt.xlabel('Canales ch15-ch29')
    plt.ylabel('Canales ch00-ch14')

    plt.subplot(1, 2, 2)
    sns.heatmap(coincidencias_df_ch30_ch44_vs_ch45_ch59, annot=True, cmap='viridis', fmt='d', linewidth=.1)
    plt.title(f'Coincidencias de Activaciones entre Pares de Canales (ch30-ch44 vs ch45-ch59) - {nombre_base}')
    plt.xlabel('Canales ch45-ch59')
    plt.ylabel('Canales ch30-ch44')

    plt.tight_layout()
    plt.savefig(os.path.join(directorio_graficas, 'heatmaps_coincidencias_seleccionados.png'))
    plt.close()

    del df
    gc.collect()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python coincidenciasmeiga.py <nombre_del_archivo_csv>")
    else:
        nombre_archivo = sys.argv[1]
        procesar_csv(nombre_archivo)


