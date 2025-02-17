#!/bin/bash

# Criar pastas necessárias apenas se não existirem
for dir in "./output/site/mapas/cobertura/" "./output/site/mapas/equipe/" "./output/site/mapas/densidade/"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir" && echo "Pasta criada: $dir" || echo "Erro ao criar pasta: $dir"
    else
        echo "Pasta já existe: $dir"
    fi
done

OUTPUT_FILE="shapes/setores_ligth_processado.gpkg"

echo "Unindo arquivos em $OUTPUT_FILE..."
cat shapes/setores_ligth_processado_part_* > "$OUTPUT_FILE"
#rm -f shapes/setores_ligth_processado_part_*  # Remove as partes após a reconstrução
echo "Arquivo reconstruído com sucesso: $OUTPUT_FILE"

echo "Reconstruindo arquivo shapes/setores_light_densidade.gpkg..."
cat shapes/setores_light_densidade_part_* > shapes/setores_light_densidade.gpkg
#rm -f shapes/setores_light_densidade_part_*  # Remove as partes após a reconstrução
echo "Arquivo reconstruído com sucesso: shapes/setores_light_densidade.gpkg"

echo "Reconstruindo arquivos de distâncias..."

cat dados/distancias/BR_part_* > dados/distancias/BR.parquet
#rm -f dados/distancias/BR_part_*  # Remove as partes após a reconstrução
echo "Arquivo reconstruído: dados/distancias/BR.parquet"

cat dados/distancias/SP_part_* > dados/distancias/SP.parquet
#rm -f dados/distancias/SP_part_*  # Remove as partes após a reconstrução
echo "Arquivo reconstruído: dados/distancias/SP.parquet"

echo "Todos os arquivos foram reconstruídos com sucesso!"
