#!/bin/bash

# Reconstrução do arquivo shapes/setores_ligth_processado.gpkg
OUTPUT_FILE="shapes/setores_ligth_processado.gpkg"

# Junta os arquivos do shapes
echo "Unindo arquivos em $OUTPUT_FILE..."
cat shapes/setores_ligth_processado_part_* > "$OUTPUT_FILE"
#rm -f shapes/setores_ligth_processado_part_*  # Remove as partes após a reconstrução
echo "Arquivo reconstruído com sucesso: $OUTPUT_FILE"

# Reconstrução dos arquivos de distâncias
echo "Reconstruindo arquivos de distâncias..."

cat dados/distancias/BR_part_* > dados/distancias/BR.parquet
#rm -f dados/distancias/BR_part_*  # Remove as partes após a reconstrução
echo "Arquivo reconstruído: dados/distancias/BR.parquet"

cat dados/distancias/SP_part_* > dados/distancias/SP.parquet
#rm -f dados/distancias/SP_part_*  # Remove as partes após a reconstrução
echo "Arquivo reconstruído: dados/distancias/SP.parquet"

echo "Todos os arquivos foram reconstruídos com sucesso!"
