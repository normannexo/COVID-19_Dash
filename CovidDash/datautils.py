import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup


class JHdata:
    
    def __init__(self):
        self.df = self.get_johnshopkins_df()

    def get_johnshopkins_df(self):
        df_confirmed_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
        df_deaths_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
        #df_recovered_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
        df_confirmed_raw.rename(columns={'3/21/202':'3/21/20'}, inplace=True)
        
        df_confirmed = df_confirmed_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt')\
            .assign(date=lambda x: pd.to_datetime(x.date))\
            .assign(type='confirmed')
        
        df_deaths = df_deaths_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt')\
            .assign(date=lambda x: pd.to_datetime(x.date))\
            .assign(type='deaths')
        
        df_covid19 = pd.concat([df_confirmed, df_deaths]).reset_index(drop=True)
        df_covid19
        # get country codes
        url_codes = "https://countrycode.org/"
        codes_html = requests.get(url_codes).text
        soup = BeautifulSoup(codes_html, 'html.parser')
        code_table = soup.find('table', {'data-sort-name':'countrycode'})
        df_cc = pd.read_html(str(code_table))[0]
        df_cc[['ISO2', 'ISO3']] = df_cc['ISO CODES'].str.split(' / ', expand=True)
        df_covid19['country_key'] =df_covid19['Country/Region']
        # fix deviant country spellings:
        dict_replace=({'Mainland China':'China', 
                       'US':'United States',
                        'UK':'United Kingdom',
                         'Korea, South':'South Korea',
                         'North Macedonia':'Macedonia', 
                         'Others':np.nan, 
                         'Taiwan*':'Taiwan',
                         'Cabo Verde':'Cape Verde',
                         r"Cote d'Ivoire":'Ivory Coast',
                         'Czechia':'Czech Republic',
                         
                       
                       })
        df_covid19['country_key'] = df_covid19['country_key'].replace(dict_replace)
    
        # merge data
        df_covid19 = df_covid19.merge(df_cc, left_on='country_key', right_on='COUNTRY', how='left')
        
        
        df_covid_19_pivot = df_covid19.pivot_table(index=['Country/Region', 'date'], columns='type', values='cnt', aggfunc='sum').reset_index()
        df_covid_19_pivot['confirmed_diff'] = df_covid_19_pivot.groupby('Country/Region').confirmed.diff()
        return df_covid_19_pivot
    def get_last_update(self):
        return self.df.date.max()
    
    def get_countries(self):
        return self.df[self.df['date']==self.get_last_update()].sort_values(by='confirmed', ascending=False)['Country/Region'].values
    
    def get_current_world(self):
        return self.df.groupby('date').agg({'confirmed':'sum', 'deaths':'sum'}).reset_index()


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


class Italydata():
    def __init__(self):
        self.df = self.get_df()
    def get_df(self):
        df_italy = pd.read_csv('https://github.com/pcm-dpc/COVID-19/raw/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv')
        df_italy = df_italy.rename(columns={'data':'date', 'stato':'country', 'ricoverati_con_sintomi':'hospitalized', 'terapia_intensiva':'ICU',
                         'totale_ospedalizzati':'hospitalized_total',
                         'isolamento_domiciliare':'home_confinement',
                         'totale_attualmente_positivi':'confirmed_active',
                         'nuovi_attualmente_positivi':'confirmed_new',
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
        
        
    