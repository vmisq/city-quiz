import dash
from dash import dcc, html, no_update, ALL
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import random
from api import get_quiz_data

MIN_N = 3
DEFAULT_N = 5
MAX_N = 10

uf_options = [
    {"label": "Todos!", "value": 'ALL'},
    {"label": "Acre", "value": "AC"},
    {"label": "Alagoas", "value": "AL"},
    {"label": "Amapá", "value": "AP"},
    {"label": "Amazonas", "value": "AM"},
    {"label": "Bahia", "value": "BA"},
    {"label": "Ceará", "value": "CE"},
    {"label": "Distrito Federal", "value": "DF"},
    {"label": "Espírito Santo", "value": "ES"},
    {"label": "Goiás", "value": "GO"},
    {"label": "Maranhão", "value": "MA"},
    {"label": "Mato Grosso", "value": "MT"},
    {"label": "Mato Grosso do Sul", "value": "MS"},
    {"label": "Minas Gerais", "value": "MG"},
    {"label": "Pará", "value": "PA"},
    {"label": "Paraíba", "value": "PB"},
    {"label": "Paraná", "value": "PR"},
    {"label": "Pernambuco", "value": "PE"},
    {"label": "Piauí", "value": "PI"},
    {"label": "Rio de Janeiro", "value": "RJ"},
    {"label": "Rio Grande do Norte", "value": "RN"},
    {"label": "Rio Grande do Sul", "value": "RS"},
    {"label": "Rondônia", "value": "RO"},
    {"label": "Roraima", "value": "RR"},
    {"label": "Santa Catarina", "value": "SC"},
    {"label": "São Paulo", "value": "SP"},
    {"label": "Sergipe", "value": "SE"},
    {"label": "Tocantins", "value": "TO"},
]

startpage = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("City-Quiz!", className="text-center mb-4", style={'font-size': 144}), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Municípios por rodada"),
            dbc.Input(id='input-N', type="number", value=DEFAULT_N, min=MIN_N, max=MAX_N, step=1, className="mb-3", style={'font-size': 24})
        ], width={'size': 2, 'offset': 4}),
        dbc.Col([
            dbc.Label("Estados"),
            dbc.Select(id='input-UF', value='ALL', options=uf_options, className="mb-3", style={'font-size': 24})
        ], width=2),
    dbc.Row([
            dbc.RadioItems(
                options=[
                    {"label": "Fácil", "value": 1},
                    {"label": "Dificil", "value": 0},
                ],
                value=1,
                id="input-r",
                inline=True,
                style={'font-size': 24},
                className="text-center mb-3"
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Começar!", color="primary", className="text-center", id="start-button", n_clicks=0, style={'width': '100%', 'font-size': 36})
        ], width={'size': 2, 'offset': 5})
    ]),
], className="mt-1", fluid=True, style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'})

def build_page(table, data, instructions, r):
    return dbc.Container([
            dbc.Row([
                dbc.Col(html.Br(), width=12),
                dbc.Col(html.H1("City-Quiz!", className="text-left mb-4"), width=10),
                dbc.Col(
                    html.A(html.H1("Github", className="text-rigth mb-4"), href='https://github.com/vmisq/city-quiz'),
                    width=2, style={'text-align': 'right'}),
                html.Hr(),
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("Instruções", className="text-center mb-3"),
                    html.P(instructions, className="text-center mb-1"),
                    html.Hr(),
                    html.Br(),
                ], width=12),
            ]),
            dbc.Row(table),
            html.H1(' ', id=f'text-summary{"-r" if r else ""}', className="text-center mb-3"),
            dcc.Store(id='answers', data=data),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Enviar!",
                        color="primary",
                        className="text-center",
                        id=f'send-button{"-r" if r else ""}',
                        n_clicks=0,
                        style={'width': '100%', 'font-size': 18}
                    ),
                    dbc.Button("", id=f'giveup-button{"-r" if r else ""}', n_clicks=0, style={'display': 'none'})
                ], width={'size': 4, 'offset': 4}),
            ], id=f'after-validate{"-r" if r else ""}'),
            html.Br(),
        ])

