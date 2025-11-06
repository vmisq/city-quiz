import pandas as pd
import requests
import json
import os
import datetime
import inspect
import asyncio

DAYS_TO_REFRESH = 365 #180000
PREFERED_FILTER = json.loads(os.environ.get('PREFERED_FILTER', '{}'))
MIN_POP_BALANCE = int(os.environ.get('MIN_POP_BALANCE', '0'))

def check_if_exists(func):
    def wrapper(*args, **kwargs):
        file_path = kwargs.get('file_path') or inspect.signature(func).parameters['file_path'].default
        file_path = file_path.replace('__id__', str(kwargs.get('id')))
        if os.path.exists(file_path):
            last_modified_date = os.path.getmtime(file_path)
            last_modified_date = datetime.datetime.fromtimestamp(last_modified_date)
            now = datetime.datetime.now()
            if (now - last_modified_date).days<=DAYS_TO_REFRESH:
                return pd.read_json(file_path)
        else:
            folder_name = '/'.join(file_path.split('/')[:-1])
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
        json_res = func(*args, **kwargs)
        with open(file_path, 'w') as f:
            json.dump(json_res, f)
        return pd.read_json(file_path)
    return wrapper

def parse_latest_value(res):
    latest_year = 0
    for year, value in res.items():
        year_int = int(year.rsplit('-')[-1])
        if value is not None and year_int>latest_year:
            latest_year = year_int
    return res.get(str(latest_year))

# May need to change to fetch multiple items at once
@check_if_exists
def get_municipios(file_path='data/municipios.json'):
    url = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
    response = requests.get(url)
    return [{
        'id': i['id'],
        'nome': i['nome'],
        'id_microregiao': i['microrregiao']['id'],
        'nome_microregiao': i['microrregiao']['nome'],
        'id_mesoregiao': i['microrregiao']['mesorregiao']['id'],
        'nome_mesoregiao': i['microrregiao']['mesorregiao']['nome'],
        'id_uf': i['microrregiao']['mesorregiao']['UF']['id'],
        'uf_sigla': i['microrregiao']['mesorregiao']['UF']['sigla'],
        'uf_nome': i['microrregiao']['mesorregiao']['UF']['nome']
    } for i in response.json() if i.get('microrregiao')]

@check_if_exists
def get_populacao_municipios(file_path='data/populacao-municipios.json'):
    url = 'https://servicodados.ibge.gov.br/api/v3/agregados/793/periodos/-6/variaveis/93?localidades=N6[all]'
    response = requests.get(url)
    return [{
        'id': i['localidade']['id'],
        'nome': i['localidade']['nome'],
        'populacao': parse_latest_value(i['serie'])
    } for i in response.json()[0]['resultados'][0]['series']]

@check_if_exists
def get_indicadores(id, indicadores, file_path='data/indicadores/__id__.json'):
    url = f"https://servicodados.ibge.gov.br/api/v1/pesquisas/-/indicadores/{'|'.join([str(i['id']) for i in indicadores])}/resultados/{id}"
    response = requests.get(url)
    return [{'id': i['id'], 'value': parse_latest_value(i['res'][0]['res'])} for i in response.json()]

def fetch_random_cities(df, N=5, uf='ALL'):
    if uf!='ALL':
        dff = df.query(f'uf_sigla=="{uf}"').copy()
    else:
        dff = df.copy()

    buffer = []
    try:
        if PREFERED_FILTER:
            df_prefered_region = dff \
                .query(' and '.join([f'({col_name}=="{col_value}")' for col_name, col_value in PREFERED_FILTER.items()])) \
                .sample(N//4+1)
            buffer.append(df_prefered_region)
            N -= len(df_prefered_region)
    except Exception as e:
        print(e)

    try:
        if MIN_POP_BALANCE:
            df_pop_filter = dff \
                .query(f'populacao > {MIN_POP_BALANCE}') \
                .sample(max(N-min(N, 2),2))
            buffer.append(df_pop_filter)
            N -= len(df_pop_filter)
    except Exception as e:
        print(e)

    df_no_filter = dff.sample(N)
    buffer.append(df_no_filter)

    return pd.concat(buffer).to_dict('records')

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

async def get_quiz_data_async(N=5, uf='ALL', load_all=False):
    df_municipios = get_municipios()
    df_populacao = get_populacao_municipios()
    if load_all:
        N_municipios = df_municipios.merge(df_populacao[['id', 'populacao']], on='id').to_dict('records')
    else:
        N_municipios = fetch_random_cities(df_municipios.merge(df_populacao[['id', 'populacao']], on='id'), N=N, uf=uf)
    
    def make_buffer(municipio, indicadores):
        df_buffer = get_indicadores(id=municipio['id'], indicadores=indicadores)
        df_buffer['municipio'] = municipio['nome'] + ' - ' + municipio['uf_sigla']
        df_buffer['mesoregiao'] = municipio['nome_mesoregiao']
        return df_buffer

    buffer = await asyncio.gather(*[
        asyncio.to_thread(make_buffer, municipio=municipio, indicadores=indicadores) for municipio in N_municipios
    ])

    df = pd.concat(buffer) \
        .merge(pd.DataFrame(indicadores), left_on='id', right_on='id') \
        .pivot(index=['municipio', 'mesoregiao'], columns='indicador', values='value') \
        .sample(frac=1) \
        .reset_index() \
        .to_json()

    return json.loads(df)

def get_quiz_data(*args, **kwargs):
    return asyncio.run(get_quiz_data_async(*args, **kwargs))

def persist_data():
    data = get_quiz_data(load_all=True)
    with open('data/all.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    persist_data()