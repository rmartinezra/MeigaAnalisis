#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    # 1) Leer matrices en CSV (fondo y otro)
    df_fondo = pd.read_csv("fondo.csv", index_col=0)
    df_otro  = pd.read_csv("flujo_heatmap_matrix.csv", index_col=0)

    # 2) Calcular diferencia relativa: (fondo - otro) / fondo
    df_diff = (df_fondo - df_otro) / df_fondo

    # 3) Crear niveles para la escala (21 niveles)
    vmin = df_diff.values.min()
    vmax = df_diff.values.max()
    levels = np.linspace(vmin, vmax, 41)

    # 4) Graficar heatmap
    plt.figure(figsize=(10, 8))  # Más grande para artículos
    
    # Forzamos el rango del extent a [-20, 20] en x e y,
    # suponiendo que quieres ver ese rango completo.
    # Ajusta si tus datos tienen un rango distinto.
    extent = [-20, 20, -20, 20]

    # Mapa de calor. Transponemos df_diff para que coincida
    # con la forma en que quieres ver (fila <-> eje Y).
    # "interpolation" puede ser nearest, bilinear, bicubic, etc.
    img = plt.imshow(
        df_diff.values.T,
        origin='lower',
        aspect='auto',
        cmap=plt.get_cmap('jet', 21),
        vmin=0.05,
        vmax=vmax,
        extent=extent,
        interpolation='nearest'
    )

    # 5) Barra de color
    cbar = plt.colorbar(img, ticks=levels)
    # Etiqueta del colorbar
    cbar.set_label("Flux Attenuation", fontsize=18)
    # Aumentar tamaño de fuente en la barra de color
    cbar.ax.tick_params(labelsize=14)

    # 6) Ajustar los ejes x e y:
    # Definimos ticks manualmente si queremos incluir -20 y 20
    tick_positions = np.arange(-20, 21, 5)  # -20, -15, -10, ..., 15, 20
    plt.xticks(tick_positions, fontsize=14)
    plt.yticks(tick_positions, fontsize=14)

    # 7) Etiquetas en LaTeX
    plt.xlabel(r"$\theta_x \;(\mathrm{deg})$", fontsize=18)
    plt.ylabel(r"$\theta_y \;(\mathrm{deg})$", fontsize=18)


    plt.tight_layout()
    plt.savefig("diferencia_relativa_heatmap.png", dpi=600)
    print("Saved figure: diferencia_relativa_heatmap.png")

if __name__ == "__main__":
    main()
