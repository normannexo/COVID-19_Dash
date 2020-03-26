################
## Main App #####
################


import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from datetime import timedelta

import plotly
import plotly.graph_objs as go
import datautils

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.CERULEAN]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

server = app.server


jh = datautils.JHdata()
print(jh.df[jh.df['Country/Region']=='Germany'][['date','confirmed']])

rki = datautils.RKIdata()
print(rki.df)


df_jh = jh.df
print("last update: " + str(jh.get_last_update() -timedelta(days=10)))
df_world = jh.get_current_world()

colors={
    "text":'black',
    'background': 'white'#'#0e2f63'
    
    }

gcolors=dict()

####
## plot layouts
###

plot_layout=go.Layout(
         paper_bgcolor=colors['background'],plot_bgcolor=colors['background'], font={'color':colors['text']},yaxis={'title': 'y-axis','fixedrange':True},xaxis={'title': 'x-axis','fixedrange':True}, dragmode=False
    )


########
## NavBar
#########

navbar = html.Div(
    [
        dcc.Location(id="url"),
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("World", href="/johnshopkins", id="page-1-link"),
                dbc.NavLink("Germany", href="/rki", id="page-2-link"),
                dbc.NavLink("Italy", href="/page-3", id="page-3-link"),
            ],
            brand="COVID-19",
            color='black',
            dark=True,
        )
    ]
)

#####
## Graphs
#####

# JH

world_fig = go.Figure()
world_fig.add_trace(go.Scatter(x=df_world.date,y=df_world.confirmed,
                    mode='lines',
                    name='confirmed'
                    ))
world_fig.add_trace(go.Scatter(x=df_world.date, y=df_world.deaths,
                    mode='lines', name='deaths'))
world_fig.update_layout(title_text="World", paper_bgcolor=colors['background'],plot_bgcolor=colors['background'], font={'color':colors['text']})

graph_world = dcc.Graph(
        id = "gWorld",
        figure = world_fig #px.line(df_world, x='date', y='confirmed')
)



map_fig = px.choropleth(df_jh, locations="Country/Region",
                    color="confirmed", # lifeExp is a column of gapminder
                    hover_name="Country/Region", # column to add to hover information
                    color_continuous_scale=px.colors.sequential.Viridis)
graph_map = dcc.Graph(
        figure=map_fig
    )

# RKI

germany_fig_df = rki.df.groupby(level=1).agg({'confirmed':'sum', 'deaths':'sum'}).reset_index()
germany_fig = go.Figure()
germany_fig.add_trace(go.Scatter(x=germany_fig_df.date,y=germany_fig_df.confirmed,
                    mode='lines',
                    name='confirmed'
                    ))
germany_fig.add_trace(go.Scatter(x=germany_fig_df.date, y=germany_fig_df.deaths,
                    mode='lines', name='deaths'))
germany_fig.update_layout(title_text="Germany", paper_bgcolor=colors['background'],plot_bgcolor=colors['background'], font={'color':colors['text']})

graph_germany = dcc.Graph(
        id = "gRKI_overall",
        figure = germany_fig #px.line(df_world, x='date', y='confirmed')
)

germany_fig_new_df = rki.df.groupby(level=1).agg({'confirmed_diff':'sum', 'deaths':'sum'}).reset_index()
germany_fig_new = go.Figure()
germany_fig_new.add_trace(go.Bar(x=germany_fig_new_df.date,y=germany_fig_new_df.confirmed_diff,
                    name='confirmed new'
                    ))
germany_fig_new.update_layout(paper_bgcolor=colors['background'],plot_bgcolor=colors['background'], font={'color':colors['text']})

graph_germany = dcc.Graph(
        id = "gRKI_overall",
        figure = germany_fig #px.line(df_world, x='date', y='confirmed')
)

graph_germany_new = dcc.Graph(
        id = "gRKI_overall_new",
        figure = germany_fig_new
)
controls = html.Div(
    
    [
        html.H4('Choose country:'),
        dcc.Dropdown(
            options= [
                
                {'label':col, 'value':col} for col in jh.get_countries()
            ]
            , id='country', value=['Germany'], multi=True, style={'background':colors ['background']}
        ),


    ]
    
)

country_card = dbc.Card(
    [
        dbc.CardImg(id='country_flag'),
        dbc.CardBody(
            [
                
                html.H4("Card title", className="card-title", id='card_title_country'),
                html.P(
                    "Some quick example text to build on the card title and "
                    "make up the bulk of the card's content.",
                    className="card-text",
                )
            ]
        ),
    ],
    style={"width": "18rem"},
)



country_table = dash_table.DataTable(
    id='table',
    #columns=[{"name": i, "id": i} for i in df.columns],
    #data=df.to_dict('records')
)



