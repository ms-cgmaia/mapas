import os
import pandas as pd
import geopandas as gpd
from shapely import Point
from tqdm import tqdm
from geopy.distance import geodesic 
import sys
import importlib
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
import utils
importlib.reload(utils)

from utils import sg_uf_ibge, co_uf_ibge

# base de setores do IBGE
setores = gpd.read_file('./shapes/setores_light.gpkg')
setores['SG_UF'] = setores.CD_UF.map(sg_uf_ibge)
setores = setores[['SG_UF','CD_MUN','CD_SETOR','geometry']]
setores['geometry'] = [geom.centroid for geom in setores['geometry']]
setores['CO_MUNICIPIO'] = [int(str(mun)[:6]) for mun in setores.CD_MUN]
del setores['CD_MUN']
setores = setores.drop_duplicates('CD_SETOR')
setores.head()

unidades = gpd.read_file('./shapes/unidades_cnes_realocadas.gpkg', driver='GPKG')
# Filtra as unidades da APS pelo tipo de equipe e tipo de unidade
unidades = unidades.loc[unidades.TP_EQUIPE.isin([70,71,72,73,74,76]) & unidades.TP_UNIDADE.isin([1,2,15,32,40,71])]
unidades = unidades.groupby(['SG_UF','CO_MUNICIPIO','CO_CNES']).agg({'LATITUDE':'mean', 'LONGITUDE':'mean'}).reset_index()
unidades['geometry'] = [Point(point[0],point[1]) for point in zip(unidades.LONGITUDE, unidades.LATITUDE)]

#função para calcular as distâncias
def gera_distancias_mun(municipio, limite=16):
    centroide_setores = setores.loc[setores.CO_MUNICIPIO == municipio]
    estabelecimentos = unidades.loc[unidades.CO_MUNICIPIO == municipio ]

    distancias = estabelecimentos.rename(columns={'geometry':'coord_ubs'}).merge(centroide_setores.rename(columns={'geometry':'coord_setor'}), how='cross')
    
    # Calculando as distancias
    distancias['distancia'] = [
        geodesic((ponto_ubs.y, ponto_ubs.x), (ponto_setor.y, ponto_setor.x)).km 
        for ponto_ubs, ponto_setor in zip(distancias['coord_ubs'], distancias['coord_setor'])
    ]
    distancias = distancias.loc[distancias.distancia<=limite]
    
    # Pegando apenas as colunas desejadas
    distancias = distancias[['CO_MUNICIPIO_x','CO_CNES','CD_SETOR','distancia']].rename(columns={'CO_MUNICIPIO_x':'CO_MUNICIPIO'})
    return distancias

# Lista para receber os dados gerados
dados = []

for UF in tqdm(co_uf_ibge.keys()):
    # Um limite de distância maior para os municípios da Amazônia Legal, por possuírem setores muito maiores que no restante do brasil
    if UF in ['AC','AP','AM','PA','MT','RR','RO','TO','MA']:
        limite = 32
    else:
        limite = 16
    for municipio in set(setores.loc[setores.SG_UF == UF].CO_MUNICIPIO.unique()):
        temp = gera_distancias_mun(municipio, limite)
        dados.append(temp.copy())

# Junta os daddos gerados
dados = pd.concat(dados)

print("Gerando dados do Brasil...")
# Salva os dados nacionais
dados.to_parquet(f'./dados/distancias/BR.parquet')

print("Gerando dados por UF...")
# Salva os dados por UF
for UF in tqdm(co_uf_ibge.keys()):
    dados.loc[dados.CO_MUNICIPIO.isin(set(setores.loc[setores.SG_UF == UF].CO_MUNICIPIO.unique()))].to_parquet(f'./dados/distancias/{UF}.parquet')