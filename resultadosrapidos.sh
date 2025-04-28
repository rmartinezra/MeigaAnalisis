#!/bin/bash
# Script para contar las líneas del archivo "eventos_con_al_menos_4_canales_activados.csv"
# en cada carpeta que sigue el patrón graficas_output_*_output_meiga y guardar la salida en resultado.txt

output_file="resultado.txt"

# Vaciar el archivo de salida si ya existe
> "$output_file"

for carpeta in graficas_output_*_output_meiga; do
    # Verifica que el archivo exista en la carpeta actual
    if [ -f "$carpeta/eventos_con_al_menos_4_canales_activados.csv" ]; then
        echo "Procesando carpeta: $carpeta" >> "$output_file"
        wc -l "$carpeta/eventos_con_al_menos_4_canales_activados.csv" >> "$output_file"
    else
        echo "Archivo no encontrado en $carpeta" >> "$output_file"
    fi
done

echo "Resultados guardados en $output_file"

