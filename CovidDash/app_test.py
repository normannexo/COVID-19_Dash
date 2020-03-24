import dash

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output


df_rki = pd.read_csv("http://www.nexolin.de/data/covid-19/rki/rki_data.csv", parse_dates=['date'])
df_rki  = df_rki.set_index(['Bundesland', 'date'])
df_trace1 = df_rki.loc[pd.IndexSlice[:,'17/03/2020'],:].reset_index()
print(df_trace1)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


fig = px.bar(df_trace1, x='Bundesland', y='confirmed')

df_trace2 = df_rki.groupby('date').confirmed.sum()
print(df_trace2)
fig2 = px.bar(df_trace2, x=df_trace2.index, y='confirmed')



app.layout = html.Div( children=[
    dcc.Input(id='my-id', value='initial value', type='text'),
    html.Div(id='my-div'),
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center'
        }
    ),

    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center'
    }),

   
    dcc.Graph(
        id='example-graph-3',
        figure=fig
    ),
    dcc.Graph(
        id='example-graph-4',
        figure=fig2
    )
    
])

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)




if (__name__ == '__main__'):
    app.run_server(debug=True)
