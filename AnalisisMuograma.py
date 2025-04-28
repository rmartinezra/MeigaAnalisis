#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

def extract_pixel(value, offset):
    """
    Convierte un valor de cadena (e.g. 'ch00') en número de píxel,
    restándole el offset correspondiente.
    """
    try:
        num = int(value.lower().replace("ch", ""))
        return num - offset
    except Exception:
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Unifica: (1) Traducción de canales a coordenadas, (2) Cálculo de flujo, "
                    "(3) Suavizado gaussiano del heatmap resultante."
    )
    # -----------------------------
    # Argumentos de entrada/salida
    # -----------------------------
    parser.add_argument("--input_csv",
                        required=True,
                        help="CSV de entrada con columnas: Ch00-14, Ch15-29, Ch30-44, Ch45-59, Frecuencia.")
    parser.add_argument("--output_flux_csv",
                        default="flux_data.csv",
                        help="Nombre del CSV final con la información de flux (tras la segunda etapa).")
    parser.add_argument("--output_heatmap_matrix",
                        default="flujo_heatmap_matrix.csv",
                        help="CSV con la matriz del heatmap antes de aplicar el suavizado gaussiano.")
    parser.add_argument("--output_heatmap_matrix_filled",
                        default="heatmap_filled.csv",
                        help="CSV con la matriz del heatmap tras el suavizado.")
    parser.add_argument("--output_image",
                        default="heatmap_filled.png",
                        help="Nombre de la imagen PNG final con el heatmap suavizado.")

    # -----------------------------
    # Parámetros del detector / tiempo
    # -----------------------------
    parser.add_argument("--time", type=float, required=True,
                        help="Tiempo total de adquisición en segundos [s]. (Por ej. 3600)")

    # Lado de píxel en cm
    parser.add_argument("--pixel_side", type=float, default=4.0,
                        help="Lado del píxel en cm (por defecto, 4.0).")
    # Distancia entre paneles en cm
    parser.add_argument("--distance_cm", type=float, default=100.0,
                        help="Distancia entre paneles en cm (por defecto, 100.0, es decir 1 m).")

    # -----------------------------
    # Parámetros del suavizado
    # -----------------------------
    parser.add_argument("--sigma", type=float, default=1.2,
                        help="Valor de sigma para el filtro gaussiano.")
    parser.add_argument("--truncate", type=float, default=6.0,
                        help="Número de sigmas hasta donde se toman vecinos en la interpolación.")

    # -----------------------------
    # Opciones del histograma
    # -----------------------------
    parser.add_argument("--num_bins", type=int, default=40,
                        help="Número de bins en cada eje (theta_x, theta_y) para el 2D-histogram.")

    args = parser.parse_args()

    # ================================================================
    # 1) TRADUCTOR: Leer CSV y traducir canales a coordenadas de píxel
    # ================================================================
    df_in = pd.read_csv(args.input_csv)

    # Extraer coordenadas (panel1_x, panel1_y, panel2_x, panel2_y)
    df_in['Panel1_x'] = df_in['Ch00-14'].apply(lambda x: extract_pixel(x, 0))
    df_in['Panel1_y'] = df_in['Ch15-29'].apply(lambda x: extract_pixel(x, 15))
    df_in['Panel2_x'] = df_in['Ch30-44'].apply(lambda x: extract_pixel(x, 30))
    df_in['Panel2_y'] = df_in['Ch45-59'].apply(lambda x: extract_pixel(x, 45))

    # Generar grid completo de combinaciones de 0..14 en cada coordenada
    coords = range(15)
    all_combos = pd.MultiIndex.from_product(
        [coords, coords, coords, coords],
        names=["Panel1_x", "Panel1_y", "Panel2_x", "Panel2_y"]
    )
    df_full = pd.DataFrame(index=all_combos).reset_index()

    # Combinar la información con la tabla original
    df_in_translated = df_in[['Panel1_x','Panel1_y','Panel2_x','Panel2_y','Frecuencia']]
    df_combined = pd.merge(df_full, df_in_translated,
                           on=["Panel1_x","Panel1_y","Panel2_x","Panel2_y"],
                           how="left")

    # Rellenar Frecuencia ausente con 1 (según indicaba traductor.py)
    df_combined['Frecuencia'] = df_combined['Frecuencia'].fillna(1).astype(int)

    # ============================================================
    # 2) FLUJO: Calcular la aceptancia y el flujo para cada r_{m,n}
    # ============================================================
    d = args.pixel_side
    A = d**2                # área de un píxel (cm^2)
    D_cm = args.distance_cm # distancia entre paneles en cm
    T_exp = args.time       # tiempo total de adquisición

    # Diferencia en píxeles
    df_combined["E_cm"] = np.sqrt(
        (df_combined["Panel2_x"] - df_combined["Panel1_x"])**2 +
        (df_combined["Panel2_y"] - df_combined["Panel1_y"])**2
    ) * d

    # r_{m,n} = sqrt(D^2 + E^2)
    df_combined["r_mn"] = np.sqrt(D_cm**2 + df_combined["E_cm"]**2)

    # Aceptancia T(r_{m,n}) = 4*A^2 / r_{m,n}^2
    df_combined["Acceptance"] = 4.0 * (A**2) / (df_combined["r_mn"]**2)

    # Flujo = Frecuencia / (Tiempo * Aceptancia)
    df_combined["Flux"] = df_combined["Frecuencia"] / (T_exp * df_combined["Acceptance"])

    # Angulos en x, y (grados)
    df_combined["Delta_x_cm"] = (df_combined["Panel2_x"] - df_combined["Panel1_x"]) * d
    df_combined["Delta_y_cm"] = (df_combined["Panel2_y"] - df_combined["Panel1_y"]) * d
    df_combined["Theta_x_deg"] = np.degrees(np.arctan(df_combined["Delta_x_cm"] / D_cm))
    df_combined["Theta_y_deg"] = np.degrees(np.arctan(df_combined["Delta_y_cm"] / D_cm))

    # Guardamos CSV con la info completa de flujo (opcional, según tus necesidades)
    df_combined.to_csv(args.output_flux_csv, index=False)
    print(f"CSV con datos de Flux guardado en: {args.output_flux_csv}")

    # ========================================================
    # 3) Construir el histograma 2D con pesos = 'Flux'
    # ========================================================
    angle_min, angle_max = -22, 22  # Rango típico (ajusta si gustas)
    x_edges = np.linspace(angle_min, angle_max, args.num_bins + 1)
    y_edges = np.linspace(angle_min, angle_max, args.num_bins + 1)

    # Histograma 2D sumando 'Flux' en cada bin
    hist2d_flux, xbins, ybins = np.histogram2d(
        df_combined["Theta_y_deg"],
        df_combined["Theta_x_deg"],
        bins=[y_edges, x_edges],
        weights=df_combined["Flux"]
    )

    # Guardar la matriz original (sin suavizar) en CSV
    #   - Filas => y (θy), Columnas => x (θx)
    y_centers = 0.5*(ybins[:-1] + ybins[1:])
    x_centers = 0.5*(xbins[:-1] + xbins[1:])

    df_heatmap = pd.DataFrame(hist2d_flux, index=y_centers, columns=x_centers)
    df_heatmap.index.name = "Theta_y_deg_center"
    df_heatmap.columns.name = "Theta_x_deg_center"
    df_heatmap.to_csv(args.output_heatmap_matrix)
    print(f"Matriz del heatmap (sin suavizar) guardada en: {args.output_heatmap_matrix}")

    # ========================================================
    # 4) "Completado": Filtro Gaussiano para suavizar
    # ========================================================
    # Se aplica un filtro gaussiano sobre la matriz hist2d_flux
    hist2d_flux_filled = gaussian_filter(
        hist2d_flux,
        sigma=args.sigma,
        mode='nearest',
        truncate=args.truncate
    )

    # Convertimos en DataFrame para guardarlo
    df_heatmap_filled = pd.DataFrame(hist2d_flux_filled, index=y_centers, columns=x_centers)
    df_heatmap_filled.index.name = "Theta_y_deg_center"
    df_heatmap_filled.columns.name = "Theta_x_deg_center"
    df_heatmap_filled.to_csv(args.output_heatmap_matrix_filled)
    print(f"Matriz suavizada guardada en: {args.output_heatmap_matrix_filled}")


