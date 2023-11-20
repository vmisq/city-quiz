import pandas as pd
import requests
import json
import os
import datetime
import inspect

def check_if_exists(func):
    def wrapper(*args, **kwargs):
        file_path = kwargs.get('file_path') or inspect.signature(func).parameters['file_path'].default
        if len(args):
            file_path = file_path.replace('__id__', str(args[0]))
        if os.path.exists(file_path):
            last_modified_date = os.path.getmtime(file_path)
            last_modified_date = datetime.datetime.fromtimestamp(last_modified_date)
            now = datetime.datetime.now()
            if (now - last_modified_date).days<=30:
                return pd.read_json(file_path)
        json_res = func(*args, **kwargs)
        with open(file_path, 'w') as f:
            json.dump(json_res, f)
        return pd.read_json(file_path)
    return wrapper

# May need to change to fetch multiple items at once
@check_if_exists
def get_municipios(file_path='data/municipios.json'):
    url = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
    response = requests.get(url)
    return [{
        'id': i['id'],
        'nome': i['nome'],
        'id_uf': i['microrregiao']['mesorregiao']['UF']['id'],
        'uf_sigla': i['microrregiao']['mesorregiao']['UF']['sigla'],
        'uf_nome': i['microrregiao']['mesorregiao']['UF']['nome']
    } for i in response.json()]

@check_if_exists
def get_indicadores(id, indicadores, file_path='data/indicadores-__id__.json'):
    def parse_latest_value(res):
        latest_year = 0
        for year, value in res.items():
            year_int = int(year.rsplit('-')[-1])
            if value is not None and year_int>latest_year:
                latest_year = year_int
        return res.get(str(latest_year))
    
    url = f"https://servicodados.ibge.gov.br/api/v1/pesquisas/-/indicadores/{'|'.join([str(i['id']) for i in indicadores])}/resultados/{id}"
    response = requests.get(url)
    return [{'id': i['id'], 'value': parse_latest_value(i['res'][0]['res'])} for i in response.json()]

def fetch_random_cities(df, N=5, uf='ALL'):
    if uf!='ALL':
        return df.query(f'uf_sigla=="{uf}"').sample(N).to_dict('records')
    return df.sample(N).to_dict('records')

indicadores = [
    {'id': 29171, 'indicador': 'População estimada'},
    {'id': 29166, 'indicador': 'População'},
    {'id': 29167, 'indicador': 'Área da unidade territorial'},
    {'id': 29170, 'indicador': 'Prefeito'},
    {'id': 60409, 'indicador': 'Gentílico'},
    {'id': 77861, 'indicador': 'Bioma'},
    {'id': 30255, 'indicador': 'IDH'},
    {'id': 47000, 'indicador': 'PIB per capita'}
]

def get_quiz_data(N=5, uf='ALL'):
    df_municipios = get_municipios()
    N_municipios = fetch_random_cities(df_municipios, N=N, uf=uf)
    
    buffer = []
    for municipio in N_municipios:
        df_buffer = get_indicadores(municipio['id'], indicadores)
        df_buffer['municipio'] = municipio['nome'] + ' - ' + municipio['uf_sigla']
        buffer.append(df_buffer)

    df = pd.concat(buffer) \
            .merge(pd.DataFrame(indicadores), left_on='id', right_on='id') \
            .pivot(index='municipio', columns='indicador', values='value') \
            .sample(frac=1) \
            .reset_index() \
            .to_json()

    return json.loads(df)









### OLD
# @check_if_exists
# def get_indicadores_panorama(file_path='data/indicadores-panorama.json'):
#     def parse_levels(x):
#         for i in x:
#             yield {
#                 'id': i['id'],
#                 'indicador': i['indicador'],
#                 'posicao': i['posicao']
#             }
#             child = i.get('children')
#             if child:
#                 for j in parse_levels(child):
#                     yield j
# 
#     url = 'https://servicodados.ibge.gov.br/api/v1/pesquisas/10058/indicadores'
#     response = requests.get(url)
#     return [i for i in parse_levels(response.json())]