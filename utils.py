"""
utils.py

Este módulo fornece funções utilitárias para processar e analisar dados geográficos e relacionados à saúde.
Ele inclui funções para formatar identificadores, recuperar unidades de saúde, gerar mapas e executar
transformações de dados. As funções são projetadas para serem reutilizáveis e facilitar tarefas comuns na análise de dados.

Funções:
- format_ine(numero): Formata um número fornecido para uma sequência de 10 dígitos.
- format_cnes(numero): Formata um número fornecido para uma sequência de 7 dígitos.
- get_unidades(UF='DF', MACRO=None, ativas=True): Recupera unidades de saúde com base em critérios especificados.
- gera_mapa_densidade(UF, MACRO, export=False): Gera um mapa de densidade de unidades de saúde para uma área fornecida.
- get_setores(UF, MACRO): Recupera setores censitários para um estado e macrorregião especificados.
- convert_keys_to_int(d): Converte todas as chaves em um dicionário de sequência de caracteres para inteiro format.
- get_distancias(UF): Carrega dados de distância para um estado especificado.
- format_population(x): Formata um número populacional com separadores de milhares.
- format_percentage(x): Formata um valor decimal como uma string de porcentagem.
"""

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

#Situação detalhada do Setor Censitário
ds_cd_sit = { 
    #urbano
	1: 'Área urbana de alta densidade de edificações de cidade ou vila',
	2: 'Área urbana de baixa densidade de edificações de cidade ou vila',
	3: 'Núcleo urbano',
    #rural
	5: 'Aglomerado rural - Povoado',
	6: 'Aglomerado rural - Núcleo rural',
	7: 'Aglomerado rural - Lugarejo',
	8: 'Área rural (exclusive aglomerados)',
	9: 'Massas de água',
}
#Tipo do Setor Censitário
ds_cd_tipo	= {
	0: 'Não especial',
	1: 'Favela e Comunidade Urbana',
	2: 'Quartel e base militar',
	3: 'Alojamento / acampamento',
	4: 'Setor com baixo patamar domiciliar',
	5: 'Agrupamento indígena',
	6: 'Unidade prisional',
	7: 'Convento / hospital / ILPI / IACA',
	8: 'Agrovila do PA', #assentamentos
	9: 'Agrupamento quilombola',
}
# descrição de tipo de equipe
tipo_sigla = {
    70:'eSF',
    71:'eSB',
    72:'eMulti',
    73:'eCR',
    74:'eAPP',
    76:'eAP',
}
tipo_descricao = {
    70:'EQUIPE DE SAUDE DA FAMILIA',
    71:'EQUIPE DE SAUDE BUCAL',
    72:'EQUIPE MULTIPROFISSIONAL',
    73:'EQUIPE DOS CONSULTORIOS NA RUA',
    74:'EQUIPE DE ATENCAO PRIMARIA PRISIONAL',
    76:'EQUIPE DE ATENCAO PRIMARIA',
}
co_uf_ibge = {'AC':'12','AL':'27','AP':'16','AM':'13','BA':'29','CE':'23','DF':'53','ES':'32','GO':'52','MA':'21','MT':'51','MS':'50','MG':'31','PA':'15','PB':'25','PR':'41','PE':'26','PI':'22','RJ':'33','RN':'24','RS':'43','RO':'11','RR':'14','SC':'42','SP':'35','SE':'28','TO':'17'}
sg_uf_ibge = {'12':'AC','27':'AL','16':'AP','13':'AM','29':'BA','23':'CE','53':'DF','32':'ES','52':'GO','21':'MA','51':'MT','50':'MS','31':'MG','15':'PA','25':'PB','41':'PR','26':'PE','22':'PI','33':'RJ','24':'RN','43':'RS','11':'RO','14':'RR','42':'SC','35':'SP','28':'SE','17':'TO'}