# ========================================================
# Graficar el heatmap SIN suavizar (tal cual, sin interpolar)
# ========================================================
    plt.figure(figsize=(8,6))
    img = plt.imshow(
    hist2d_flux,
    origin='lower',
    aspect='auto',
    cmap='jet',
    extent=[x_centers.min(), x_centers.max(), y_centers.min(), y_centers.max()]
    )
     # Barra de color
    cbar_raw = plt.colorbar(img)
    cbar_raw.set_label("Cnts", fontsize=18)
    cbar_raw.ax.tick_params(labelsize=14)

    # Definir los ticks para que incluya -20 y 20
    tick_positions = np.arange(-20, 21, 5)  # -20, -15, -10, ..., 15, 20
    plt.xticks(tick_positions, fontsize=14)
    plt.yticks(tick_positions, fontsize=14)

    # Ejes con LaTeX y fuentes grandes
    plt.xlabel(r"$\theta_x \;(\mathrm{deg})$", fontsize=18)
    plt.ylabel(r"$\theta_y \;(\mathrm{deg})$", fontsize=18)


    plt.tight_layout()
    plt.savefig("flux_no_smoothing.png", dpi=300)
    print("Saved the no-smoothing heatmap: flux_no_smoothing.png")
    # ========================================================
    # 5) Graficar el heatmap suavizado y guardarlo
    # ========================================================
    plt.figure(figsize=(8,6))
    plt.imshow(df_heatmap_filled.values,
               origin='lower',
               aspect='auto',
               cmap='jet',
               extent=[x_centers.min(), x_centers.max(),
                       y_centers.min(), y_centers.max()])
    cbar = plt.colorbar()
    cbar.set_label("Flujo (suavizado)")
    plt.xlabel("Theta_x_deg_center")
    plt.ylabel("Theta_y_deg_center")
    plt.title("Flujo Angular Suavizado (Filtro Gaussiano)")
    plt.tight_layout()
    plt.savefig(args.output_image, dpi=300)
    print(f"Heatmap suavizado guardado en: {args.output_image}")

if __name__ == "__main__":
    main()
