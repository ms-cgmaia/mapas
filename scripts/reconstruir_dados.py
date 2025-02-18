import os
import glob
import shutil
import sys

# verifica se deve remover os arquivos temporários
REMOVER = len(sys.argv) > 1 and sys.argv[1].lower() == "true"

# criando pastas necessárias para exportação dos mapas, caso não existam
directories = [
    "./output/site/mapas/cobertura/",
    "./output/site/mapas/equipe/",
    "./output/site/mapas/densidade/",
]

for dir_path in directories:
    try:
        os.makedirs(dir_path, exist_ok=True)
        print(f"[OK] Pasta criada ou já existente: {dir_path}")
    except Exception as e:
        print(f"[ERRO] Falha ao criar pasta {dir_path}: {e}", file=sys.stderr)
        sys.exit(1)

# reconstruindo arquivos
def reconstruir_arquivo(input_pattern, output_file, remover):
    print(f"[INFO] Reconstruindo {output_file}...")

    input_files = sorted(glob.glob(input_pattern))
    if not input_files:
        print(f"[ERRO] Nenhuma parte encontrada para {output_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(output_file, "wb") as out_file:
            for file in input_files:
                with open(file, "rb") as in_file:
                    shutil.copyfileobj(in_file, out_file)
        
        print(f"[OK] Arquivo reconstruído com sucesso: {output_file}")

        if remover:
            for file in input_files:
                os.remove(file)
            print(f"[OK] Partes removidas após reconstrução: {input_pattern}")

    except Exception as e:
        print(f"[ERRO] Falha ao reconstruir {output_file}: {e}", file=sys.stderr)
        sys.exit(1)

# Reconstruindo os arquivos
reconstruir_arquivo("shapes/setores_ligth_processado_part_*", "shapes/setores_ligth_processado.gpkg", REMOVER)
reconstruir_arquivo("shapes/setores_light_densidade_part_*", "shapes/setores_light_densidade.gpkg", REMOVER)
reconstruir_arquivo("dados/distancias/BR_part_*", "dados/distancias/BR.parquet", REMOVER)
reconstruir_arquivo("dados/distancias/SP_part_*", "dados/distancias/SP.parquet", REMOVER)

print("[SUCESSO] Todos os arquivos foram reconstruídos com sucesso!")