nome_macro = {
	'1101': 'Macrorregional II (Cacoal)',
	'1102': 'Macrorregião I (Porto Velho)',
	'1201': 'Macro Única - AC (Rio Branco)',
	'1302': 'Oeste (Tabatinga)',
	'1303': 'Leste (Parintins)',
	'1304': 'Central (Manaus)',
	'1401': 'Macro-Roraima (Boa Vista)',
	'1509': 'Macrorregional IV (Marabá)',
	'1510': 'Macrorregional III  (Santarém)',
	'1511': 'Macrorregional II (Paragominas)',
	'1512': 'Macrorregional I (Belém)',
	'1601': 'Macro Única - AP (Macapá)',
	'1701': 'Macrorregião Norte (Araguaína)',
	'1702': 'Macrorregião Centro-Sul (Palmas)',
	'2109': 'Macrorregião Sul (Imperatriz)',
	'2110': 'Macrorregião Norte (São Luís)',
	'2111': 'Macrorregião Leste (Caxias)',
	'2207': 'Semi-Árido (Picos)',
	'2208': 'Meio Norte (Teresina)',
	'2209': 'Litoral (Parnaíba)',
	'2210': 'Cerrados (Floriano)',
	'2306': '5ª Macro - Litoral Leste/Jaguaribe (Aracati)',
	'2307': '4ª Macro - Sertão Central (Quixadá)',
	'2308': '3ª Macro - Cariri (Juazeiro do Norte)',
	'2309': '2ª Macro - Sobral (Sobral)',
	'2310': '1ª Macro - Fortaleza (Fortaleza)',
	'2401': 'Macrorregião II (Mossoró)',
	'2402': 'Macrorregião I (Natal)',
	'2501': 'Macrorregião III - Sertão/Alto Sertão (Cajazeiras)',
	'2502': 'Macrorregião II - Campina Grande (Campina Grande)',
	'2503': 'Macrorregião I - João Pessoa (João Pessoa)',
	'2605': 'Vale do São Francisco e Araripe (Petrolina)',
	'2606': 'Sertão (Serra Talhada)',
	'2607': 'Metropolitana (Recife)',
	'2608': 'Agreste (Caruaru)',
	'2703': '2ª Macrorregião de Saúde (Arapiraca)',
	'2704': '1ª Macrorregião de Saúde (Maceió)',
	'2801': 'Macro Única (Aracaju)',
	'2910': 'Sul (Ilhéus)',
	'2911': 'Sudoeste (Vitória da Conquista)',
	'2912': 'Oeste (Barreiras)',
	'2913': 'Norte (Juazeiro)',
	'2914': 'Nordeste (Alagoinhas)',
	'2915': 'Leste (Salvador)',
	'2916': 'Extremo Sul (Teixeira de Freitas)',
	'2917': 'Centro-Leste (Feira de Santana)',
	'2918': 'Centro - Norte (Jacobina)',
	'3101': 'Sul (Poços de Caldas)',
	'3102': 'Centro Sul (São João Del Rei)',
	'3103': 'Centro (Belo Horizonte)',
	'3104': 'Jequitinhonha (Diamantina)',
	'3105': 'Oeste (Divinópolis)',
	'3106': 'Leste (Governador Valadares)',
	'3107': 'Sudeste (Juiz de Fora)',
	'3108': 'Norte (Montes Claros)',
	'3109': 'Noroeste (Patos de Minas)',
	'3110': 'Leste do Sul (Manhuaçu)',
	'3111': 'Nordeste (Teófilo Otoni)',
	'3112': 'Triangulo do Sul (Uberaba)',
	'3113': 'Triangulo do Norte (Uberlândia)',
	'3114': 'Vale do Aço (Ipatinga)',
	'3205': 'Sul (Cachoeiro de Itapemirim)',
	'3207': 'Metropolitana (Vitória)',
	'3209': 'Central/Norte (Linhares)',
	'3310': 'Macrorregião III (Campos dos Goytacazes)',
	'3311': 'Macrorregião II (Rio de Janeiro)',
	'3312': 'Macrorregião I (Volta Redonda)',
	'3518': 'RRAS9 (Bauru)',
	'3519': 'RRAS8 (Sorocaba)',
	'3520': 'RRAS7 (Santos)',
	'3521': 'RRAS6 (São Paulo)',
	'3522': 'RRAS5 (Osasco)',
	'3523': 'RRAS4 (Taboão da Serra)',
	'3524': 'RRAS3 (Francisco Morato)',
	'3525': 'RRAS2 (Guarulhos)',
	'3526': 'RRAS17 (São José dos Campos)',
	'3527': 'RRAS16 (Jundiaí)',
	'3528': 'RRAS15 (Campinas)',
	'3529': 'RRAS14 (Piracicaba)',
	'3530': 'RRAS13 (Ribeirão Preto)',
	'3531': 'RRAS12 (São José do Rio Preto)',
	'3532': 'RRAS11 (Presidente Prudente)',
	'3533': 'RRAS10 (Marília)',
	'3534': 'RRAS1 (São Caetano do Sul)',
	'4105': 'Macrorregional Norte (Londrina)',
	'4106': 'Macrorregional Noroeste (Maringá)',
	'4107': 'Macrorregional Leste (Curitiba)',
	'4108': 'Macrorregião Oeste (Cascavel)',
	'4210': 'Sul (Criciúma)',
	'4211': 'Planalto Norte e Nordeste (Joinville)',
	'4212': 'Meio Oeste e Serra Catarinense (Lages)',
	'4213': 'Grande Oeste (Chapecó)',
	'4214': 'Grande Florianopolis (Florianópolis)',
	'4215': 'Foz do Rio Itajaí (Itajaí)',
	'4216': 'Alto Vale do Itajaí (Blumenau)',
	'4308': 'Vales (Santa Cruz do Sul)',
	'4309': 'Sul (Pelotas)',
	'4310': 'Serra (Caxias do Sul)',
	'4311': 'Norte (Passo Fundo)',
	'4312': 'Missioneira (Santo Ângelo)',
	'4313': 'Metropolitana (Porto Alegre)',
	'4314': 'Centro-Oeste (Santa Maria)',
	'5005': 'Três Lagoas (Três Lagoas)',
	'5006': 'Dourados (Dourados)',
	'5007': 'Corumba (Corumbá)',
	'5008': 'Campo Grande (Campo Grande)',
	'5101': 'Macrorregião Sul  (Rondonópolis)',
	'5102': 'Macrorregião Oeste (Pontes e Lacerda)',
	'5103': 'Macrorregião Norte  (Sinop)',
	'5104': 'Macrorregião Leste (Barra do Garças)',
	'5105': 'Macrorregião Centro-Norte (Cuiabá)',
	'5206': 'Macrorregião Sudoeste (Rio Verde)',
	'5207': 'Macrorregião Nordeste (Formosa)',
	'5208': 'Macrorregião Centro-Oeste (Goiânia)',
	'5209': 'Macrorregião Centro-Norte (Anápolis)',
	'5210': 'Macrorregião Centro Sudeste (Catalão)',
	'5302': 'Distrito Federal (Brasília)',
}

def format_ine(numero):
    try:
        return f'{int(numero):010d}'
    except Exception:
        return None

def format_cnes(numero):
    try:
        return f'{int(numero):07d}'
    except Exception:
        return None
    
    # carregando shape das unidades
