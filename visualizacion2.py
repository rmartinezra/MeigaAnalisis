import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

# Argumentos desde la línea de comandos
parser = argparse.ArgumentParser(description="Genera un heatmap a partir de un archivo CSV.")
parser.add_argument('filepath', type=str, help='Ruta al archivo CSV')
parser.add_argument('--vmin', type=int, default=0, help='Valor mínimo para el rango de color en el heatmap')
parser.add_argument('--vmax', type=int, default=100, help='Valor máximo para el rango de color en el heatmap')
args = parser.parse_args()

# Cargar el archivo CSV
def load_data(filepath):
    data = pd.read_csv(filepath)
    return data

# Extraer las columnas relevantes y calcular los ángulos
def preprocess_data(data):
    ch00_14 = data['Ch00-14'].apply(lambda x: int(x[2:]))
    ch15_29 = data['Ch15-29'].apply(lambda x: int(x[2:]))
    ch30_44 = data['Ch30-44'].apply(lambda x: int(x[2:]))
    ch45_59 = data['Ch45-59'].apply(lambda x: int(x[2:]))
    frecuencia = data['Frecuencia']
    
    d = 1.0  # Distancia entre los paneles (ajustable)
    theta_x = np.arctan((ch30_44 - ch00_14) / d)
    theta_y = np.arctan((ch45_59 - ch15_29) / d)
    
    return ch30_44, ch45_59, theta_x, theta_y, frecuencia, d

# Función para generar el mapa de calor
def create_heatmap(ch30_44, ch45_59, theta_x, theta_y, frecuencia, d):
    projected_x_initial = ch30_44 - np.tan(theta_x) * d
    projected_y_initial = ch45_59 - np.tan(theta_y) * d
    
    heatmap_data = pd.DataFrame({
        'Projected_X_initial': projected_x_initial,
        'Projected_Y_initial': projected_y_initial,
        'PosX_final': ch30_44,
        'PosY_final': ch45_59,
        'Frecuencia': frecuencia
    })
    
    pivot_data = heatmap_data.pivot_table(
        index='Projected_Y_initial', 
        columns='Projected_X_initial', 
        values='Frecuencia',
        aggfunc='sum',
        fill_value=0
    )
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_data, cmap='inferno', annot=False, vmin=args.vmin, vmax=args.vmax, fmt="d", linewidths=.5, cbar_kws={'label': 'Frecuencia de Eventos'})
    plt.title('Mapa de Calor de Trayectorias: Proyección y Posición Final')
    plt.xlabel('Proyección X Inicial')
    plt.ylabel('Proyección Y Inicial')
    plt.savefig('heatmap.png')  # Guardar el heatmap como imagen PNG
    plt.close()

# Ejecutar las funciones
data = load_data(args.filepath)
ch30_44, ch45_59, theta_x, theta_y, frecuencia, d = preprocess_data(data)
create_heatmap(ch30_44, ch45_59, theta_x, theta_y, frecuencia, d)