def build_game_page(N, uf, r):
    data = get_quiz_data(int(N), uf)

    if r:
        data['municipio'] = {municipio_key: municipio_item.split(' - ')[0] for municipio_key, municipio_item in data['municipio'].items()} 

    table_header = [html.Thead(html.Tr([
        html.Th("#"),
        html.Th("Município"),
        html.Th("Gentílico"),
        html.Th("Mesoregião"),
        html.Th("População estimada"),
        html.Th("Bioma"),
        html.Th("Prefeito"),
        html.Th("IDH"),
    ]))]

    values = {
        'municipio': sorted([val for key, val in data['municipio'].items()]),
        'Gentílico': sorted([val for key, val in data['Gentílico'].items()]),
        'mesoregiao': sorted([val for key, val in data['mesoregiao'].items()]),
        'População estimada': sorted([float(val) for key, val in data['População estimada'].items()]),
        'Bioma': sorted([val for key, val in data['Bioma'].items()]),
        'Prefeito': sorted([val for key, val in data['Prefeito'].items()]),
        'IDH': sorted([val for key, val in data['IDH'].items()])
    }

    rows = []
    if r:
        random.shuffle(values['municipio'])
        random.shuffle(values['Gentílico'])
        for i, municipio in data['municipio'].items():
            rows.append(html.Tr([
                html.Th(int(i)+1),
                html.Th(dbc.Select(
                    options=[{"label": opt_j, "value": opt_j} for opt_j in values['municipio']],
                    id={"type": "select_municipio", "index": i}
                )),
                html.Th(dbc.Select(
                    options=[{"label": opt_j, "value": opt_j} for opt_j in values['Gentílico']],
                    id={"type": "select_gentilico", "index": i}
                )),
                html.Th(data['mesoregiao'][i]),
                html.Th(data['População estimada'][i]),
                html.Th(data['Bioma'][i]),
                html.Th(data['Prefeito'][i]),
                html.Th(data['IDH'][i]),
            ]))
        instructions = "Tente adivinhar o Município, e o seu gentílico, que corresponde a estes valores.\n" + \
                       "Após preencher todos, valide sua resposta pelo botão Enviar!\n" + \
                       "Caso não tenha acertado todos, não se preocupe, ainda pode editar e enviar novamente."
    else:
        for i, municipio in data['municipio'].items():
            rows.append(html.Tr([
                html.Th(int(i)+1),
                html.Th(municipio),
                html.Th(dbc.Input(id={"type": "input_gentilico", "index": i})),
                html.Th(dbc.Select(
                    options=[{"label": opt_j, "value": opt_j} for opt_j in values['mesoregiao']],
                    id={"type": "select_meso", "index": i}
                )),
                html.Th(dbc.Select(
                    options=[{"label": f'{opt_j:,.0f}'.replace(',', '.'), "value": opt_j} for opt_j in values['População estimada']],
                    id={"type": "select_pop", "index": i}
                )),
                html.Th(dbc.Select(
                    options=[{"label": opt_j, "value": opt_j} for opt_j in values['Bioma']],
                    id={"type": "select_bio", "index": i}
                )),
                html.Th(dbc.Select(
                    options=[{"label": opt_j, "value": opt_j} for opt_j in values['Prefeito']],
                    id={"type": "select_pref", "index": i}
                )),
                html.Th(dbc.Select(
                    options=[{"label": f'{float(opt_j):,.3f}'.replace('.', ','), "value": opt_j} for opt_j in values['IDH']],
                    id={"type": "select_idh", "index": i}
                ))
            ]))
        instructions = "Tente adivinhar qual o valor correto para cada Município.\n" + \
                       "Após preencher todos, valide sua resposta pelo botão Enviar!\n" + \
                       "Caso não tenha acertado todos, não se preocupe, ainda pode editar e enviar novamente."

    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_header + table_body, id='main-table', bordered=True)
    return build_page(table, data, instructions, r)

app = dash.Dash(
    external_stylesheets=[dbc.themes.SKETCHY]
)
app.config.suppress_callback_exceptions=True
app.title = 'City-Quiz!'

server = app.server

app.layout = html.Div([
    html.Script(f'document.documentElement.lang = "pt-BR";'),
    dcc.Location(id='url', refresh=True),
    dcc.Location(id='url-search', refresh=True),
    dbc.Spinner(
        html.Div(id='content', style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'height': '100vh'}),
        color="secondary"
    )
])

@app.callback(
    Output('content', 'children'),
    Output('content', 'style'),
    Input('url', 'search'),
    prevent_initial_call=True
)
def display_page(query_string):
    query_parameters = query_string.rsplit('?')[-1]
    params_dict = {param.split('=')[0].upper(): param.split('=')[1].upper() for param in query_parameters.split('&') if '=' in param}

    N_value = params_dict.get('N', None)
    UF_value = params_dict.get('UF', None)
    REVERSED_value = params_dict.get('REVERSED', None)
    r = REVERSED_value=='1' or REVERSED_value=='TRUE'

    if N_value:
        if not 3<=int(N_value)<=10:
            return startpage, None
        if not UF_value in [i['value'] for i in uf_options]:
            return build_game_page(N_value, 'ALL', r), None
        return build_game_page(N_value, UF_value, r), None
    else:
        return startpage, None
    
