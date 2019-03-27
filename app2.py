from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
from pandas.io.json import json_normalize
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from flask import Flask, render_template, request
import webbrowser
import os

app = dash.Dash()
server = Flask(__name__)
STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'yelp'
COLLECTION_NAME = 'business'
FIELDS = {'business_id': True, 'name': True, 'state': True, 'stars':1,'is_open': True, 'categories': True,'latitude':True, 'longitude': True, '_id': False}
star_FIELDS = { 'stars': 1, '_id': 0}
rev_FIELDS = { 'stars': 1,'date': 1, '_id': 0}
eda_FIELDS = {'city' : True, 'state' : True, 'business_id': True, 'name': True, 'state': True, 'is_open': True, 'categories': True, '_id': False}

#df=pd.read_json(os.path.join(STATIC_PATH,'yelp_academic_dataset_business.json'))

connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collection = connection[DBS_NAME][COLLECTION_NAME]
projects = collection.find(projection=FIELDS, limit=100000)
df= json_normalize(json.loads(dumps(projects)))

#print(df)
@app.server.route('/home')
def serve_static():
    abc='world'
    return render_template('index.html',abc=abc)

app.layout = html.Div([
    html.H1('Yelp businesses'),
    html.Div(id='text-content'),
    dcc.Graph(id='map_walmart', figure={
        'data': [{
            'lat': df['latitude'],
            'lon': df['longitude'],
            'marker': {
                'color': df['stars'],
                'size': 8,
                'opacity': 0.6
            },
            'customdata': df['business_id'],
            'type': 'scattermapbox'
        }],
        'layout': {
            'mapbox': {
                'accesstoken': 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'
            },
            'hovermode': 'closest',
            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
        }
    })
])


@app.callback(
    dash.dependencies.Output('text-content', 'children'),
    [dash.dependencies.Input('map_walmart', 'hoverData')])
def update_text(hoverData):
    #print(hoverData)
    s = df[df['business_id'] == hoverData['points'][0]['customdata']]
    return html.A(html.H3(
        'The {}, {} {} opened in {}'.format(
            s.iloc[0]['name'],
            s.iloc[0]['state'],
            s.iloc[0]['city'],
            s.iloc[0]['stars']
        )
    ),href='\home')



app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=True,dev_tools_hot_reload=False)