#unidades = gpd.read_file('./'shapes'/unidades_cnes.gpkg')
def get_unidades(UF='DF', MACRO=None, ativas=True):
    if os.path.exists('../shapes/unidades_cnes_realocadas.gpkg'):
        unidades = gpd.read_file('../shapes/unidades_cnes_realocadas.gpkg', driver='GPKG')
    elif os.path.exists('./shapes/unidades_cnes_realocadas.gpkg'):
        unidades = gpd.read_file('./shapes/unidades_cnes_realocadas.gpkg', driver='GPKG')

    unidades = unidades.astype({'CO_MACRORREGIONAL':'Int64'})
    # filtrando unidades de SE
    if MACRO is None:
        unidades = unidades.loc[(unidades.SG_UF==UF) & unidades.TP_EQUIPE.isin([70,71,72,73,74,76]) & unidades.TP_UNIDADE.isin([1,2,15,32,40,71])]
    else:
        unidades = unidades.loc[(unidades.CO_MACRORREGIONAL==int(MACRO)) & unidades.TP_EQUIPE.isin([70,71,72,73,74,76]) & unidades.TP_UNIDADE.isin([1,2,15,32,40,71])]
    if ativas:
        return unidades.loc[unidades.ST_ATIVA==1]
    return unidades

# Configurações de estilos dos Markers e conteúdos das caixas das equipes
def get_caixa_old(equipe):
    return f"""
     <div style="width:250px;">
        <span style="font-family: 'Roboto', sans-serif; font-weight: 800; color:#F90; font-size: 1.45em; margin-bottom: 5px; display: block; border-bottom: 2px solid #DDD;">{equipe.NO_MUNICIPIO}</span>
        <p style ="font-size: 0.9em"><b>ENDEREÇO:</b> {equipe.NO_LOGRADOURO}<br/>
        <b>COORDENADA:</b> {round(equipe.geometry.y,5):n}, {round(equipe.geometry.x,5):n}<br/>
        <b>ÁREA: </b>{equipe.CO_AREA}<br/>
        {"<span style='color:#F90'>(original fora do municipio)</span>" if equipe.DENTRO_MUNICIPIO == False else ""}
        <div style="margin: 2px 0; padding:10px 15px; background-color: #EEE;">
        <b>{equipe.DS_TIPO_UNIDADE}</b><br/>
        {equipe.NO_FANTASIA} (CNES:{format_cnes(equipe.CO_CNES)})<br/>
        </div>
        <div style="overflow-y: auto; margin-top: 15px; max-height: 250px; padding: 10px; border: 1px solid #EEE; background-color: #FAFAFA;">
        <b>{equipe.DS_EQUIPE}</b><br/>
        {equipe.NO_REFERENCIA} (INE:{format_ine(equipe.CO_EQUIPE)})<br/>
        <b>PESSOAS CADASTRADAS: </b>{equipe.CADASTROS_VINCULADOS:n}<br/>
        <b>PESSOAS ACOMPANHADAS: </b>{equipe.CADASTROS_ACOMPANHADOS:n}<br/>
        </div>
     </div>
     """
# Lixos?
marker_colors = ['red','blue','gray','darkred','lightred','orange','beige','green','darkgreen','lightgreen','darkblue','lightblue','purple','darkpurple','pink','cadetblue','lightgray','black']
cor_equipe = {73:'gray', 70:'red', 71:'green', 72:'darkblue', 74:'black', 76:'orange'}
icon_equipe = {71:'face-laugh-wink', 73:'truck-medical', 74:'building-shield'} #tooth


def get_caixa(cnes, export=False):
   if export:
        scroll = '<div class="scrollbar">'
   else:
        scroll = '<div style="overflow-y: auto; margin-top: 15px; max-height: 250px; padding: 0px 10px; border: 1px solid #EEE; background-color: #FAFAFA;">'
   
   inicio = f"""
      <div style="width:250px; max-height: 500px;">
         <span style="font-family: 'Roboto', sans-serif; font-weight: 800; color:#F90; font-size: 1.45em; margin-bottom: 5px; display: block; border-bottom: 2px solid #DDD;">{cnes.NO_MUNICIPIO}</span>
         <p style ="font-size: 0.9em"><b>ENDEREÇO:</b> {cnes.NO_LOGRADOURO}<br/>
         <b>COORDENADA:</b> {round(cnes.LONGITUDE,5):n}, {round(cnes.LATITUDE,5):n}<br/>
         {"<span style='color:#F90'>(Coordenada original fora do municipio)</span>" if cnes.DENTRO_MUNICIPIO == False else ""}
         </p>
      <div style="margin: 2px 0; padding:10px 15px; background-color: #EEE;">
         <b>{cnes.DS_TIPO_UNIDADE}</b><br/>
         {cnes.NO_FANTASIA} (CNES:{cnes.CO_CNES})<br/>
      </div>
        """
   equipes = ''
   for i in range(len(cnes.CO_EQUIPE)):
        linha = f"""
            <p><b>{tipo_sigla.get(int(cnes.TP_EQUIPE[i])) +' - '+ tipo_descricao.get(int(cnes.TP_EQUIPE[i])) if "DS_EQUIPE" not in cnes else cnes.DS_EQUIPE[i]}</b><br/>
            {cnes.NO_REFERENCIA[i]} (INE:{cnes.CO_EQUIPE[i]})<br/>
            {"<span style='color:#F90'>(carga horária inválida para financiamento)</span><br/>" if 'ST_EQUIPE_VALIDA' in cnes and cnes.ST_EQUIPE_VALIDA[i] == 'N' else ""}
            <b>PARÂMETRO CADASTRAL: </b>{cnes.PARAMETRO_CADASTRAL[i]:n}<br/>
            <b>PESSOAS CADASTRADAS: </b>{cnes.CADASTROS_VINCULADOS[i]:n}<br/>
            <b>PESSOAS ACOMPANHADAS: </b>{cnes.CADASTROS_ACOMPANHADOS[i]:n}</p>
        """
        equipes += linha
   return inicio + scroll + equipes + '</div></div>'

