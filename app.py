import numpy as np
import pandas as pd

import plotly.express as px

from dash import Dash, dcc, html, Input, Output

app = Dash(__name__)

df_mosty = pd.read_csv('./Data/sr_co_most_dc_2021-01-01.csv',
                      sep=';',
                      encoding='cp1250')

# keep only some columns
df_mosty = df_mosty[
    ['Trieda cesty', 'Číslo cesty', 'Správcovské číslo mostu',
     'Identifikačné číslo mostu', 'rok postavenia',
     'stavebný stav - kód', 'Stavebný stav',
     'LongitudeE', 'LatitudeN']
]

# rename columns
df_mosty.columns = ['ck_trieda', 'ck_cislo', 'spravcovske_cislo',
     'ID_most', 'rok_postavenia',
     'stav_kod', 'stav_slovom',
     'lon', 'lat']

# clean the technical condition columns
df_mosty['stav_kod'] = df_mosty['stav_kod'].replace(np.nan, -1)
df_mosty['stav_kod'] = df_mosty['stav_kod'].astype(int)
df_mosty = df_mosty.sort_values(by='stav_kod', ascending=True)
df_mosty['stav_kod'] = df_mosty['stav_kod'].astype(str)

df_mosty['stav_slovom'] =  df_mosty['stav_slovom'].replace(np.nan, 'Neznámy')

# clean road category values
df_mosty['ck_trieda'] = df_mosty['ck_trieda'].replace(
    {
        'diaľnica':'Diaľnica',
        'privádzač diaľničný':'Diaľnica',
        'cesta I. triedy':'Cesta I. triedy',
        'cesta II. triedy':'Cesta II. triedy',
        'II. trieda - miestna zberná (MZ)':'Cesta II. triedy',
        'cesta III. triedy':'Cesta III. triedy',
        'III. trieda - miestna obslužná (MO)':'Cesta III. triedy',
        'miestna neurčená':'Miestna cesta'
    }
)


app.layout = html.Div(children=[
    html.H1(children='Stav mostov v 2021'),

    html.Div(children=[
        html.Div(children=[
            dcc.Graph(
                id='plot-scatter-bridges'
            )
        ], style={ 'display':'inline-block'}),

        html.Div(children=[
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
                html.A('štatistické výstupy SSC.'),
                       href='https://www.cdb.sk/sk/statisticke-vystupy.alej'
            )
        ], style={ 'display':'inline-block',
                   'padding':'20px'})
    ], style={'display':'flex', 'padding':'10px'})
])

@app.callback(
    Output('plot-scatter-bridges', 'figure'),
    Input('plot-states-shown', 'value'),
    Input('plot-road-cat-shown', 'value'))
def update_plot(states_shown, road_cat_shown):
    df_plotted = df_mosty[df_mosty['stav_slovom'].isin(states_shown)\
                          & df_mosty['ck_trieda'].isin(road_cat_shown)]
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
    fig.update_layout(mapbox_style='open-street-map')

    return fig

@app.callback(
    Output('bridge-count', 'children'),
    Input('plot-states-shown', 'value'),
    Input('plot-road-cat-shown', 'value'))
def update_bridge_count(states_shown, road_cat_shown):
    df_plotted = df_mosty[df_mosty['stav_slovom'].isin(states_shown)\
                          & df_mosty['ck_trieda'].isin(road_cat_shown)]

    return df_plotted.shape[0]

if __name__ == '__main__':
    app.run_server(debug=True)