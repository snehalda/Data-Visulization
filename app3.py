import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import cufflinks as cf
cf.go_offline()


app = dash.Dash()

app.layout = html.Div([
    html.H1('Stock Tickers'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
        ],
        value=['COKE'],
        multi = True,
    ),
    dcc.Graph(id='my-graph')
])
@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def plot_time_series(dropdown_value):

    #print('here')
    path = "C:\\Users\\Snehal\Downloads\\yelp_checkin.csv"
    check_in = pd.read_csv(path)
    check_in = check_in.loc[check_in['business_id'] == '3Mc-LxcqeguOXOVT_2ZtCg']
    check_in.fillna(0)
    df = check_in.groupby(['weekday', 'hour'])['checkins'].sum()
    df = df.reset_index()
    df = df.pivot(index='hour', columns='weekday')[['checkins']]
    df.columns = df.columns.droplevel()
    df = df.reset_index()
    # Workaround for not being able to sort the values by hour
    df.hour = df.hour.apply(lambda x: str(x).split(':')[0])
    df.hour = df.hour.astype(int)
    # Sort the hour column
    df = df.sort_values('hour')
   #

    df = df[['hour', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']]
    df = check_in.groupby(['weekday', 'hour', ])['checkins'].sum().to_frame().reset_index()
    df = df.pivot(index='hour', columns='weekday')[['checkins']]
    #print(k.iplot(asFigure=True))

    print(df)
    json_stars = df.to_json(orient='split')

    # df = pd.DataFrame()
    # for x in dropdown_value:
    #     dat_x=pd.read_csv("C://Users//Snehal//Downloads//AAPL.csv")
    #     dat_x.set_index("Date", inplace= True)
    #     df=pd.concat([df,dat_x.Close],axis=1)
    #     print(df)
    #     print('***********************')
    # df.columns=dropdown_value
    # print(df.iplot(asFigure=True))
    return  df.iplot(asFigure=True)

if __name__ == '__main__':
    app.run_server()