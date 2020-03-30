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
import math
import plotly
import plotly.graph_objs as go
import datautils
from flask_caching import Cache

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.CERULEAN]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title = "COVID-19 Dashboard"
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
server = app.server


TIMEOUT = 60*60*2

jh = datautils.JHdata()
rki = datautils.RKIdata
italy = datautils.Italydata()

@cache.memoize(timeout=TIMEOUT)
def update_jh():
    global jh
    jh.update_data()
   
@cache.memoize(timeout=TIMEOUT)
def update_rki():
    global rki
    rki =  datautils.RKIdata()

@cache.memoize(timeout=TIMEOUT)
def update_it():
    global italy
    italy =  datautils.Italydata()




### 
## GET DATA
######

#jh = datautils.JHdata()
#print(jh.df[jh.df['Country/Region']=='Germany'][['date','confirmed']])

#rki = datautils.RKIdata()
#print(rki.df)

#it = datautils.Italydata()



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
                dbc.NavLink("Italy", href="/italy", id="page-3-link"),
            ],
            brand="COVID-19",
            color='black',
            dark=True,
        )
    ]
)


#######
#### Source card

def create_source_div(src, link):
    div = html.Div(
            ['Source: ', html.A(src, href=link)]
        )
   

    return div
#####
## Graphs and Tables
#####

# JH

def get_world_graphs():
    df_world = jh.get_current_world()
    print(df_world)
    world_fig = go.Figure(layout=plot_layout)
    world_fig.add_trace(go.Scatter(x=df_world.date,y=df_world.confirmed,
                        mode='lines+markers',
                        name='confirmed'
                        ))
    world_fig.add_trace(go.Scatter(x=df_world.date, y=df_world.deaths,
                        mode='lines+markers', name='deaths'))
    world_fig.update_layout(title_text="World", yaxis_title='cumulative confirmed cases', xaxis_title='date')
    graph_world = dcc.Graph(
        id = "gWorld",
        figure = world_fig
        )
    
    
    table_world_data =  jh.df.groupby('date').agg({'confirmed':'sum', 'confirmed_diff':'sum', 'deaths':'sum'}).reset_index().nlargest(5,'date')
    print(table_world_data)
    table_world_data['date'] = table_world_data['date'].dt.strftime('%Y/%m/%d')
    table_world_data.columns= ['date', 'confirmed', 'confirmed new', 'deaths']
    table_columns=[{"name": i, "id": i} for i in table_world_data.columns]
    
    
    table_world = dash_table.DataTable(
        id='world_table',
        columns=table_columns,
        data = table_world_data.to_dict('records'),
        style_cell = {
                    'font_family': 'Arial',
                    'font_size': '1.4em',
                    'text_align': 'center'
                },
        style_as_list_view = True
    )


    
    ####
    ### Controls
    #####
    ddoptions = [{'label':col, 'value':col} for col in jh.get_countries()]
    controls_dd_country = html.Div(
        
        [
            html.H4('Choose countries:', style={'color':'black'}),
            dcc.Dropdown(
                id='country', value=['Germany', 'Italy', 'US'], multi=True, style={'background':'white', 'color':'black'},
                options=ddoptions
                
            ),
    
    
        ]
        
    )
    
    return graph_world, table_world, controls_dd_country



def get_radio_items():
    ritems = dbc.FormGroup([
        html.H4('Choose type:',  style={'color':'black'}),
      dbc.RadioItems(
            options=[
                {"label": "confirmed cases", "value": 'confirmed'},
                {"label": "deaths", "value": 'deaths'},
            ],
            value='confirmed',
            id="type_input",
        )
    ])
    return ritems
    







# RKI

