# Mapa das Unidades Básicas de Saúde da APS

## Descrição

Este projeto foi desenvolvido pela Coordenação-Geral de Monitoramento, Avaliação e Inteligência Analítica da Secretaria de Atenção Primária à Saúde do Ministério da Saúde (CGMAIA/SAPS/MS), com o objetivo de possibilitar a visualização de informações essenciais para o planejamento e gestão da Atenção Primária à Saúde (APS). 

Foram criados três tipos de mapas, utilizando dados abertos disponibilizados pelo Governo Federal. Os três tipos de mapas disponíveis são:

1. **Demografia**: Informações sobre a população.
2. **Equipes**: Dados sobre as equipes de saúde.
3. **Cobertura da APS**: Mapas que mostram a abrangência da APS e sua cobertura.

### Mapas de Demografia

Para gerar o mapa de demografia, utilizamos scripts usando um notebook (scripts/demografia.ipynb).

### Mapas de Equipes

Para gerar o mapa de demografia, utilizamos scripts usando um notebook (scripts/equipes.ipynb).

### Mapas de cobertura APS

Para gerar o mapa de cobertura APS, utilizamos scripts usando um notebook (scripts/cobertura.ipynb).

#### Script para gerar distâncias

O script `scripts/gera_distancias.py` é responsável por gerar os arquivos em `dados/distancias`, utilizando a base de [setores do IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/26565-malhas-de-setores-censitarios-divisoes-intramunicipais.html). Ele retorna um DataFrame com as distâncias entre cada unidade de saúde e os setores censitários de um município, considerando um limite máximo de distância.

## Resultados Gerados

Os resultados serão armazenados na pasta `output/site/mapas`, que conterá três subpastas:

- `cobertura`: Resultados relacionados à cobertura da APS.
- `equipe`: Resultados referentes à equipe.
- `ruralidade`: Resultados sobre a ruralidade.

A página inicial do site pode ser acessada no caminho `output/site/index.html`, onde será possível visualizar todos os resultados gerados.


### **Pré-requisitos**

Antes de executar o projeto, é imprescindível que todas as bases estejam corretas. De antemão, será necessário gerar a base extraída do IBGE e outros arquivos. Para isso, execute o script `reconstruir_dados.py` com os seguintes comandos:

Para gerar os arquivos necessários:
```python
python scripts/reconstruir_dados.py
```
ou

Caso deseje remover os arquivos de entrada após a reconstrução, passe o parâmetro `True`:
```python
python scripts/reconstruir_dados.py True
```