@app.callback(
    Output('url', 'search'),
    Input('start-button', 'n_clicks'),
    State('input-N', 'value'),
    State('input-UF', 'value'),
    State('input-r', 'value'),
    prevent_initial_call=True
)
def update_location(n1, N_value, UF_value, REVERSED_value):
    if n1>0:
        if N_value and UF_value:
            return f'?N={N_value}&UF={UF_value}&reversed={REVERSED_value}'
        raise PreventUpdate
    raise PreventUpdate

@app.callback(
    Output('after-validate', 'children'),
    Output({"type": "input_gentilico", "index": ALL}, "valid"),
    Output({"type": "select_meso", "index": ALL}, "valid"),
    Output({"type": "select_pop", "index": ALL}, "valid"),
    Output({"type": "select_bio", "index": ALL}, "valid"),
    Output({"type": "select_pref", "index": ALL}, "valid"),
    Output({"type": "select_idh", "index": ALL}, "valid"),
    Output({"type": "input_gentilico", "index": ALL}, "invalid"),
    Output({"type": "select_meso", "index": ALL}, "invalid"),
    Output({"type": "select_pop", "index": ALL}, "invalid"),
    Output({"type": "select_bio", "index": ALL}, "invalid"),
    Output({"type": "select_pref", "index": ALL}, "invalid"),
    Output({"type": "select_idh", "index": ALL}, "invalid"),
    Output('text-summary', 'children'),
    Input('send-button', 'n_clicks'),
    State('answers', 'data'),
    State({"type": "input_gentilico", "index": ALL}, "value"),
    State({"type": "select_meso", "index": ALL}, "value"),
    State({"type": "select_pop", "index": ALL}, "value"),
    State({"type": "select_bio", "index": ALL}, "value"),
    State({"type": "select_pref", "index": ALL}, "value"),
    State({"type": "select_idh", "index": ALL}, "value"),
    State('giveup-button', 'n_clicks'),
    prevent_initial_call=True
)
def validate_answers(n_clicks, data, input_gentilico, select_meso, select_pop, select_bio, select_pref, select_idh, gave_up):
    if n_clicks<=0:
        raise PreventUpdate
    results_gentilico = [
        all([
            k.lower().strip().replace(' ', '-') in [w.lower().strip().replace(' ', '-') for w in j.split(' ou ')]
            for k in (i or '').split(' ou ')
        ])
        for i,j in zip(input_gentilico, [k for _, k in data['Gentílico'].items()])
    ]
    results_meso = [i==j for i,j in zip(select_meso, [k for _, k in data['mesoregiao'].items()])]
    results_pop = [i==j for i,j in zip(select_pop, [k for _, k in data['População estimada'].items()])]
    results_bio = [i==j for i,j in zip(select_bio, [k for _, k in data['Bioma'].items()])]
    results_pref = [i==j for i,j in zip(select_pref, [k for _, k in data['Prefeito'].items()])]
    results_idh = [i==j for i,j in zip(select_idh, [k for _, k in data['IDH'].items()])]

    send_button = dbc.Button(
        "Enviar!",
        color="primary",
        className="text-center",
        id="send-button",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    )

    success_button = dbc.Button(
        "Jogar Outra Vez",
        color="success",
        className="text-center",
        id="new-button",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    )
    
    giveup_button = dbc.Button(
        "Ver Resultados",
        color="warning",
        outline=False,
        className="text-center",
        id="giveup-button",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    )

    new_button = dbc.Button(
        "Nova Rodada",
        color="info",
        outline=False,
        className="text-center",
        id="new-button",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    )

    return_button = dcc.Link(dbc.Button(
        "Voltar a Página Inicial",
        color="primary",
        outline=True,
        className="text-center",
        id="return-button",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    ), href='/')

    results = [*results_gentilico, *results_meso, *results_pop, *results_bio, *results_pref, *results_idh]
    text_summary = f"{sum(results)} de {len(results)} ({sum(results)/len(results):.0%})"

    if gave_up>0:
        text_summary =  f"- de {len(results)} (-%)"

    if all(results):
        after_buttons = [
            dbc.Col(return_button, width={'size': 2}),
            dbc.Col(success_button, width={'size': 4, 'offset': 2})
        ]
    else:
        after_buttons = [
            dbc.Col(return_button, width={'size': 2}),
            dbc.Col(send_button, width={'size': 4, 'offset': 2}),
            dbc.Col(giveup_button, width={'size': 2}),
            dbc.Col(new_button, width={'size': 2})
        ]

    return (
        after_buttons,
        results_gentilico,
        results_meso,
        results_pop,
        results_bio,
        results_pref,
        results_idh,
        [not i for i in results_gentilico],
        [not i for i in results_meso],
        [not i for i in results_pop],
        [not i for i in results_bio],
        [not i for i in results_pref],
        [not i for i in results_idh],
        text_summary
    )

