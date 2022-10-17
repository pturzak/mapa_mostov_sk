import numpy as np
import pandas as pd
import gunicorn 

import plotly.express as px

from dash import Dash, dcc, html, Input, Output

app = Dash(__name__)
server = app.server 

df_mosty = pd.read_csv('./Data/sr_mosty_all.csv',
                       sep=',',
                       encoding='utf-8')

df_mosty = df_mosty.sort_values(by=['rok_data', 'stav_kod'],
                                ascending=[True, True])

app.layout = html.Div(children=[
    html.H1(children='Stav mostov'),

    html.Div(children=[
        html.Div(children=[
            dcc.Graph(
                id='plot-scatter-bridges'
            )
        ], style={ 'display':'inline-block'}),

        html.Div(children=[
            html.Label('Stav v roku'),
            dcc.Slider(
                2012, 2022, 11,
                value=2022,
                marks={2012:'2012', 2017:'2017', 2021:'2021', 2022:'2022'},
                id='year-slider'
            ),
            html.Br(),

            html.Label('Kategoria cesty'),
            dcc.Dropdown(
                df_mosty['ck_trieda'].unique(),
                df_mosty['ck_trieda'].unique(),
                multi=True,
                id='plot-road-cat-shown'
            ),
            html.Br(),

            html.Label('Technicky stav'),
            dcc.Dropdown(
                df_mosty['stav_slovom'].unique(),
                df_mosty['stav_slovom'].unique(),
                multi=True,
                id='plot-states-shown'
            ),
            html.Br(),

            html.Label('Zobrazujem '),
            html.Label(id='bridge-count'),
            html.Label(' mostov.'),
            html.Br(),
            html.Br(),

            html.Label('Zdroj údajov: '),
            dcc.Link(
                html.A('štatistické výstupy SSC'),
                       href='https://www.cdb.sk/sk/statisticke-vystupy.alej'
            )
        ], style={ 'display':'inline-block',
                   'padding':'20px'})
    ], style={'display':'flex', 'padding':'10px'}),

    html.Div(children=[
        dcc.Link(
            html.A('View source'),
                   href='https://github.com/pturzak/mapa_mostov_sk'
        )
    ])
])

@app.callback(
    Output('plot-scatter-bridges', 'figure'),
    Input('plot-states-shown', 'value'),
    Input('plot-road-cat-shown', 'value'),
    Input('year-slider', 'value'))
def update_plot(states_shown, road_cat_shown, year):
    df_plotted = df_mosty[df_mosty['stav_slovom'].isin(states_shown)\
                          & df_mosty['ck_trieda'].isin(road_cat_shown)\
                          & (df_mosty['rok_data']==year)]
    fig = px.scatter_mapbox(
        df_plotted,
        lat='lat',
        lon='lon',
        hover_data=['ID_most', 'ck_trieda', 'rok_postavenia', 'stav_slovom'],
        color='stav_slovom',
        width=1200,
        height=800,
        color_discrete_map={
            'Bezchybný': 'forestgreen',
            'Veľmi dobrý': 'forestgreen',
            'Dobrý': 'forestgreen',
            'Uspokojivý': 'gold',
            'Zlý': 'orangered',
            'Veľmi zlý': 'firebrick',
            'Havarijný': 'black',
            'Neznámy': 'gray'
        }
    )
    fig.update_layout(mapbox_style='carto-positron')

    return fig

@app.callback(
    Output('bridge-count', 'children'),
    Input('plot-states-shown', 'value'),
    Input('plot-road-cat-shown', 'value'),
    Input('year-slider', 'value'))
def update_bridge_count(states_shown, road_cat_shown, year):
    df_plotted = df_mosty[df_mosty['stav_slovom'].isin(states_shown)\
                          & df_mosty['ck_trieda'].isin(road_cat_shown)\
                          & (df_mosty['rok_data']==year)]

    return df_plotted.shape[0]

if __name__ == '__main__':
    app.run_server(debug=True)