def create_box(cnes, export=False):
    if export:
        scroll = '<div class="scrollbar">'
    else:
        scroll = '<div style="overflow-y: auto; margin-top: 15px; max-height: 250px; padding: 0px 10px; border: 1px solid #EEE; background-color: #FAFAFA;">'
    inicio = f"""
    <div style="width:250px; max-height: 500px;">
        <span style="font-family: 'Roboto', sans-serif; font-weight: 800; color:#F90; font-size: 1.45em; margin-bottom: 5px; display: block; border-bottom: 2px solid #DDD;">{cnes.NO_MUNICIPIO}</span>
        <p style ="font-size: 0.9em"><b>ENDEREÇO:</b> {cnes.NO_LOGRADOURO}<br/>
        <b>COORDENADA:</b> {round(cnes.LONGITUDE,5):n}, {round(cnes.LATITUDE,5):n}<br/>
        {"<span style='color:#F90'>(Coordenada original fora do municipio)</span>" if cnes.DENTRO_MUNICIPIO == False else ""}
        </p>
    <div style="margin: 2px 0; padding:10px 15px; background-color: #EEE;">
        <b>{cnes.DS_TIPO_UNIDADE}</b><br/>
        {cnes.NO_FANTASIA} (CNES:{cnes.CO_CNES})<br/>
        """
    equipes = ''
    cadastros_previne = 0
    cadastros_totais = 0
    cadastros_acompanhados = 0
    parametro_cadastral = 0
    for i in range(len(cnes.CO_EQUIPE)):
        # <p><b>{tipo_descricao.get(int(cnes.TP_EQUIPE[i])) if cnes.DS_EQUIPE[i] is None else cnes.DS_EQUIPE[i]}</b> ({tipo_sigla.get(int(cnes.TP_EQUIPE[i])) if cnes.SG_EQUIPE[i] is None else cnes.SG_EQUIPE[i]})<br/>
        # To do: Acrescentar informações diferentes para cada tipo de unidade
        # if cnes.TP_EQUIPE == 72:
        #     # Modalidade da emulti
        #     # QT vínculos Emulti
        #     pass #emulti
        # elif cnes.TP_EQUIPE == 71:
        #     # Modalidade da eSB
        #     # QT vínculos eSB
        #     pass #eSB
        # else:
        #     pass #esf eap eapp
        #{"<span style='color:#F90'>(carga horária inválida para financiamento)</span><br/>" if 'ST_EQUIPE_VALIDA' in cnes and cnes.ST_EQUIPE_VALIDA[i] == 'N' else ""}
        linha = f"""
            <p><b>{tipo_sigla.get(int(cnes.TP_EQUIPE[i])) +' - '+ tipo_descricao.get(int(cnes.TP_EQUIPE[i])) if "DS_EQUIPE" not in cnes else cnes.DS_EQUIPE[i]}</b><br/>
            {cnes.NO_REFERENCIA[i]} (INE:{cnes.CO_EQUIPE[i]})<br/>
            <b>PARÂMETRO CADASTRAL: </b>{cnes.PARAMETRO_CADASTRAL[i]:n}<br/>
            <b>PESSOAS CADASTRADAS: </b>{cnes.CADASTROS_VINCULADOS[i]:n}<br/>
            <b>PESSOAS ACOMPANHADAS: </b>{cnes.CADASTROS_ACOMPANHADOS[i]:n}</p>
        """
        parametro_cadastral += cnes.PARAMETRO_CADASTRAL[i]
        cadastros_previne += cnes.CADASTROS_PREVINE[i]
        cadastros_totais += cnes.CADASTROS_VINCULADOS[i]
        cadastros_acompanhados += cnes.CADASTROS_ACOMPANHADOS[i]
        equipes += linha
    #ÁREA: {cnes.CO_AREA[i]} 
    soma = f"""<b>PARÂMETRO CADASTRAL:</b> {parametro_cadastral:n}<br/>
        <b>VÍNCULOS ANTERIORES:</b> {cadastros_previne:n}<br/>
        <b>PESSOAS CADASTRADAS:</b> {cadastros_totais:n}<br/>
        <b>PESSOAS ACOMPANHADAS:</b> {cadastros_acompanhados:n}
    </div>
    {scroll}
    """
    fim = f'</div></div>'
    return inicio + soma + equipes + fim

#icones -> https://fontawesome.com/icons/categories/medical-health
def gera_mapa_equipe_old(UF, MACRO, export=False):
   cor_equipe = {73:'steelblue', 70:'blue', 71:'gray', 72:'red', 74:'black', 76:'orange'}
   icon_equipe = {71:'face-laugh-wink', 73:'truck-medical', 74:'building-shield'} #tooth
   unidades = get_unidades(UF, MACRO, True)
   if os.path.exists('../shapes/macro.gpkg'):
      macro = gpd.read_file('../shapes/macro.gpkg')
   elif os.path.exists('./shapes/macro.gpkg'):
      macro = gpd.read_file('./shapes/macro.gpkg')
   macro = macro.astype({'CO_MACRORREGIONAL':'Int64'})
   centroUF = macro.loc[macro.CO_MACRORREGIONAL == int(MACRO)].geometry.centroid.values
   map = folium.Map(location=[centroUF.y,centroUF.x], tiles = 'cartodbpositron', control_scale=True, prefer_canvas=True, zoom_start=12)
   for key, value in tipo_sigla.items():
      temp_group = folium.FeatureGroup(value)
      #todo_criar grupo de equipes do estabelecimento
      grupo_estabelecimento = ''
      for index, equipe in unidades.loc[unidades.TP_EQUIPE==key].iterrows():
         folium.Marker([equipe.geometry.y, equipe.geometry.x], icon=folium.Icon(color=cor_equipe.get(key, 'steelblue'), icon='ship' if (equipe.TP_UNIDADE == 32 or equipe.CO_SUB_TIPO_EQUIPE == 12) else icon_equipe.get(key, 'house-medical'), prefix='fa'),popup=get_caixa(equipe), tooltip=equipe.NO_REFERENCIA).add_to(temp_group)
      temp_group.add_to(map)
      
   # Criando o layer de contorno
   folium.features.GeoJson(macro.loc[macro.CO_MACRORREGIONAL == int(MACRO)], name=nome_macro.get(str(MACRO)),
      style_function = lambda x: {'fillColor': 'transparent', 'color':'steelblue', 'fillOpacity': 0, 'weight': 1,'dash_array':'2'}).add_to(map)

   folium.LayerControl().add_to(map)
   if export:
      map.save(f"./output/site/mapas/equipe/{UF}_{MACRO}.html")
   return map

