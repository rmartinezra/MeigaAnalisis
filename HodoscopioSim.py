import json
import csv
import os

def parse_binary_counter(binary_counter):
    # Function to parse the binary counter string into channel values
    # Assuming each channel value is represented by a bit in the string
    channels = []
    for i in range(len(binary_counter)):
        channels.append(int(binary_counter[i]))  # Convert each character to an integer
    
    return channels

def procesar_datos_meiga(input_file):
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    unified_data = []
    
    for event, event_data in data['Output'].items():
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
        unified_row = [int(event.split('_')[-1])] + channels_0[:30] + channels_0[30:] + channels_1
        
        # Agregar la fila unificada a los datos finales
        unified_data.append(unified_row)
    
    # Escribir los datos unificados a un archivo CSV en el directorio actual
    output_file = 'output_meiga.csv'
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Escribir encabezados
        headers = ['event'] + [f'ch{i:02d}' for i in range(60)]
        csvwriter.writerow(headers)
        
        # Escribir filas de datos
        for row in unified_data:
            csvwriter.writerow(row)
    
    print(f"Archivo CSV generado: {output_file}")

if __name__ == "__main__":
    # Usar el nombre del archivo JSON directamente si está en el mismo directorio
    input_file = 'output_00.json'
    procesar_datos_meiga(input_file)



