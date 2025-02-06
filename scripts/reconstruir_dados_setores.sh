#!/bin/bash

# Nome do arquivo final
OUTPUT_FILE="shapes/setores_light.gpkg"

# Verifica se há arquivos divididos
PARTS=$(ls shapes/setores_part_* 2>/dev/null)

if [ -z "$PARTS" ]; then
    echo "Nenhum arquivo de partes encontrado em ./shapes/"
    exit 1
fi

# Junta os arquivos
echo "Unindo arquivos em $OUTPUT_FILE..."
cat shapes/setores_part_* > "$OUTPUT_FILE"

# Confirmação
echo "Arquivo reconstruído com sucesso: $OUTPUT_FILE"