def get_germany_graphs():
    
    germany_fig_df = rki.df.groupby(level=1).agg({'confirmed':'sum', 'deaths':'sum'}).reset_index()
    germany_fig = go.Figure(layout=plot_layout)
    germany_fig.add_trace(go.Scatter(x=germany_fig_df.date,y=germany_fig_df.confirmed,
                        mode='lines+markers',
                        name='confirmed'
                        ))
    germany_fig.add_trace(go.Scatter(x=germany_fig_df.date, y=germany_fig_df.deaths,
                        mode='lines+markers', name='deaths'))
    germany_fig.update_layout(title_text="Germany")
    
    graph_germany = dcc.Graph(
            id = "gRKI_overall",
            figure = germany_fig #px.line(df_world, x='date', y='confirmed')
    )
    
    germany_fig_new_df = rki.df.groupby(level=1).agg({'confirmed_diff':'sum', 'deaths':'sum'}).reset_index()
    germany_fig_new = go.Figure(layout=plot_layout)
    germany_fig_new.add_trace(go.Bar(x=germany_fig_new_df.date,y=germany_fig_new_df.confirmed_diff,
                        name='confirmed new'
                        ))
    germany_fig_new.update_layout(paper_bgcolor=colors['background'],plot_bgcolor=colors['background'], font={'color':colors['text']})
    
    graph_germany_new = dcc.Graph(
            id = "gRKI_overall_new",
            figure = germany_fig_new
    )
    
    ### controls
    ddoptions = [{'label':col, 'value':col} for col in rki.get_states()]
    controls_dd_states = html.Div(
        
        [
            html.H4('Choose federal states:', style={'color':'black'}),
            dcc.Dropdown(
                id='states', value=['Bayern', 'Nordrhein-Westfalen'], multi=True, style={'background':'white', 'color':'black'},
                options=ddoptions
                
            ),
    
    
        ]
        
    )
        
    
    return graph_germany, graph_germany_new, controls_dd_states



#table_data = germany_fig_df = rki.df.groupby(level=1).agg({'confirmed':'sum', 'confirmed_diff':'sum', 'deaths':'sum'}).reset_index()


#####
### Italy - Graphs and Tables
#### 
def get_italy_graphs():
    update_it()
    italy_overall = italy.df.loc[(italy.get_last_update()-timedelta(days=28)):].reset_index()
    italy_fig = go.Figure(layout=plot_layout)
    italy_fig.add_trace(go.Scatter(x=italy_overall.date,y=italy_overall.confirmed,
                        mode='lines+markers',
                        name='confirmed'
                        ))
    italy_fig.add_trace(go.Scatter(x=italy_overall.date, y=italy_overall.deaths,
                        mode='lines+markers', name='deaths'))
    italy_fig.update_layout(title_text="Italy")
    
    graph_italy = dcc.Graph(
            id = "gItaly",
            figure = italy_fig #px.line(df_world, x='date', y='confirmed')
    )
    
    
    italy_new_fig = go.Figure(layout=plot_layout)
    italy_new_fig.add_trace(go.Bar(x=italy_overall.date,y=italy_overall.confirmed_new,
                        name='confirmed new'
                        ))
    italy_new_fig.update_layout(title_text="Italy - confirmed new")
    
    graph_italy_new = dcc.Graph(
            id = "gItalyNew",
            figure = italy_new_fig
    )
    
    return graph_italy, graph_italy_new






# JH graphs countries

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

graph_country_progress  = dcc.Graph(
        id = "gCountry_p",
        config={
        'displayModeBar': False
    }
)



#### graphs states rki
graph_rki_cd = dcc.Graph(
        id = "gGermany_cd",
        config={
        'displayModeBar': False
    }
)

graph_rki_c = dcc.Graph(
        id = "gGermany_c",
        config={
        'displayModeBar': False
    }
)

graph_rki_progress  = dcc.Graph(
        id = "gGermany_p",
        config={
        'displayModeBar': False
    }
)
############
### LAYOUT
##############

# JH

def get_jh_layout():
    update_jh()
    sdiv = create_source_div(' Johns Hopkins CSSE', 'https://github.com/CSSEGISandData/COVID-19')
    graph_world, table_world, dd_country = get_world_graphs()
    rows_jh_list = [
        sdiv,
        dbc.Row([dbc.Col(graph_world, md=12)], style={'padding':'3em'}),
        dbc.Row(html.H4('Development in last 5 days:', style={'color':'black'})),
        dbc.Row([dbc.Col(table_world, md=12)]),
        html.Br(),html.Br(),
        dbc.Row([dbc.Col(dd_country, md=8), dbc.Col(get_radio_items(), md=4)], justify='center'),
        dbc.Row(graph_country_c, justify='center'),
        dbc.Row(graph_country_cd , justify='center'),
        dbc.Row(graph_country_progress , justify='center'),
        
        ]

    jh_layout = html.Div(rows_jh_list)
    return jh_layout
#graphRow2 = dbc.Row([dbc.Col(country_table, md = 8)])

#RKI




