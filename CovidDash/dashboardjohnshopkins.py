
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State

import plotly
import plotly.graph_objs as go
import data

jh = data.JHdata()


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
        dcc.Dropdown(
            options= [
                
                {'label':col, 'value':col} for col in jh.get_countries()
            ]
            , id='country', value='Germany'
        ),


    ]
    
)



#graphRow0 = dbc.Row([dbc.Col(controls, id='card1', md=3)])

pie = dcc.Graph(
        id = "pieGraph",
        figure = {
          "data": [
            {
              "values": [800, 345, 500],
              "labels": [
                "Positive",
                "Negative",
                "Neutral"
              ],
              "name": "Sentiment",
              "hoverinfo":"label+name+percent",
              "hole": .7,
              "type": "pie",
              "marker" : dict(color=['#05C7F2','#D90416','#D9CB04'])
              }],
          "layout": {
                "title" : dict(text ="Sentiment Analysis",
                               font =dict(
                               size=20,
                               color = 'white')),
                "paper_bgcolor":"#111111",
                "width": "2000",
                "annotations": [
                    {
                        "font": {
                            "size": 20
                        },
                        "showarrow": False,
                        "text": "",
                        "x": 0.2,
                        "y": 0.2
                    }
                ],
                "showlegend": False
              }
        }
)
bar = dcc.Graph(
        id = "3",
        figure ={
                  "data": [
                  {
                          'x':['Positive', 'Negative', 'Neutral'],
                          'y':[800, 345, 500],
                          'name':'SF Zoo',
                          'type':'bar',
                          'marker' :dict(color=[        '#05C7F2','#D90416','#D9CB04']),
                  }],
                "layout": {
                      "title" : dict(text ="Overall Sentiments",
                                     font =dict(
                                     size=20,
                                     color = 'white')),
                      "xaxis" : dict(tickfont=dict(
                          color='white')),
                      "yaxis" : dict(tickfont=dict(
                          color='white')),
                      "paper_bgcolor":"#111111",
                      "plot_bgcolor":"#111111",
                      "width": "2000",
                      #"grid": {"rows": 0, "columns": 0},
                      "annotations": [
                          {
                              "font": {
                                  "size": 20
                              },
                              "showarrow": False,
                              "text": "",
                              "x": 0.2,
                              "y": 0.2
                          }
                      ],
                      "showlegend": False
                  }
              }
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




graphRow1 = dbc.Row([dbc.Col(graph_world, md=4), dbc.Col(country_tile)])
app.layout = html.Div([html.Br(), graphRow1])


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



if __name__=='__main__':
    app.run_server(debug=True)
    

