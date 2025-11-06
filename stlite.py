
import streamlit as st
import random
import pandas as pd

st.set_page_config(layout="wide")
st.markdown('<link rel="stylesheet" href="styles.css">', unsafe_allow_html=True)

MIN_N, DEFAULT_N, MAX_N = 3, 5, 10
uf_options = {
    "Todos!": 'ALL',
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO",
}

def load_data():
    N = st.session_state.N
    uf = uf_options[st.session_state.uf]
    PREFERED_FILTER = {}
    MIN_POP_BALANCE = 0

    df = pd.read_json('data/all.json')
    df[['nome', 'uf_sigla']] = df['municipio'].str.split(' - ', n=1, expand=True)
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

    st.session_state.data = pd.concat(buffer).reset_index().to_dict()
    
    st.session_state.data['municipio'] = {municipio_key: municipio_item.split(' - ')[0] for municipio_key, municipio_item in st.session_state.data['municipio'].items()}
    data = st.session_state.data

    st.session_state.v = {
        'municipio': sorted([val for key, val in data['municipio'].items()]),
        'Gentílico': sorted([val for key, val in data['Gentílico'].items()]),
        # 'mesoregiao': sorted([val for key, val in data['mesoregiao'].items()]),
        # 'População estimada': sorted([float(val) for key, val in data['População estimada'].items()]),
        # 'Bioma': sorted([val for key, val in data['Bioma'].items()]),
        # 'Prefeito': sorted([val for key, val in data['Prefeito'].items()]),
        # 'IDH': sorted([val for key, val in data['IDH'].items()])
    }
    random.shuffle(st.session_state.v['municipio'])
    random.shuffle(st.session_state.v['Gentílico'])
    st.session_state.n_tentativas = 0
    st.session_state.give_up = False
    for i in range(st.session_state.N):
        st.session_state[f'm{i}_res'] = ''
        st.session_state[f'g{i}_res'] = ''


col_title, col_N, col_uf, col_source = st.columns(4)
with col_title:
    st.title("City-Quiz!")
with col_N:
    N = st.number_input("Municípios por rodada", MIN_N, MAX_N, DEFAULT_N, 1, on_change=load_data, key='N')
with col_uf:
    uf_box = st.selectbox("Estado", uf_options.keys(), on_change=load_data, key='uf')
    uf = uf_options[uf_box]
with col_source:
    logo_color_filter = '0' if st.context.theme.type=='light' else '100'
    st.markdown(f"""
        <a href="https://github.com/vmisq/city-quiz" target="_blank" style="position: absolute; top: 10px; right: 10px;;">
            <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/github.svg" width="72" height="72" style="filter: invert({logo_color_filter}%) brightness({logo_color_filter}%)"/>
        </a>
    """, unsafe_allow_html=True) #"""

if 'data' not in st.session_state.keys():
    load_data()
data = st.session_state.data
values = st.session_state.v
v_m = [''] + values['municipio']
v_g = [''] + values['Gentílico']

st.markdown("""
    ### Instruções
    Tente adivinhar o Município, e o seu gentílico, que corresponde a estes valores.
    Após preencher todos, valide sua resposta pelo botão Enviar!
    Caso não tenha acertado todos, não se preocupe, ainda pode editar e enviar novamente.
""")

with st.form("game"):
    col_m, col_g, col_meso, col_pop, col_bio, col_pref, col_idh = st.columns(7)
    for i, _ in data['municipio'].items():
        if st.session_state.give_up:
            with col_m:
                st.text_input('Município' + st.session_state[f'm{i}_res'], data['municipio'][i], disabled=True, key=f"m{i}_res_show")
            with col_g:
                st.text_input("Gentílico" + st.session_state[f'g{i}_res'], data['Gentílico'][i], disabled=True, key=f"g{i}_res_show")
        else:
            with col_m:
                idx = 0
                if st.session_state.n_tentativas:
                    idx = v_m.index(st.session_state[f'm{i}'])
                select_municipio = st.selectbox('Município' + st.session_state[f'm{i}_res'], v_m, key=f"m{i}", index=idx)
            with col_g:
                idx = 0
                if st.session_state.n_tentativas:
                    idx = v_g.index(st.session_state[f'g{i}'])
                select_gentilico = st.selectbox("Gentílico" + st.session_state[f'g{i}_res'], v_g, key=f"g{i}", index=idx)
        with col_meso:
            st.text_input("Mesoregião", data['mesoregiao'][i], disabled=True, key=f"meso{i}")
        with col_pop:
            st.text_input("Pop. estimada", data['População estimada'][i], disabled=True, key=f"pop{i}")
        with col_bio:
            st.text_input("Bioma", data['Bioma'][i], disabled=True, key=f"bio{i}")
        with col_pref:
            st.text_input("Prefeito", data['Prefeito'][i], disabled=True, key=f"pref{i}")
        with col_idh:
            st.text_input("IDH", data['IDH'][i], disabled=True, key=f"idh{i}")

    if st.session_state.n_tentativas:
        st.markdown(f"""
            ## {st.session_state.text_summary}
            ### # Tentativas: {st.session_state.n_tentativas}
        """)

    col_send, col_results, col_replay = st.columns(3)
    with col_send:
        if st.form_submit_button("Enviar", width='stretch', type="primary", disabled=st.session_state.give_up):
            st.session_state.n_tentativas += 1
            results = []
            for i in range(st.session_state.N):
                if st.session_state[f'm{i}'] == data['municipio'][i]:
                    st.session_state[f'm{i}_res'] = ' :white_check_mark:'
                    results.append(1)
                else:
                    st.session_state[f'm{i}_res'] = ' :x:'
                    results.append(0)
                if st.session_state[f'g{i}'] == data['Gentílico'][i]:
                    st.session_state[f'g{i}_res'] = ' :white_check_mark:'
                    results.append(1)
                else:
                    st.session_state[f'g{i}_res'] = ' :x:'
                    results.append(0)
            st.session_state.text_summary = f"{sum(results)} de {len(results)} ({sum(results)/len(results):.0%})"
            st.rerun()

    with col_results:
        if st.session_state.n_tentativas:
            if st.form_submit_button('Ver Resultados', width='stretch', type="secondary", disabled=st.session_state.give_up):
                st.session_state.give_up = True
                for i in range(st.session_state.N):
                    st.session_state[f'm{i}_res'] = st.session_state[f'm{i}_res']
                    st.session_state[f'g{i}_res'] = st.session_state[f'g{i}_res']
                st.rerun()

    with col_replay:
        if st.session_state.n_tentativas:
            if st.form_submit_button('Jogar Novamente', width='stretch', type="secondary"):
                load_data()
                st.rerun()