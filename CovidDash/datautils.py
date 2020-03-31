import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup


class JHdata:
    
    def __init__(self):
         self.df = self.get_data()

    

    def get_last_update(self):
        return self.df.date.max()
    
    def get_countries(self):
        return self.df[self.df['date']==self.get_last_update()].sort_values(by='confirmed', ascending=False)['Country/Region'].values
    
    def get_current_world(self):
        return self.df.groupby('date').agg({'confirmed':'sum', 'deaths':'sum'}).reset_index()
    
    def get_data(self):
        df_confirmed_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
        df_deaths_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
        
        df_confirmed = df_confirmed_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt')\
            .assign(date=lambda x: pd.to_datetime(x.date))\
            .assign(type='confirmed')
        
        df_deaths = df_deaths_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt')\
            .assign(date=lambda x: pd.to_datetime(x.date))\
            .assign(type='deaths')
        
        df_covid19 = pd.concat([df_confirmed, df_deaths]).reset_index(drop=True)

    
    
        df_covid_19_pivot = df_covid19.pivot_table(index=['Country/Region', 'date'], columns='type', values='cnt', aggfunc='sum').reset_index()
        df_covid_19_pivot['confirmed_diff'] = df_covid_19_pivot.groupby('Country/Region').confirmed.diff()
        df_covid_19_pivot['deaths_diff'] = df_covid_19_pivot.groupby('Country/Region').deaths.diff()
       
        return df_covid_19_pivot
    def update_data(self):
        self.df = self.get_data()


class RKIdata():
    def __init__(self):
        self.df = self.get_rki_df()
    def get_rki_df(self):
        df_rki = pd.read_csv("http://www.nexolin.de/data/covid-19/rki/rki_data.csv", parse_dates=['date'])
        df_rki['days'] = df_rki.groupby(['Bundesland','date']).filter(lambda x: x['confirmed']>50).groupby('Bundesland').cumcount() + 1
        df_rki['confirmed_diff'] = df_rki.groupby('Bundesland').confirmed.diff()
        df_rki = df_rki.set_index(['Bundesland','date'])
        return df_rki
    def get_last_update(self):
        return self.df.reset_index().date.max()
    def get_states(self):
        return self.df.reset_index()['Bundesland'].unique()


class Italydata():
    def __init__(self):
        self.df = self.get_df()
    def get_df(self):
        df_italy = pd.read_csv('https://github.com/pcm-dpc/COVID-19/raw/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv')
        df_italy = df_italy.rename(columns={'data':'date', 'stato':'country', 'ricoverati_con_sintomi':'hospitalized', 'terapia_intensiva':'ICU',
                     'totale_ospedalizzati':'hospitalized_total',
                     'isolamento_domiciliare':'home_confinement',
                     'totale_attualmente_positivi':'confirmed_active',
                     'nuovi_positivi':'confirmed_new',
                     'dimessi_guariti':'recovered',
                     'deceduti':'deaths',
                     'totale_casi':'confirmed',
                     'tamponi':'tests'
                    })
        df_italy['date'] = pd.to_datetime(df_italy.date)
        df_italy = df_italy.set_index('date')

        return df_italy
    
    def get_last_update(self):
        return self.df.reset_index().date.max()
        

def fetch_all_data():
    df_italy = pd.read_csv('https://github.com/pcm-dpc/COVID-19/raw/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv')
    df_italy = df_italy.rename(columns={'data':'date', 'stato':'country', 'ricoverati_con_sintomi':'hospitalized', 'terapia_intensiva':'ICU',
                     'totale_ospedalizzati':'hospitalized_total',
                     'isolamento_domiciliare':'home_confinement',
                     'totale_attualmente_positivi':'confirmed_active',
                     'nuovi_positivi':'confirmed_new',
                     'dimessi_guariti':'recovered',
                     'deceduti':'deaths',
                     'totale_casi':'confirmed',
                     'tamponi':'tests'
                    })
    df_italy['date'] = pd.to_datetime(df_italy.date)
    df_italy = df_italy.set_index('date')
    df_italy.to_csv('./data/italy.csv')
    
    df_confirmed_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    df_deaths_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    
    df_confirmed = df_confirmed_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt')\
        .assign(date=lambda x: pd.to_datetime(x.date))\
        .assign(type='confirmed')
    
    df_deaths = df_deaths_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt')\
        .assign(date=lambda x: pd.to_datetime(x.date))\
        .assign(type='deaths')
    
    df_covid19 = pd.concat([df_confirmed, df_deaths]).reset_index(drop=True)

    
    
    df_covid_19_pivot = df_covid19.pivot_table(index=['Country/Region', 'date'], columns='type', values='cnt', aggfunc='sum').reset_index()
    df_covid_19_pivot['confirmed_diff'] = df_covid_19_pivot.groupby('Country/Region').confirmed.diff()
    df_covid_19_pivot['deaths_diff'] = df_covid_19_pivot.groupby('Country/Region').deaths.diff()
    print('jh')
    df_covid_19_pivot.to_csv('./data/jh.csv')
    

    