def gera_mapa_equipe(UF, MACRO=None, export=False):
    icon_sigla_equipe = {'eSF':'house-medical', 'eSFR':'ship', 'eSB':'face-laugh-wink', 'eMulti':'house-medical', 'eAPP':'building-shield', 'eAP':'house-medical','eCR':'truck-medical'}
    cor_sigla_equipe = {'eCR':'gray','eSF':'red','eSFR':'blue', 'eSB':'green','eMulti':'darkblue','eAPP':'black', 'eAP':'orange'}    
    
    if MACRO is None:
        unidades = get_unidades(UF, ativas=True)
        if os.path.exists('../shapes/estados.json'):
            estados = gpd.read_file('../shapes/estados.json')
        elif os.path.exists('./shapes/estados.json'):
            estados = gpd.read_file('./shapes/estados.json')
        
        estados_uf = estados.loc[estados.SIGLA==UF]
        centroUF = estados_uf.geometry.centroid.values
        arquivo = UF
    else: 
        unidades = get_unidades(UF, MACRO, True)
        if os.path.exists('../shapes/macro.gpkg'):
            macro = gpd.read_file('../shapes/macro.gpkg')
        elif os.path.exists('./shapes/macro.gpkg'):
            macro = gpd.read_file('./shapes/macro.gpkg')

        macro = macro.astype({'CO_MACRORREGIONAL':'Int64'})
        nome_macro = macro[['CD_MUN', 'CD_UF', 'CO_MACRORREGIONAL', 'NO_MACRORREGIONAL']].rename(columns={'CD_UF':'SG_UF'})
        nome_macro = nome_macro[['CO_MACRORREGIONAL','NO_MACRORREGIONAL']].set_index('CO_MACRORREGIONAL').to_dict()
        nome_macro = nome_macro.get('NO_MACRORREGIONAL')
        centroUF = macro.loc[macro.CO_MACRORREGIONAL == int(MACRO)].geometry.centroid.values
        arquivo = f'{UF}_{MACRO}'
            
    unidades = unidades.groupby(['NO_MUNICIPIO','CO_CNES','NO_FANTASIA','NO_LOGRADOURO','DS_TIPO_UNIDADE','TP_UNIDADE','SG_EQUIPE']).agg({'CO_EQUIPE':list, 'TP_EQUIPE':list, 'DS_EQUIPE':list,'CO_AREA':list, 'NO_REFERENCIA':list, 'ST_EQUIPE_VALIDA':list, 'CADASTROS_ACOMPANHADOS':list,'CADASTROS_VINCULADOS':list, 'CADASTROS_PREVINE':list, 'PARAMETRO_CADASTRAL':list, 'LATITUDE':'mean', 'LONGITUDE':'mean', 'DENTRO_MUNICIPIO':'max'}).reset_index()
    unidades['geometry'] = [Point(point[0],point[1]) for point in zip(unidades.LONGITUDE, unidades.LATITUDE)]
    unidades = gpd.GeoDataFrame(unidades, geometry='geometry')
    
    map = folium.Map(location=[centroUF.y,centroUF.x], tiles = 'cartodbpositron', control_scale=True, prefer_canvas=True, zoom_start=12)

    for value in ['eSFR','eSF','eSB','eMulti','eCR','eAPP','eAP']:
        temp_group = folium.FeatureGroup(value)
        for index, equipe in unidades.loc[unidades.SG_EQUIPE==value].iterrows():
            folium.Marker([equipe.geometry.y, equipe.geometry.x], icon=folium.Icon(color=cor_sigla_equipe.get(value, 'steelblue'), icon='ship' if (equipe.TP_UNIDADE == 32) else icon_sigla_equipe.get(value, 'house-medical'), prefix='fa'),popup=get_caixa(equipe, export), tooltip=equipe.NO_FANTASIA).add_to(temp_group)
        temp_group.add_to(map)
    
    # Criando o layer de contorno
    if MACRO is None:
        folium.features.GeoJson(estados_uf, name=UF,
            style_function = lambda x: {'fillColor': 'transparent', 'color':'steelblue', 'fillOpacity': 0, 'weight': 1,'dash_array':'2'}).add_to(map)
    else:
        folium.features.GeoJson(macro.loc[macro.CO_MACRORREGIONAL == int(MACRO)], name=nome_macro.get(str(MACRO)),
            style_function = lambda x: {'fillColor': 'transparent', 'color':'steelblue', 'fillOpacity': 0, 'weight': 1,'dash_array':'2'}).add_to(map)

    folium.LayerControl().add_to(map)
    if export:
        html_map = map.get_root().render()
        html_map = html_map.replace(
            "</head>",
            f"{custom_scrollbar_css}</head>"
        )

        diretorio_1 = "./output/site/mapas/equipe/"
        diretorio_2 = "../output/site/mapas/equipe/"

        if os.path.exists(diretorio_1):
            diretorio = diretorio_1
        elif os.path.exists(diretorio_2):
            diretorio = diretorio_2
        else:
            diretorio = diretorio_1
            os.makedirs(diretorio)

        with open(f"{diretorio}{arquivo}.html", "w", encoding='utf-8') as f:
            f.write(html_map)

        map.save(f"{diretorio}{arquivo}.html")

    return map


