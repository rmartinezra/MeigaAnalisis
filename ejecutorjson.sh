#!/bin/bash

# Directorio donde están los archivos .json
DIRECTORIO="/ruta/a/tu/directorio"

# Script de Python que quieres ejecutar
SCRIPT_PYTHON="/ruta/a/tu/script.py"

# Usa GNU parallel para ejecutar el script Python en paralelo
find "$DIRECTORIO" -name "*.json" | parallel -j 0 python3 "$SCRIPT_PYTHON" {}
