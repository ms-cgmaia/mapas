
'''

Este script produz os mapas de cobertua da APS

Entradas (dados necessários):

distancias = pd.read_parquet(f'./dados/distancias/{UF}.parquet')
estados = gpd.read_file('./shapes/BR_UF_2022.gpkg')
setores = gpd.read_file('./shapes/setores_ligth_processado.gpkg')
unidades = gpd.read_file('./shapes/unidades_processado.gpkg')

Saídas:
Mapas de um estado ou de todos no caminho: ./output/site/mapas/cobertura/

Executando:

python3 /scripts/cobertura_aps.py AC --export True/False -> gera de um estado específico
python3 /scripts/cobertura_aps.py --export True/False -> gera de todo o Brasil

'''

import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import pandas as pd
pd.set_option('display.max_columns', 200)
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster
import locale
locale.setlocale(locale.LC_ALL, '')
from shapely import Point
from tqdm import tqdm
import argparse
from geopy.distance import geodesic
import importlib
import sys
import importlib
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
import utils
importlib.reload(utils)
from utils import get_unidades, get_setores, co_uf_ibge, sg_uf_ibge, custom_scrollbar_css, gera_mapa_densidade, create_box

setores = gpd.read_file('./shapes/setores_ligth_processado.gpkg')
setores.columns = [col.lower() for col in setores.columns]

unidades = gpd.read_file('./shapes/unidades_processado.gpkg')

def get_distancias(UF):
    distancias = pd.read_parquet(f'./dados/distancias/{UF}.parquet').rename(columns={'CD_SETOR': 'ID_SETOR'})
    return distancias.sort_values(by=['CO_CNES','distancia'], ascending=True).reset_index(drop=True)
    #estabelecimentos = unidades.loc[unidades.id_setor.isin(distancias.CD_SETOR)]
    #merged_df = estabelecimentos.merge(distancias, on=['CO_MUNICIPIO', 'CO_CNES'], how='left')
    #merged_df.columns = [col.lower() for col in merged_df.columns]
    #return merged_df[['CO_MUNICIPIO','CO_CNES','ID_SETOR','distancia']].dropna().sort_values(by=['CO_CNES','distancia'], ascending=True).reset_index(drop=True)

def distribuir_cadastros(cnes_id, cadastros_disponiveis, distancias_ordenadas, setores_temp, ajuste=False):
    #print("CNES:", cnes_id)
    distancias_atuais = distancias_ordenadas[distancias_ordenadas["CO_CNES"] == cnes_id]
    
    if  distancias_atuais.empty: 
        return
    
    visitados = set()  # Para rastrear setores_temp já completamente preenchidos
    
    setores_alocados = {}
    
    for _, row in distancias_atuais.iterrows():
        if cadastros_disponiveis <= 0:
            break
        setor_atual = setores_temp[setores_temp["id_setor"] == row["ID_SETOR"]]
        
        id_setor_atual = setor_atual['id_setor'].values[0]
                    
        if id_setor_atual in visitados:
            continue

        if not setor_atual.empty:
            populacao_total = setor_atual["populacao"].values[0]
        else:
            print("Nenhum setor encontrado com o id_setor especificado.")
        
        populacao_captada = setor_atual['pop_captada'].values[0]
        populacao_restante = populacao_total - populacao_captada
        
        #print("Setor:", id_setor_atual, " restante:", populacao_restante, "populaçao total:", populacao_total, "captada", populacao_captada," restante cadastros:", cadastros_disponiveis, "distancia", row["distancia"])
    
        if cadastros_disponiveis >= populacao_restante:
            # Setor completamente preenchido
            setores_temp.loc[setores_temp['id_setor'] == str(id_setor_atual), 'pop_captada'] += populacao_restante
            cadastros_disponiveis -= populacao_restante
            setores_alocados[id_setor_atual] = populacao_restante
            visitados.add(id_setor_atual) 
        else:
            # Setor parcialmente preenchido
            setores_temp.loc[setores_temp['id_setor'] == str(id_setor_atual), 'pop_captada'] += cadastros_disponiveis

            setores_alocados[id_setor_atual] = cadastros_disponiveis
            cadastros_disponiveis = 0  # Todos os cadastros foram utilizados
            break
            
    return (cnes_id, setores_alocados)

def get_resultado(UF, ajustaCadastros = False):
    
    distancias = get_distancias(UF)
    estabelecimentos = unidades.loc[unidades.id_setor.isin(distancias.ID_SETOR)]
    
    processado = []

    municipios = tqdm(set(estabelecimentos.CO_MUNICIPIO))
    alocacao = []
    sem_cadastro = set()
    for municipio in municipios:
        
        ubs_temp = estabelecimentos.loc[estabelecimentos.CO_MUNICIPIO == municipio]
        setores_temp = setores.loc[setores.co_municipio == municipio]
        for _, row in ubs_temp.iterrows():
            retorno = distribuir_cadastros(row['CO_CNES'], row['PARAMETRO_TOTAL'], distancias, setores_temp)
            if retorno:
                alocacao.append((municipio, row['CADASTROS_TOTAIS'], retorno))
            else:
                # estabelecimento sem cadastros para distribuir
                sem_cadastro.add(row['CO_CNES'])
                pass
                #print(f"Não retornou nada: municipio: {municipio} usb: {row['CO_CNES']} cadastros:{row['PARAMETRO_TOTAL']}")
        processado.append(setores_temp)
    #print('Estabelecimentos sem cadastro:',len(sem_cadastro))
    # Resultado final
    resultado = pd.concat(processado)
    if ajustaCadastros:
        resultado['valor'] = resultado.pop_captada / resultado.populacao_ajustada
    else:
        resultado['valor'] = resultado.pop_captada / resultado.populacao
    #resultado = resultado.drop_duplicates()
    resultado = gpd.GeoDataFrame(resultado, geometry='geometry')
    resultado = resultado.set_crs(setores.crs)
    resultado['geoid'] = resultado.index.astype(str)
    #resultado[['id_setor', 'populacao', 'pop_captada', 'valor']]
    return resultado