def get_setores(UF, MACRO):
    if os.path.exists('../shapes/setores_light_densidade.gpkg'):
        setores_global = gpd.read_file('../shapes/setores_light_densidade.gpkg')
    elif os.path.exists('./shapes/setores_light_densidade.gpkg'):
        setores_global = gpd.read_file('./shapes/setores_light_densidade.gpkg')
    setores_global =  setores_global.loc[setores_global.CO_MACRORREGIONAL==int(MACRO)]
    #Não estava gerando a coluna de geoid
    setores_global['geoid'] = setores_global.index.astype(str)
    return gpd.GeoDataFrame(setores_global, geometry='geometry')
    from shapely.validation import make_valid
    
    import numpy as np
    setores = gpd.read_file('./shapes/setores_light.gpkg')
    setores = setores.astype({'CO_MACRORREGIONAL':'Int64'})
    setores =  setores.loc[setores.CO_MACRORREGIONAL==int(MACRO)]
    setores['Densidade'] = setores.v0001/setores.AREA_KM2
    #setores['Log_Densidade'] = np.log(setores['Densidade'].replace(0, np.nan).fillna(0)) #np.log(setores['Densidade'])
    # Suavizado pela raiz quadrada
    setores['Log_Densidade'] = np.sqrt(setores['Densidade'].replace(0, np.nan).fillna(0))
    setores['Log_Densidade'] = setores['Log_Densidade'].replace([np.inf, -np.inf], 0)  # Substitui Inf por NaN
    # Suavizado por box-cox
    #from scipy import stats
    #setores['Densidade_Ajustada'] = setores['Densidade'] + 1  # Adiciona 1 para evitar zeros
    #setores['Log_Densidade'], _ = stats.boxcox(setores['Densidade_Ajustada'])

    setores.CD_SIT = pd.to_numeric(setores.CD_SIT)
    setores.CD_TIPO = pd.to_numeric(setores.CD_TIPO)
    # Convertendo os códigos para a descrição
    setores['CD_SIT'] = setores.CD_SIT.map(ds_cd_sit)
    setores['CD_TIPO'] = setores.CD_TIPO.map(ds_cd_tipo)
    # Criando o geoID para o geojson
    setores['geoid'] = setores.index.astype(str)
    setores = setores[['CD_MUN','geoid', 'CO_MACRORREGIONAL', 'CD_SETOR', 'SITUACAO', 'CD_SIT', 'CD_TIPO', 'AREA_KM2', 'v0001', 'Densidade','Log_Densidade', 'geometry']]
    setores['geometry'] = setores['geometry'].apply(make_valid)
    return gpd.GeoDataFrame(setores, geometry='geometry')

# estilos da scroll bar para injection no css
custom_scrollbar_css = """
        <style>
        .scrollbar {
            background-color: #FAFAFA;
            overflow-y: auto;
            margin: 15px 0px;
            padding: 0px 10px;
            max-height: 250px;
            border: 1px solid #EEE;
        }
        .scrollbar::-webkit-scrollbar-track {
            -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
            border-radius: 10px;
            background-color: #F5F5F5;
        }
        .scrollbar::-webkit-scrollbar {
            width: 10px;
            background-color: #F5F5F5;
        }
        .scrollbar::-webkit-scrollbar-thumb {
            border-radius: 10px;
            -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,.3);
            background-color: #f1942f;
        }
        </style>
        """

