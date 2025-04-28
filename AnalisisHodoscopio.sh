#!/bin/bash
#Hacer en el directorio de los jobs
# Ruta donde están los scripts de Python
PYTHON_SCRIPTS_DIR="/opt/data/python_src/"

# Function to display usage information
usage() {
    echo "Usage: $0 -n <number_of_directories>"
    exit 1
}

# Parse command line options
while getopts ":n:" opt; do
    case $opt in
        n)
            num_dirs=$OPTARG
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            ;;
    esac
done

# Check if the number of directories was provided
if [ -z "$num_dirs" ]; then
    echo "Error: You must provide the number of directories with the -n flag."
    usage
fi

# Function to copy output JSON files from jobs directories (Paso 0)
copy_json_files() {
    local num_dirs=$1
    for i in $(seq -w 0 "$num_dirs"); do
        cp "../jobs/run_${i}/output_${i}.json" datos/ || printf "Error copying ../jobs/run_${i}/output_${i}.json\n" >&2
    done
}

# Function to remove out.log files from run directories (Paso 0)
remove_logs() {
    local num_dirs=$1
    for i in $(seq -w 0 "$num_dirs"); do
        rm "../jobs/run_${i}/out.log" || printf "Error deleting run_${i}/out.log\n" >&2
    done
}

# Medir el tiempo total de procesamiento
START_TIME=$(date +%s)

# 0. Paso 0: Copiar archivos JSON y eliminar logs
echo "Ejecutando paso 0: Copiar archivos JSON y eliminar logs..."
copy_json_files "$num_dirs"
remove_logs "$num_dirs"
wait
echo "Finalizó el paso 0."
# 1. Ejecutar el script `pruebalectura.py` en paralelo sobre archivos JSON
DIRECTORIO_JSON="datos"
SCRIPT_PYTHON_JSON="${PYTHON_SCRIPTS_DIR}/lectura.py"
echo "Ejecutando $SCRIPT_PYTHON_JSON sobre archivos .json..."
find "$DIRECTORIO_JSON" -name "*.json" | parallel -j 0 python3 "$SCRIPT_PYTHON_JSON" {}
wait
echo "Finalizó la ejecución de $SCRIPT_PYTHON_JSON sobre los archivos .json."

# 2. Ejecutar el script `coincidenciasmeiga.py` en paralelo sobre archivos CSV
DIRECTORIO_CSV="datos"
SCRIPT_PYTHON_CSV="${PYTHON_SCRIPTS_DIR}/coincidenciasmeiga.py"
echo "Ejecutando $SCRIPT_PYTHON_CSV sobre archivos .csv..."
find "$DIRECTORIO_CSV" -name "*.csv" | parallel -j 0 python3 "$SCRIPT_PYTHON_CSV" {}
wait
echo "Finalizó la ejecución de $SCRIPT_PYTHON_CSV sobre los archivos .csv."

# 3. Copiar y renombrar archivos coincidencias_cuaternas_activaciones.csv
DEST_DIR="coincidencias_cuaternas"
mkdir -p "$DEST_DIR"
echo "Copiando archivos coincidencias_cuaternas_activaciones.csv..."
for dir in graficas_output_*_output_meiga; do
    suffix=${dir#graficas_output_}
    suffix=${suffix%_output_meiga}

    src_file="${dir}/coincidencias_cuaternas_activaciones.csv"
    dest_file="${DEST_DIR}/coincidencias_cuaternas_activaciones_${suffix}.csv"

    if [[ -f "$src_file" ]]; then
        cp "$src_file" "$dest_file" || printf "Error al copiar %s\n" "$src_file" >&2
    else
        printf "Archivo no encontrado: %s\n" "$src_file" >&2
    fi
done

# Calcular y mostrar el tiempo total de procesamiento
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))
echo "Tiempo total de procesamiento: ${ELAPSED_TIME} segundos"
