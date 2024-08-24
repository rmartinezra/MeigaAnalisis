import json
import csv
import os
import sys
from tqdm import tqdm

def parse_binary_counter(binary_counter):
    # Function to parse the binary counter string into channel values
    return [int(bit) for bit in binary_counter]  # List comprehension for efficiency

def procesar_datos_meiga(input_file):
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    unified_data = []
    
    events = list(data['Output'].items())
    
    for event, event_data in tqdm(events, desc="Procesando eventos", ncols=100):
        if len(event_data) != 2:
            continue
        
        # Obtener los datos de los detectores
        detector_0_data = event_data['Detector_0']
        detector_1_data = event_data['Detector_1']
        
        # Extraer los valores del BinaryCounter de cada detector
        try:
            binary_counter_0 = detector_0_data['BinaryCounter']
            binary_counter_1 = detector_1_data['BinaryCounter']
        except KeyError as e:
            print(f"Error: KeyError - '{e}' not found in detector data.")
            continue
        
        # Parse binary counters into channel lists
        channels_0 = parse_binary_counter(binary_counter_0)
        channels_1 = parse_binary_counter(binary_counter_1)
        
        # Combine channels as required (ch00-ch59)
        unified_row = [int(event.split('_')[-1])] + channels_0 + channels_1
        
        # Agregar la fila unificada a los datos finales
        unified_data.append(unified_row)
    
    # Crear nombre de archivo de salida basado en el nombre del archivo de entrada
    output_file = f"{os.path.splitext(input_file)[0]}_output_meiga.csv"
    
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Escribir encabezados
        headers = ['event'] + [f'ch{i:02d}' for i in range(60)]
        csvwriter.writerow(headers)
        
        # Escribir filas de datos
        csvwriter.writerows(unified_data)  # Escribir todas las filas de una vez
    
    print(f"Archivo CSV generado: {output_file}")

if __name__ == "__main__":
    # Verificar que se haya proporcionado un argumento de archivo
    if len(sys.argv) != 2:
        print("Uso: python3 script.py <ruta_al_archivo_json>")
        sys.exit(1)
    
    # Obtener la ruta del archivo JSON desde los argumentos de línea de comandos
    input_file = sys.argv[1]
    procesar_datos_meiga(input_file)


