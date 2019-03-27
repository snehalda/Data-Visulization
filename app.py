import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
from pandas.io.json import json_normalize
import os

app = dash.Dash()

df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/'
    'cb5392c35661370d95f300086accea51/raw/'
    '8e0768211f6b747c0db42a9ce9a0937dafcbd8b2/'
    'indicators.csv')
STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'yelp'
COLLECTION_NAME = 'business'
FIELDS = {'business_id': True, 'name': True, 'state': True, 'stars':1,'review_count': True, 'categories': True,'latitude':0, 'longitude': 0, '_id': False}
star_FIELDS = { 'stars': 1, '_id': 0}
rev_FIELDS = { 'stars': 1,'date': 1, '_id': 0}
eda_FIELDS = {'city' : True, 'state' : True, 'business_id': True, 'name': True, 'state': True, 'is_open': True, 'categories': True, '_id': False}

#df=pd.read_json(os.path.join(STATIC_PATH,'yelp_academic_dataset_business.json'))

connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collection = connection[DBS_NAME][COLLECTION_NAME]
projects = collection.find(projection=FIELDS, limit=100000)
df= json_normalize(json.loads(dumps(projects)))
df=df.fillna(0)
df = df[df.categories.str.contains("Restaurant", na=False)]
available_indicators = pd.DataFrame(df['categories'].unique()).to_string(index=False)
print(available_indicators)
available_indicators = available_indicators.split(',')

print(available_indicators)
app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Fast Food'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Bar'
            ),
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'NV'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%'}),

    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=df['stars'].min(),
        max=df['stars'].max(),
        value=df['stars'].max(),
        step=None,
        marks={str(stars): str(stars) for stars in df['stars'].unique()}
    ), style={'width': '49%', 'padding': '0px 20px 20px 20px'})
])

@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    #print('graph')
    # print(df)
    # print('year value')
    # print(year_value)
    dff = df[df['stars'] == year_value]
    #print(dff)
    return {
        'data': [go.Scatter(
            x=dff[dff.categories.str.contains(xaxis_column_name, na=False)]['review_count'],
            y=dff[dff.categories.str.contains(yaxis_column_name, na=False)]['review_count'],
            text=dff[dff.categories.str.contains(yaxis_column_name, na=False)]['state'],
            customdata=dff[dff.categories.str.contains(yaxis_column_name, na=False)]['state'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }

def create_time_series(dff, axis_type, title):
    #list(dff)
    #print(dff)
    return {
        'data': [go.Bar(
            x=dff['stars'],
            y=dff['review_count'],
            marker=go.bar.Marker(
                color='rgb(55, 83, 109)'
            )
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }

@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    # print('y timeseries')
    # print(df)
    # print('country_name value')
    # print(country_name)
    dff = df[df['state'] == country_name]
    # print(dff)
    # print('xaxis coumn')
    # print(xaxis_column_name)
    print(list(dff))
    dff= dff[dff.categories.str.contains(xaxis_column_name, na=False)]
    #dff = dff[dff['categories'] == xaxis_column_name]
    #print(dff)
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)

@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
def update_x_timeseries(hoverData, yaxis_column_name, axis_type):

    print(hoverData)
    print(list(hoverData))
    dff = df[df['state'] == hoverData['points'][0]['customdata']]
    dff = dff[dff.categories.str.contains(yaxis_column_name, na=False)]
    #dff = dff[dff['categories'] == yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server()