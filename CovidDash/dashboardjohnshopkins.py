
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State

import plotly
import plotly.graph_objs as go
import datautils

jh = datautils.JHdata()


df_jh = jh.df
print("last update: " + str(jh.get_last_update()))
df_world = jh.get_current_world()



world_fig = go.Figure()
world_fig.add_trace(go.Scatter(x=df_world.date,y=df_world.confirmed,
                    mode='lines',
                    name='confirmed'))
world_fig.add_trace(go.Scatter(x=df_world.date, y=df_world.sick,
                    mode='lines',
                    name='active'))
world_fig.add_trace(go.Scatter(x=df_world.date, y=df_world.deaths,
                    mode='lines', name='deaths'))
world_fig.update_layout(title_text="World")

graph_world = dcc.Graph(
        id = "gWorld",
        figure = world_fig #px.line(df_world, x='date', y='confirmed')
)


external_stylesheets=[dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



controls = html.Div(
    
    [
        html.H4('Choose country:'),
        dcc.Dropdown(
            options= [
                
                {'label':col, 'value':col} for col in jh.get_countries()
            ]
            , id='country', value='Germany'
        ),


    ]
    
)



country_table = dash_table.DataTable(
    id='table',
    #columns=[{"name": i, "id": i} for i in df.columns],
    #data=df.to_dict('records')
)



graph_country = dcc.Graph(
        id = "gCountry"
)


country_tile = html.Div(
    [
        dbc.Row([dbc.Col(controls, md=4)]),
        dbc.Row([graph_country])
        
        
        ]
    
    
    )


graphRow0 = dbc.Row([dbc.Col(controls, md=4)])
graphRow1 = dbc.Row([dbc.Col(graph_world, md=4), dbc.Col(graph_country, md=4)])
graphRow2 = dbc.Row([dbc.Col(country_table, md = 8)])

app.layout = html.Div([html.Br(), graphRow0, graphRow1, graphRow2])


@app.callback(
    Output("gCountry", "figure"),
    [
        Input('country', "value")
    ],
)
def make_graph(country):
    # minimal input validation, make sure there's at least one cluster
    plot_data = df_jh[df_jh['Country/Region']==country]
    #fig2 = px.bar(plot_data, x='date', y='confirmed')
    country_fig = go.Figure()
    country_fig.add_trace(go.Scatter(x=plot_data.date,y=plot_data.confirmed,
                        mode='lines',
                        name='confirmed'))
    country_fig.add_trace(go.Scatter(x=plot_data.date, y=plot_data.sick,
                        mode='lines',
                        name='active'))
    country_fig.add_trace(go.Scatter(x=plot_data.date, y=plot_data.deaths,
                        mode='lines', name='deaths'))
    return country_fig



@app.callback(
    [
    Output("table", "columns"),
    Output("table", "data")
    ],
    [
        Input('country', "value")
    ],
)
def make_table(country):
    table_data = df_jh[df_jh['Country/Region']==country].set_index('date').sort_index(ascending=False).head(10).reset_index()
    return [[{"name": i, "id": i} for i in table_data.columns],table_data.to_dict('records')]
    



if __name__=='__main__':
    app.run_server(debug=True)
    

