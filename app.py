import numpy as np
import pandas as pd
import gunicorn 

import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, State

app = Dash(__name__)
server = app.server 
    
df_mosty = pd.read_csv('./Data/sr_mosty_all.csv',
                       sep=',',
                       encoding='utf-8')

df_mosty = df_mosty.sort_values(by=['rok_data', 'stav_kod'],
                                ascending=[True, True])
years_available = [x for x in range(2012, 2025, 1)]

default_zoom = 6.7
default_lat = 48.8
default_lon = 19.7

app.layout = html.Div(children=[
    html.H3(children='Stav mostov podľa cestnej databanky'),
    html.Div(children=[
            html.Div(children=[
                dcc.Graph(
                    id='plot-scatter-bridges',
                    style={'width': '80vw',
                            'height': '90vh'}
                )
            ], style={'display':'inline-block'}
                      ),
            html.Div(children=[
                html.Label('Stav v roku'),
                dcc.Dropdown(
                    options=years_available,
                    value=2024,
                    multi=False,
                    id='year-shown'
                ),
                html.Br(),

                html.Label('Kategória cesty'),
                dcc.Dropdown(
                    df_mosty['ck_trieda'].unique(),
                    df_mosty['ck_trieda'].unique(),
                    multi=True,
                    id='plot-road-cat-shown'
                ),
                html.Br(),

                html.Label('Technický stav'),
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
                ),
                html.Br(),

                dcc.Link(
                    html.A('View source'),
                    href='https://github.com/pturzak/mapa_mostov_sk'
                )
            ], style={ 'display':'inline-block',
                       'padding':'5px',
                       'width':'350px'})
    ], style={'display':'flex', 'padding':'5px'}),
])

@app.callback(
    Output('plot-scatter-bridges', 'figure'),
    [Input('plot-states-shown', 'value'),
    Input('plot-road-cat-shown', 'value'),
    Input('year-shown', 'value')],
    [State('plot-scatter-bridges', 'figure')])
def update_plot(states_shown, road_cat_shown, year, prev_figure):
    df_plotted = df_mosty[df_mosty['stav_slovom'].isin(states_shown)\
                          & df_mosty['ck_trieda'].isin(road_cat_shown)\
                          & (df_mosty['rok_data']==year)]
    fig = px.scatter_mapbox(
        df_plotted,
        lat='lat',
        lon='lon',
        hover_data=['ID_most', 'ck_trieda', 'rok_postavenia', 'stav_slovom'],
        color='stav_slovom',
        color_discrete_map={
            'Bezchybný': 'forestgreen',
            'Veľmi dobrý': 'forestgreen',
            'Dobrý': 'limegreen',
            'Uspokojivý': 'gold',
            'Zlý': 'orangered',
            'Veľmi zlý': 'firebrick',
            'Havarijný': 'black',
            'Neznámy': 'gray'
        }
        # color_discrete_map={
        #     'Bezchybný': '#006837',
        #     'Veľmi dobrý': '#4bb05c',
        #     'Dobrý': '#b7e075',
        #     'Uspokojivý': '#fffebe',
        #     'Zlý': '#ea5739',
        #     'Veľmi zlý': '#a50026',
        #     'Havarijný': 'black',
        #     'Neznámy': 'gray'
        # }
    )
    # fig.update_layout(mapbox_style='carto-positron')
    # turn off interaction with legend
    fig.update_layout(mapbox_style='carto-positron',
                      legend=dict(
                          itemclick=False,
                          itemdoubleclick=False,
                          title='Technický stav'
                        )
                      )
    # retain zoom and center even when the Input changes
    if prev_figure\
        and ('layout' in prev_figure)\
        and ('mapbox' in prev_figure['layout']):

        fig.update_layout(
            mapbox=dict(
                    zoom=prev_figure['layout']['mapbox'].get('zoom',
                                                             default_zoom),
                    center=prev_figure['layout']['mapbox']\
                                .get('center',
                                     {'lat': default_lat,
                                      'lon': default_lon}
                                )
            ),
        )

    else:
        fig.update_layout(
            mapbox=dict(
                zoom=default_zoom,
                center=go.layout.mapbox.Center(
                    lat=default_lat,
                    lon=default_lon
                )
            ),
        )

    return fig

@app.callback(
    Output('bridge-count', 'children'),
    Input('plot-states-shown', 'value'),
    Input('plot-road-cat-shown', 'value'),
    Input('year-shown', 'value'))
def update_bridge_count(states_shown, road_cat_shown, year):
    df_plotted = df_mosty[df_mosty['stav_slovom'].isin(states_shown)\
                          & df_mosty['ck_trieda'].isin(road_cat_shown)\
                          & (df_mosty['rok_data']==year)]

    return df_plotted.shape[0]

if __name__ == '__main__':
    app.run_server(debug=True)