def gera_mapa_cobertura(UF, export=False, ajustaCadastros=False):
    unidades = get_unidades(UF)
    unidades_cnes = unidades.groupby(['CO_CNES','NO_FANTASIA','NO_MUNICIPIO','NO_LOGRADOURO','DS_TIPO_UNIDADE']).agg({'CO_EQUIPE':list, 'TP_EQUIPE':list, 'CO_AREA':list, 'NO_REFERENCIA':list, 'CADASTROS_ACOMPANHADOS':list,'CADASTROS_VINCULADOS':list, 'CADASTROS_PREVINE':list, 'PARAMETRO_CADASTRAL':list, 'LATITUDE':'mean', 'LONGITUDE':'mean', 'DENTRO_MUNICIPIO':'max'}).reset_index()
    # Após juntar as médias das coordenadas (que deveriam ser iguais), a geometria é recalculada
    unidades_cnes['geometry'] = [Point(point[0],point[1]) for point in zip(unidades_cnes.LONGITUDE, unidades_cnes.LATITUDE)]
    setores = get_resultado(UF, ajustaCadastros)
    setores['valor_formatado'] = setores['valor'].apply(lambda x: f"{x:.2%}")
    #carrega o estado para colocar um contorno e definir o centro
    estados = gpd.read_file('./shapes/BR_UF_2022.gpkg')
    centroUF = estados.loc[estados.SIGLA == UF].geometry.centroid.values

    # Criando o mapa com tile de fundo
    map = folium.Map(location=[centroUF.y,centroUF.x], tiles = 'cartodbpositron', control_scale=True, prefer_canvas=True, zoom_start=11)
    # Cria p objeto marker cluster 
    marker_cluster = MarkerCluster(name="Unidades básicas de saúde")
    # cria os estabelecimentos
    for index, cnes in unidades_cnes.iterrows():
        caixa = create_box(cnes)
        folium.Marker([cnes.geometry.y, cnes.geometry.x], icon=folium.Icon(color="orange", icon="house-medical", prefix='fa'), popup=caixa, tooltip = cnes.NO_FANTASIA).add_to(marker_cluster)
    
    # Acrescentando os shapes
    # shape dos setores censitarios
    folium.Choropleth(
        geo_data=setores,
        name='Cobertura',
        data=setores,
        columns=['geoid', 'valor'],
        key_on='feature.id',
        fill_color='Blues',
        fill_opacity=0.8,
        line_opacity=0.5,
        line_color='black',
        line_weight=.5,
        smooth_factor=1.0,
        nan_fill_color = "White",
        legend_name= 'Percentual de cobertura'
        ).add_to(map)


    # Criando o layer com os tooltips por cima de tudo
    folium.features.GeoJson(setores, name='Informações dos setores',
        style_function = lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
        tooltip = folium.features.GeoJsonTooltip(fields=['populacao','pop_captada','valor_formatado'],
                                                aliases = ['População residente', 'População coberta', 'Percentual de cobertura'],
                                                labels=True, sticky=False),
        highlight_function = lambda x: {'fillColor': '#ffffff', 'color':'#ffffff', 'fillOpacity': .5, 'weight': 0.1}).add_to(map)

    # Criando o layer de contorno do estado
    #folium.features.GeoJson(estados.loc[estados.SIGLA == UF], name=UF, style_function = lambda x: {'fillColor': 'transparent', 'color':'steelblue', 'fillOpacity': 0, 'weight': 1,'dash_array':'2'}).add_to(map)    
    # Add the marker cluster to the map
    marker_cluster.add_to(map)

    folium.LayerControl().add_to(map)
    
    # Display/Export o mapa
    if export:
        output_dir = './output/site/mapas/cobertura/'
        os.makedirs(output_dir, exist_ok=True)
        map.save(f"{output_dir}{UF}.html")
        print("Mapa salvo em:", output_dir)
    return map

def gerar_mapas_cobertura_distancias(estado="", export=True):
    if estado != "":
        gera_mapa_cobertura(estado, export=export)
    else:
        for UF in tqdm(co_uf_ibge.keys()):
            gera_mapa_cobertura(UF, export=export)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerar mapas de cobertura de distâncias.")
    parser.add_argument(
        "estado", 
        type=str, 
        nargs="?",
        default="",
        help="Estado para gerar o mapa (passar sigla do estado, ex: 'AC')."
    )
    parser.add_argument(
        "--export", 
        type=bool, 
        default=True,
        help="Defina se o mapa deve ser exportado (True ou False)."
    )
    
    args = parser.parse_args()
    
    gerar_mapas_cobertura_distancias(args.estado, export=args.export)