def gera_mapa_densidade(UF, MACRO, export=False):
    unidades = get_unidades(UF, MACRO)
    unidades_cnes = unidades.groupby(['CO_CNES','NO_FANTASIA','NO_MUNICIPIO','NO_LOGRADOURO','DS_TIPO_UNIDADE']).agg({'CO_EQUIPE':list, 'TP_EQUIPE':list, 'DS_EQUIPE':list,'SG_EQUIPE':list,'CO_AREA':list, 'NO_REFERENCIA':list, 'ST_EQUIPE_VALIDA':list, 'CADASTROS_ACOMPANHADOS':list,'CADASTROS_VINCULADOS':list, 'CADASTROS_PREVINE':list, 'PARAMETRO_CADASTRAL':list, 'LATITUDE':'mean', 'LONGITUDE':'mean', 'DENTRO_MUNICIPIO':'max'}).reset_index()
    # Após juntar as médias das coordenadas (que deveriam ser iguais), a geometria é recalculada
    unidades_cnes['geometry'] = [Point(point[0],point[1]) for point in zip(unidades_cnes.LONGITUDE, unidades_cnes.LATITUDE)]
    setores = get_setores(UF, MACRO)
    #carrega o estado para colocar um contorno e definir o centro
    if os.path.exists('../shapes/macro.gpkg'):
        macro = gpd.read_file('../shapes/macro.gpkg')
    elif os.path.exists('./shapes/macro.gpkg'):
        macro = gpd.read_file('./shapes/macro.gpkg')
    macro = macro.astype({'CO_MACRORREGIONAL':'Int64'})
    centroMacro = macro.loc[macro.CO_MACRORREGIONAL == int(MACRO)].geometry.centroid.values

    # Dissolve os setores por tipo
    shape_tipos = setores[['CD_TIPO', 'geometry']].dissolve(by='CD_TIPO').reset_index()

    # Shapes Complementares
    quilombos = shape_tipos.loc[shape_tipos.CD_TIPO=='Agrupamento quilombola']
    assentamentos = shape_tipos.loc[shape_tipos.CD_TIPO=='Agrovila do PA']
    indigenas = shape_tipos.loc[shape_tipos.CD_TIPO=='Agrupamento indígena']

    # Criando o mapa com tile de fundo
    map = folium.Map(location=[centroMacro.y,centroMacro.x], tiles = 'cartodbpositron', control_scale=True, prefer_canvas=True, zoom_start=11)
    # Cria p objeto marker cluster 
    marker_cluster = MarkerCluster(name="Unidades básicas de saúde")
    # cria os estabelecimentos
    for index, cnes in unidades_cnes.iterrows():
        caixa = create_box(cnes, export)
        folium.Marker([cnes.geometry.y, cnes.geometry.x], icon=folium.Icon(color="orange", icon="house-medical", prefix='fa'), popup=caixa, tooltip = cnes.NO_FANTASIA).add_to(marker_cluster)
    
    # Acrescentando os shapes
    # shape dos setores censitarios
    folium.Choropleth(
        geo_data=setores,
        name='Densidade demográfica',
        data=setores,
        columns=['geoid', 'Log_Densidade'],
        key_on='feature.id',
        fill_color='YlOrRd',
        fill_opacity=0.8,
        line_opacity=0.5,
        line_color='black',
        line_weight=.5,
        smooth_factor=1.0,
        nan_fill_color = "White",
        legend_name= 'Raiz quadrada da densidade demográfica'
        ).add_to(map)

    # Criando o layer de quilombos
    folium.features.GeoJson(quilombos, name='Agrupamentos Quilombolas',
        style_function = lambda x: {'fillColor': '#669966', 
                                        'color':'#669966', 
                                        'fillOpacity': .5, 
                                        'weight': 0.1,
                                        'dash_array':'2'}
        ).add_to(map)

    # Criando o layer de assentamentos
    folium.features.GeoJson(assentamentos, name='Agrovila: Projeto de Assentamento',
        style_function = lambda x: {'fillColor': '#97d963', 
                                        'color':'#97d963', 
                                        'fillOpacity': .5, 
                                        'weight': 0.1,
                                        'dash_array':'2'}
        ).add_to(map)

    # Criando o layer de indigenas
    folium.features.GeoJson(indigenas, name='Agrupamentos Indígenas',
        style_function = lambda x: {'fillColor': '#c5dd2a', 
                                        'color':'#c5dd2a', 
                                        'fillOpacity': .5, 
                                        'weight': 0.1,
                                        'dash_array':'2'}
        ).add_to(map)

    # Criando o layer com os tooltips por cima de tudo
    folium.features.GeoJson(setores, name='Informações dos setores',
        style_function = lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
        tooltip = folium.features.GeoJsonTooltip(fields=['CD_SIT','CD_TIPO','v0001'],
                                                aliases = ['Situação detalhada', 'Tipo do setor', 'População residente'],
                                                labels=True, sticky=False),
        highlight_function = lambda x: {'fillColor': '#ffffff', 'color':'#ffffff', 'fillOpacity': .5, 'weight': 0.1}).add_to(map)

    # Criando o layer de contorno do estado
    #folium.features.GeoJson(estados.loc[estados.SIGLA == UF], name=UF, style_function = lambda x: {'fillColor': 'transparent', 'color':'steelblue', 'fillOpacity': 0, 'weight': 1,'dash_array':'2'}).add_to(map)    
    # Add the marker cluster to the map
    marker_cluster.add_to(map)

    folium.LayerControl().add_to(map)
    
    # Display/Export o mapa
    if export:
        html_map = map.get_root().render()
        html_map = html_map.replace(
            "</head>",
            f"{custom_scrollbar_css}</head>"
        )
        with open(f"./output/site/mapas/ruralidade/{UF}_{MACRO}.html", "w", encoding='utf-8') as f:
            f.write(html_map)
        #map.save(f"./output/site/mapas/ruralidade/{UF}.html")
    return map


