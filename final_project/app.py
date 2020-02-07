import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd


opendata : pd.DataFrame = pd.read_csv(os.path.join(os.path.dirname(__file__), 'opendata.csv'), encoding='cp1251')
opendata.date = pd.to_datetime(opendata.date)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# colors = {
#     'background': '#111111',
#     'text': '#7FDBFF'
# }

app.layout = html.Div([
    html.Div([
                html.Div([
                    html.Label('Выберите параметр:'),
                    dcc.Dropdown(
                        id='param',
                        options=[{'label': s, 'value': s} for s in opendata.name.unique()]
                    )
                ]),
                html.Div([
                    html.Label('Выберите один или несколько регионов:'),
                    dcc.Dropdown(
                        id='region',
                        options=[{'label': s, 'value': s} for s in opendata.region.unique()],
                        multi=True)
                    ])
    ], style={'columnCount': 2}),
    dcc.Graph(id='graphic',),
    # dcc.Slider(
    #         id='year-slider',
    #         min=opendata['date'].min(),
    #         max=opendata['date'].max(),
    #         value=opendata['date'].min().year,
    #        # marks={str(year): str(year) for year in opendata['date'].unique()},
    #         step=None
    #     )
], style={'columnCount': 1})


# @app.callback(
#     Output('region', 'options'),
#     [Input('param', 'value')])
# def update_region_dropdown(selected_param):
#     return [{'label': s, 'value': s} for s in datasets[selected_param].region.unique()]


@app.callback(
    Output('graphic', 'figure'),
    [Input('param', 'value'),
     Input('region', 'value')])
def update_region_dropdown(param_value, region_value):
    if param_value and region_value:
        df = opendata.loc[opendata.name == param_value]
        #df = df.loc[df.region == region_value[0]]
        return {'data': [
            dict(
                x=df[df.region == region].date,
                y=df[df.region == region].value,
                mode='lines',
                name=region,
                line={
                    'size': 15,
                    'opacity': 0.5,
                    'line': {'width': 0.5, 'color': 'white'}
                }) for region in region_value],
               'layout': dict(
                            xaxis={'title': 'Дата'},
                            yaxis={'title': param_value},
                            margin={'l': 150, 'b': 40, 't': 10, 'r': 150},
                            legend={'x': 0, 'y': 1, },
                            hovermode='closest')
        }
    else:
        return {'data': []}


if __name__ == '__main__':
    app.run_server(debug=True)
