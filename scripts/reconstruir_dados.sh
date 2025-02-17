#!/bin/bash

set -e  #interrompe a execução do script se ocorrer um erro

#verifica se o parâmetro de remoção foi passado
REMOVER=false
if [ "$1" = "True" ] || [ "$1" = "true" ]; then
    REMOVER=true
fi

#criar pastas necessárias para exportação dos mapas, caso não existam
for dir in "./output/site/mapas/cobertura/" "./output/site/mapas/equipe/" "./output/site/mapas/densidade/"; do
    if [ ! -d "$dir" ]; then
        if mkdir -p "$dir"; then
            echo "[OK] pasta criada: $dir"
        else
            echo "[ERRO] falha ao criar pasta: $dir" >&2
            exit 1
        fi
    else
        echo "[INFO] pasta já existe: $dir"
    fi
done

#reconstruindo os arquivos
reconstruir_arquivo() {
    local input_pattern=$1
    local output_file=$2
    local remover=$3
    
    echo "[INFO] reconstruindo $output_file..."
    if cat $input_pattern > "$output_file"; then
        if [ "$remover" = true ]; then
            rm -f $input_pattern
            echo "[OK] partes removidas após reconstrução: $input_pattern"
        fi
        echo "[OK] arquivo reconstruído com sucesso: $output_file"
    else
        echo "[ERRO] falha ao reconstruir $output_file" >&2
        exit 1
    fi
}

#reconstruindo os arquivos
reconstruir_arquivo "shapes/setores_ligth_processado_part_*" "shapes/setores_ligth_processado.gpkg" "$REMOVER"
reconstruir_arquivo "shapes/setores_light_densidade_part_*" "shapes/setores_light_densidade.gpkg" "$REMOVER"
reconstruir_arquivo "dados/distancias/BR_part_*" "dados/distancias/BR.parquet" "$REMOVER"
reconstruir_arquivo "dados/distancias/SP_part_*" "dados/distancias/SP.parquet" "$REMOVER"

echo "[SUCESSO] todos os arquivos foram reconstruídos com sucesso!"