def gera_mapa_densidade(UF, MACRO, export=False):
    unidades = get_unidades(UF, MACRO)
    unidades_cnes = unidades.groupby(['CO_CNES','NO_FANTASIA','NO_MUNICIPIO','NO_LOGRADOURO','DS_TIPO_UNIDADE']).agg({'CO_EQUIPE':list, 'TP_EQUIPE':list, 'DS_EQUIPE':list,'SG_EQUIPE':list,'CO_AREA':list, 'NO_REFERENCIA':list, 'ST_EQUIPE_VALIDA':list,'CADASTROS_ACOMPANHADOS':list,'CADASTROS_VINCULADOS':list, 'CADASTROS_PREVINE':list, 'PARAMETRO_CADASTRAL':list, 'LATITUDE':'mean', 'LONGITUDE':'mean', 'DENTRO_MUNICIPIO':'max'}).reset_index()
    # Após juntar as médias das coordenadas (que deveriam ser iguais), a geometria é recalculada
    unidades_cnes['geometry'] = [Point(point[0],point[1]) for point in zip(unidades_cnes.LONGITUDE, unidades_cnes.LATITUDE)]
    setores = get_setores(UF, MACRO)
    #carrega o estado para colocar um contorno e definir o centro
    if os.path.exists('../shapes/macro.gpkg'):
        macro = gpd.read_file('../shapes/macro.gpkg')
    elif os.path.exists('./shapes/macro.gpkg'):
        macro = gpd.read_file('./shapes/macro.gpkg')
    macro = macro.astype({'CO_MACRORREGIONAL':'Int64'})
    centroMacro = macro.loc[macro.CO_MACRORREGIONAL == int(MACRO)].geometry.centroid.values

    # Dissolve os setores por tipo
    shape_tipos = setores[['CD_TIPO', 'geometry']].dissolve(by='CD_TIPO').reset_index()

    # Shapes Complementares
    quilombos = shape_tipos.loc[shape_tipos.CD_TIPO=='Agrupamento quilombola']
    assentamentos = shape_tipos.loc[shape_tipos.CD_TIPO=='Agrovila do PA']
    indigenas = shape_tipos.loc[shape_tipos.CD_TIPO=='Agrupamento indígena']

    # Criando o mapa com tile de fundo
    map = folium.Map(location=[centroMacro.y,centroMacro.x], tiles = 'cartodbpositron', control_scale=True, prefer_canvas=True, zoom_start=11)
    # Cria p objeto marker cluster 
    marker_cluster = MarkerCluster(name="Unidades básicas de saúde")
    # cria os estabelecimentos
    for index, cnes in unidades_cnes.iterrows():
        caixa = create_box(cnes, export)
        folium.Marker([cnes.geometry.y, cnes.geometry.x], icon=folium.Icon(color="orange", icon="house-medical", prefix='fa'), popup=caixa, tooltip = cnes.NO_FANTASIA).add_to(marker_cluster)
    
    # Acrescentando os shapes
    # shape dos setores censitarios
    folium.Choropleth(
        geo_data=setores,
        name='Densidade demográfica',
        data=setores,
        columns=['geoid', 'Log_Densidade'],
        key_on='feature.id',
        fill_color='YlOrRd',
        fill_opacity=0.8,
        line_opacity=0.5,
        line_color='black',
        line_weight=.5,
        smooth_factor=1.0,
        nan_fill_color = "White",
        legend_name= 'Raiz quadrada da densidade demográfica'
        ).add_to(map)

    # Criando o layer de quilombos
    folium.features.GeoJson(quilombos, name='Agrupamentos Quilombolas',
        style_function = lambda x: {'fillColor': '#669966', 
                                        'color':'#669966', 
                                        'fillOpacity': .5, 
                                        'weight': 0.1,
                                        'dash_array':'2'}
        ).add_to(map)

    # Criando o layer de assentamentos
    folium.features.GeoJson(assentamentos, name='Agrovila: Projeto de Assentamento',
        style_function = lambda x: {'fillColor': '#97d963', 
                                        'color':'#97d963', 
                                        'fillOpacity': .5, 
                                        'weight': 0.1,
                                        'dash_array':'2'}
        ).add_to(map)

    # Criando o layer de indigenas
    folium.features.GeoJson(indigenas, name='Agrupamentos Indígenas',
        style_function = lambda x: {'fillColor': '#c5dd2a', 
                                        'color':'#c5dd2a', 
                                        'fillOpacity': .5, 
                                        'weight': 0.1,
                                        'dash_array':'2'}
        ).add_to(map)

    # Criando o layer com os tooltips por cima de tudo
    folium.features.GeoJson(setores, name='Informações dos setores',
        style_function = lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
        tooltip = folium.features.GeoJsonTooltip(fields=['CD_SIT','CD_TIPO','v0001'],
                                                aliases = ['Situação detalhada', 'Tipo do setor', 'População residente'],
                                                labels=True, sticky=False),
        highlight_function = lambda x: {'fillColor': '#ffffff', 'color':'#ffffff', 'fillOpacity': .5, 'weight': 0.1}).add_to(map)

    # Criando o layer de contorno do estado
    #folium.features.GeoJson(estados.loc[estados.SIGLA == UF], name=UF, style_function = lambda x: {'fillColor': 'transparent', 'color':'steelblue', 'fillOpacity': 0, 'weight': 1,'dash_array':'2'}).add_to(map)    
    # Add the marker cluster to the map
    marker_cluster.add_to(map)

    folium.LayerControl().add_to(map)
    
    # Display/Export o mapa
    if export:
        html_map = map.get_root().render()
        html_map = html_map.replace(
            "</head>",
            f"{custom_scrollbar_css}</head>"
        )
        with open(f"./output/site/mapas/ruralidade/{UF}_{MACRO}.html", "w", encoding='utf-8') as f:
            f.write(html_map)
        #map.save(f"./output/site/mapas/ruralidade/{UF}.html")
    return map

def gera_mapa_ruralidade(UF):
    print('Em breve')
    #return 

def convert_keys_to_int(d):
    """
    Converte todas as chaves de um dicionário para o tipo int.
    Suporta dicionários aninhados.
    
    Args:
        d (dict): Dicionário original com chaves no formato string.
    
    Returns:
        dict: Dicionário com as chaves convertidas para int.
    """
    if not isinstance(d, dict):
        raise ValueError("A entrada deve ser um dicionário.")
    
    converted_dict = {}
    for key, value in d.items():
        # Converte a chave para int
        int_key = int(key) if key.isdigit() else key
        
        # Converte valores, se forem dicionários, chama recursivamente
        if isinstance(value, dict):
            converted_dict[int_key] = convert_keys_to_int(value)
        else:
            converted_dict[int_key] = value
    
    return converted_dict


def get_distancias(UF):
    if os.path.exists(f'../dados/distancias/{UF}.parquet'):
        distancias = pd.read_parquet(f'../dados/distancias/{UF}.parquet').rename(columns={'CD_SETOR': 'ID_SETOR'})
    elif os.path.exists(f'./dados/distancias/{UF}.parquet'):
        distancias = pd.read_parquet(f'./dados/distancias/{UF}.parquet').rename(columns={'CD_SETOR': 'ID_SETOR'})    
    return distancias.sort_values(by=['CO_CNES','distancia'], ascending=True).reset_index(drop=True)

def format_population(x):
    import locale
    locale.setlocale(locale.LC_ALL, '')
    valor = f'{x:,}' 
    valor = valor.replace('.0','')
    return valor.replace(',','.')

def format_percentage(x):
    return f'{100*x:.2f}%'