@app.callback(
    Output('after-validate-r', 'children'),
    Output({"type": "select_municipio", "index": ALL}, "valid"),
    Output({"type": "select_gentilico", "index": ALL}, "valid"),
    Output({"type": "select_municipio", "index": ALL}, "invalid"),
    Output({"type": "select_gentilico", "index": ALL}, "invalid"),
    Output('text-summary-r', 'children'),
    Input('send-button-r', 'n_clicks'),
    State('answers', 'data'),
    State({"type": "select_municipio", "index": ALL}, "value"),
    State({"type": "select_gentilico", "index": ALL}, "value"),
    State('giveup-button-r', 'n_clicks'),
    prevent_initial_call=True
)
def validate_answers_reversed(n_clicks, data, select_municipio, select_gentilico, gave_up):
    if n_clicks<=0:
        raise PreventUpdate
    
    results_municipio = [i==j for i,j in zip(select_municipio, [k for _, k in data['municipio'].items()])]
    results_gentilico = [i==j for i,j in zip(select_gentilico, [k for _, k in data['Gentílico'].items()])]

    send_button = dbc.Button(
        "Enviar!",
        color="primary",
        className="text-center",
        id="send-button-r",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    )

    success_button = dbc.Button(
        "Jogar Outra Vez",
        color="success",
        className="text-center",
        id="new-button",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    )
    
    giveup_button = dbc.Button(
        "Ver Resultados",
        color="warning",
        outline=False,
        className="text-center",
        id="giveup-button-r",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    )

    new_button = dbc.Button(
        "Nova Rodada",
        color="info",
        outline=False,
        className="text-center",
        id="new-button",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    )

    return_button = dcc.Link(dbc.Button(
        "Voltar a Página Inicial",
        color="primary",
        outline=True,
        className="text-center",
        id="return-button",
        n_clicks=0,
        style={'width': '100%', 'font-size': 18}
    ), href='/')

    results = [*results_municipio, *results_gentilico]
    text_summary = f"{sum(results)} de {len(results)} ({sum(results)/len(results):.0%})"

    if gave_up>0:
        text_summary =  f"- de {len(results)} (-%)"

    if all(results):
        after_buttons = [
            dbc.Col(return_button, width={'size': 2}),
            dbc.Col(success_button, width={'size': 4, 'offset': 2})
        ]
    else:
        after_buttons = [
            dbc.Col(return_button, width={'size': 2}),
            dbc.Col(send_button, width={'size': 4, 'offset': 2}),
            dbc.Col(giveup_button, width={'size': 2}),
            dbc.Col(new_button, width={'size': 2})
        ]

    return (
        after_buttons,
        results_municipio,
        results_gentilico,
        [not i for i in results_municipio],
        [not i for i in results_gentilico],
        text_summary
    )

@app.callback(
    Output('url-search', 'search'),
    Input('new-button', 'n_clicks'),
    State('url-search', 'search'),
    prevent_initial_call=True
)
def refresh_game(n1, search):
    if n1>0:
        return search + '&new=true'
    raise PreventUpdate

@app.callback(
    Output('send-button', 'n_clicks'),
    Output({"type": "input_gentilico", "index": ALL}, "value"),
    Output({"type": "select_meso", "index": ALL}, "value"),
    Output({"type": "select_pop", "index": ALL}, "value"),
    Output({"type": "select_bio", "index": ALL}, "value"),
    Output({"type": "select_pref", "index": ALL}, "value"),
    Output({"type": "select_idh", "index": ALL}, "value"),
    Input('giveup-button', 'n_clicks'),
    State('send-button', 'n_clicks'),
    State('answers', 'data'),
    prevent_initial_call=True
)
def give_up(n1, n2, data):
    if n1<=0:
        raise PreventUpdate
    return (
        n2+1,
        [k for _, k in data['Gentílico'].items()],
        [k for _, k in data['mesoregiao'].items()],
        [k for _, k in data['População estimada'].items()],
        [k for _, k in data['Bioma'].items()],
        [k for _, k in data['Prefeito'].items()],
        [k for _, k in data['IDH'].items()],
    )

@app.callback(
    Output('send-button-r', 'n_clicks'),
    Output({"type": "select_municipio", "index": ALL}, "value"),
    Output({"type": "select_gentilico", "index": ALL}, "value"),
    Input('giveup-button-r', 'n_clicks'),
    State('send-button-r', 'n_clicks'),
    State('answers', 'data'),
    prevent_initial_call=True
)
def give_up_reversed(n1, n2, data):
    if n1<=0:
        raise PreventUpdate
    return (
        n2+1,
        [k for _, k in data['municipio'].items()],
        [k for _, k in data['Gentílico'].items()]
    )

if __name__ == "__main__":
    app.run_server(debug=True)