def get_rki_layout():
    update_rki()
    sdiv = create_source_div('Robert Koch Institut,  Germany', 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html')
    graph_c, graph_cn, dd_s = get_germany_graphs()
    rows_rki_list = [
        sdiv,
        dbc.Row([dbc.Col(graph_c, md=12)], style={'padding':'3em'}),
        dbc.Row([dbc.Col(graph_cn, md=12)], style={'padding':'3em'}),
        dbc.Row([dbc.Col(dd_s, md=12)], style={'padding':'3em'}),
        dbc.Row(graph_rki_c, justify='center'),
        dbc.Row(graph_rki_cd , justify='center'),
        dbc.Row(graph_rki_progress , justify='center'),
    ]
    return html.Div(rows_rki_list)

### Italy

def get_italy_layout():
    sdiv = create_source_div('Dipartimento della Protezione Civile, Italy', 'https://github.com/pcm-dpc/COVID-19')
    graph_c, graph_cn = get_italy_graphs()
    rows_italy_list = [
        sdiv,
        dbc.Row([dbc.Col(graph_c)]),
        dbc.Row([dbc.Col(graph_cn)])
        ]
    italy_layout = html.Div(rows_italy_list)
    return italy_layout
######################
### MAIN LAYOUT #####
######################

def serve_layout():
    return html.Div([navbar, dbc.Container(id="page-content", className="pt-4")], className='container', style={'background':colors['background'], 'padding':'2em'})

app.layout = serve_layout


#################
#### CALBACKS###
################



@app.callback(
    [Output("gGermany_cd", "figure"),
    Output("gGermany_c", "figure"),
    Output("gGermany_p", "figure")
    ]
    ,
    [
        Input('states', "value")
    ],
)
def make_graph_rki(states):
    plot_data = rki.df.loc[pd.IndexSlice[states,   (rki.get_last_update() - timedelta(days=21)):],:].reset_index()
    #fig2 = px.bar(plot_data, x='date', y='confirmed')
    states_cd_fig = go.Figure(layout=plot_layout)
    for s in states:
        pdata = plot_data[plot_data['Bundesland']==s]
        states_cd_fig.add_trace(go.Bar(x=pdata.date, y=pdata.confirmed_diff, name=s ))
    states_cd_fig.update_layout(title_text="confirmed new")

    states_c_fig = go.Figure(layout=plot_layout)
    for s in states:
        pdata = plot_data[plot_data['Bundesland']==s]
        states_c_fig.add_trace(go.Bar(x=pdata.date, y=pdata.confirmed, name=s ))
    states_c_fig.update_layout(title_text="confirmed")
    
    
    plot_data.loc[:,'days'] = plot_data.groupby(['Bundesland', 'date']).filter(lambda x: x['confirmed']>100).groupby('Bundesland').cumcount() + 1
    #fig2 = px.bar(plot_data, x='date', y='confirmed')
    yrange = [100, plot_data.confirmed.max()]
    states_pg_fig = go.Figure(layout=plot_layout)
    for s in states:
        pdata = plot_data[plot_data['Bundesland']==s]
        states_pg_fig.add_trace(go.Scatter(x=pdata.days, y=pdata.confirmed, name=s ,mode='lines+markers'))
    states_pg_fig.update_layout(title_text="Days since 100 cases (log)", xaxis_title='days', yaxis_title='confirmed cases', yaxis_type="log",  yaxis = dict(
        tick0 = 100
        )
    )
    states_pg_fig.update_yaxes(range=[math.log10(x) for x in yrange])
    
    
   
    
    return states_cd_fig, states_c_fig, states_pg_fig





@app.callback(
    [Output("gCountry_cd", "figure"),
    Output("gCountry_c", "figure"),
    Output("gCountry_p", "figure")
    ]
    ,
    [
        Input('country', "value"),
        Input('type_input', 'value')
    ],
)
def make_graph_jh(country, ptype):
    jht = jh
    plot_data = jht.df[(jht.df['Country/Region'].isin(country)) & (jht.df.date > (jht.get_last_update() - timedelta(days=21)))]
    country_fig = go.Figure(layout=plot_layout)
    for c in country:
        pdata = plot_data[plot_data['Country/Region']==c]
        country_fig.add_trace(go.Bar(x=pdata.date, y=pdata[(ptype + '_diff')], name=c ))
    country_fig.update_layout(title_text="new confirmed cases by country", xaxis_title='date', yaxis_title='new confirmed cases')
    
   
    
    plot_data = jht.df[(jht.df['Country/Region'].isin(country)) & (jht.df.date > (jht.get_last_update() - timedelta(days=21)))]
    country_c_fig = go.Figure(layout=plot_layout)
    for c in country:
        pdata = plot_data[plot_data['Country/Region']==c]
        country_c_fig.add_trace(go.Bar(x=pdata.date, y=pdata[ptype], name=c ))
    country_c_fig.update_layout(title_text="confirmed cases by country", xaxis_title='date', yaxis_title='confirmed cases')
    
    
    
    name_type = "confirmed cases"
    if ptype == 'deaths':
        name_type = 'deaths'
    plot_data = jht.df[(jht.df['Country/Region'].isin(country))]
    n = 1000
    if (ptype == 'deaths'):
        n=100
        
    plot_data.loc[:,'days'] = plot_data.groupby(['Country/Region', 'date']).filter(lambda x: x[ptype]>n).groupby('Country/Region').cumcount() + 1
    #fig2 = px.bar(plot_data, x='date', y='confirmed')
    plot_data = plot_data.reset_index()
    yrange = [n, plot_data.confirmed.max()]
    country_pg_fig = go.Figure(layout=plot_layout)
    for c in country:
        pdata = plot_data[plot_data['Country/Region']==c]
        country_pg_fig.add_trace(go.Scatter(x=pdata.days, y=pdata[ptype], name=c ,mode='lines+markers'))
    country_pg_fig.update_layout(title_text="Cumulative number of {} since {} {}  (log)".format(name_type, n, name_type), xaxis_title='days', yaxis_title=ptype, yaxis_type="log",  yaxis = dict(
        tick0 = n
        )
    )
    country_pg_fig.update_yaxes(range=[math.log10(x) for x in yrange])
    
    
   
    
    return country_fig, country_c_fig, country_pg_fig

@app.callback(
    [Output("gItaly_cd", "figure"),
    Output("gItaly_c", "figure"),
    Output("gItaly_p", "figure")
    ]
    ,
    [
        Input('regions', "value")
    ],
)
def make_graph_italy(regions):
    Ital
    plot_data = jht.df[(jht.df['Country/Region'].isin(country)) & (jht.df.date > (jht.get_last_update() - timedelta(days=21)))]
    #fig2 = px.bar(plot_data, x='date', y='confirmed')
    country_fig = go.Figure(layout=plot_layout)
    for c in country:
        pdata = plot_data[plot_data['Country/Region']==c]
        country_fig.add_trace(go.Bar(x=pdata.date, y=pdata.confirmed_diff, name=c ))
    country_fig.update_layout(title_text="confirmed new")
    
   
    
    plot_data = jht.df[(jht.df['Country/Region'].isin(country)) & (jht.df.date > (jht.get_last_update() - timedelta(days=21)))]
    country_c_fig = go.Figure(layout=plot_layout)
    for c in country:
        pdata = plot_data[plot_data['Country/Region']==c]
        country_c_fig.add_trace(go.Bar(x=pdata.date, y=pdata.confirmed, name=c ))
    country_c_fig.update_layout(title_text="confirmed")
    
    
    
    plot_data = jht.df[(jht.df['Country/Region'].isin(country))]
    plot_data.loc[:,'days'] = plot_data.groupby(['Country/Region', 'date']).filter(lambda x: x['confirmed']>1000).groupby('Country/Region').cumcount() + 1
    #fig2 = px.bar(plot_data, x='date', y='confirmed')
    plot_data = plot_data.reset_index()
    yrange = [1000, plot_data.confirmed.max()]
    country_pg_fig = go.Figure(layout=plot_layout)
    for c in country:
        pdata = plot_data[plot_data['Country/Region']==c]
        country_pg_fig.add_trace(go.Scatter(x=pdata.days, y=pdata.confirmed, name=c ,mode='lines+markers'))
    country_pg_fig.update_layout(title_text="Days since 1000 cases (log)", xaxis_title='days', yaxis_title='confirmed cases', yaxis_type="log",  yaxis = dict(
        tick0 = 1000
        )
    )
    country_pg_fig.update_yaxes(range=[math.log10(x) for x in yrange])
    
    
   
    
    return country_fig, country_c_fig, country_pg_fig


   


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/johnshopkins"]:
        return get_jh_layout()
    elif pathname == "/rki":
        return get_rki_layout()
    elif pathname == "/italy":
        return get_italy_layout()
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )





if __name__=='__main__':
    #app.run_server(debug=True)
    app.run_server(debug=True)