graph_country_cd = dcc.Graph(
        id = "gCountry_cd",
        config={
        'displayModeBar': False
    }
)

graph_country_c = dcc.Graph(
        id = "gCountry_c",
        config={
        'displayModeBar': False
    }
)

############
### LAYOUT
##############

# JH
graphRow0 = dbc.Row([dbc.Col(graph_world, md=12)], style={'padding':'3em'})
graphRow1 = dbc.Row([dbc.Col(controls, md=2), dbc.Col([dbc.Row(graph_country_c),dbc.Row(graph_country_cd )],md=10)])
jh_layout = html.Div([html.Br(), graphRow0, graphRow1])
#graphRow2 = dbc.Row([dbc.Col(country_table, md = 8)])

#RKI

rki_row0 = dbc.Row([dbc.Col(graph_germany, md=12)], style={'padding':'3em'})
rki_row1 = dbc.Row([dbc.Col(graph_germany_new, md=12)], style={'padding':'3em'})
rki_layout = html.Div([html.Br(),rki_row0, rki_row1])

app.layout = html.Div([navbar, dbc.Container(id="page-content", className="pt-4")], className='container', style={'background':colors['background'], 'padding':'2em'})

#################
#### CALBACKS###
################



@app.callback(
    Output("gCountry_cd", "figure"),
    [
        Input('country', "value")
    ],
)
def make_graph_cd(country):
    # minimal input validation, make sure there's at least one cluster
    plot_data = df_jh[(df_jh['Country/Region'].isin(country)) & (df_jh.date > (jh.get_last_update() - timedelta(days=21)))]
    #fig2 = px.bar(plot_data, x='date', y='confirmed')
    country_fig = go.Figure(layout=plot_layout)
#     country_fig.add_trace(go.Scatter(x=plot_data.date,y=plot_data.confirmed,
#                         mode='lines',
#                         name='confirmed'))
#     country_fig.add_trace(go.Scatter(x=plot_data.date, y=plot_data.sick,
#                         mode='lines',
#                         name='active'))
#     country_fig.add_trace(go.Scatter(x=plot_data.date, y=plot_data.deaths,
#                         mode='lines', name='deaths'))
    #country_fig.add_trace(go.Bar(x=plot_data.date, y=plot_data.confirmed_diff, name='confirmed_diff', color=country))
    for c in country:
        pdata = plot_data[plot_data['Country/Region']==c]
        country_fig.add_trace(go.Bar(x=pdata.date, y=pdata.confirmed_diff, name=c ))
    country_fig.update_layout(title_text="confirmed new")
    return country_fig

@app.callback(
    Output("gCountry_c", "figure"),
    [
        Input('country', "value")
    ],
)
def make_graph_c(country):
    # minimal input validation, make sure there's at least one cluster
    plot_data = df_jh[(df_jh['Country/Region'].isin(country)) & (df_jh.date > (jh.get_last_update() - timedelta(days=21)))]
    #fig2 = px.bar(plot_data, x='date', y='confirmed')
    country_fig = go.Figure(layout=plot_layout)
#     country_fig.add_trace(go.Scatter(x=plot_data.date,y=plot_data.confirmed,
#                         mode='lines',
#                         name='confirmed'))
#     country_fig.add_trace(go.Scatter(x=plot_data.date, y=plot_data.sick,
#                         mode='lines',
#                         name='active'))
#     country_fig.add_trace(go.Scatter(x=plot_data.date, y=plot_data.deaths,
#                         mode='lines', name='deaths'))
    #country_fig.add_trace(go.Bar(x=plot_data.date, y=plot_data.confirmed_diff, name='confirmed_diff', color=country))
    for c in country:
        pdata = plot_data[plot_data['Country/Region']==c]
        country_fig.add_trace(go.Bar(x=pdata.date, y=pdata.confirmed, name=c ))
    country_fig.update_layout(title_text="confirmed")
    return country_fig




@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/johnshopkins"]:
        return jh_layout
    elif pathname == "/rki":
        return rki_layout
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# @app.callback(
#     [
#     Output("table", "columns"),
#     Output("table", "data"),
#     Output("card_title_country", "children"),
#     Output("country_flag", 'src')
#     ],
#     [
#         Input('country', "value")
#     ],
# )
# def update_country_data(country):
#     table_data = df_jh[df_jh['Country/Region']==country].set_index('date').sort_index(ascending=False).head(10).reset_index()
#     iso2 = table_data.ISO2.max()
#     return [[{"name": i, "id": i} for i in table_data.columns],table_data.to_dict('records'), [country], "https://raw.githubusercontent.com/hjnilsson/country-flags/master/png100px/" + iso2.lower() + '.png']
#     





if __name__=='__main__':
    #app.run_server(debug=True)
    app.run_server(debug=True)

