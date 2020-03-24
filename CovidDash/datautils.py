import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup


class JHdata:
    
    def __init__(self):
        self.df = self.get_johnshopkins_df()

    def get_johnshopkins_df(self):
        df_confirmed_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv')
        df_deaths_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv')
        df_recovered_raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv')
        
        df_confirmed = df_confirmed_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt')\
            .assign(date=lambda x: pd.to_datetime(x.date))\
            .assign(type='confirmed')
        
        df_deaths = df_deaths_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt')\
            .assign(date=lambda x: pd.to_datetime(x.date))\
            .assign(type='deaths')
        
        df_recovered = df_recovered_raw.melt(id_vars=['Province/State', 'Country/Region','Lat','Long'], var_name='date', value_name='cnt') \
            .assign(date=lambda x : pd.to_datetime(x['date'])) \
            .assign(type="recovered")
        df_covid19 = pd.concat([df_confirmed, df_deaths, df_recovered]).reset_index(drop=True)
            
        # get country codes
        url_codes = "https://countrycode.org/"
        codes_html = requests.get(url_codes).text
        soup = BeautifulSoup(codes_html, 'html.parser')
        code_table = soup.find('table', {'data-sort-name':'countrycode'})
        df_cc = pd.read_html(str(code_table))[0]
        df_cc[['ISO2', 'ISO3']] = df_cc['ISO CODES'].str.split(' / ', expand=True)
        df_covid19['country_key'] =df_covid19['Country/Region']
        df_covid19['country_key'] = df_covid19['country_key'].replace({'Mainland China':'China', 'US':'United States', 'UK':'United Kingdom', 'North Macedonia':'Macedonia', 'Others':np.nan})
    
        # merge data
        df_covid19 = df_covid19.merge(df_cc, left_on='country_key', right_on='COUNTRY')
        
        
        df_covid_19_pivot = df_covid19.pivot_table(index=['Country/Region', 'ISO3', 'ISO2', 'date'], columns='type', values='cnt', aggfunc='sum').assign(sick=lambda x: x['confirmed'] - x['deaths'] - x['recovered']).reset_index()
        df_covid_19_pivot['confirmed_diff'] = df_covid_19_pivot.groupby('Country/Region').confirmed.diff()
        return df_covid_19_pivot
    def get_last_update(self):
        return self.df.date.max()
    
    def get_countries(self):
        return self.df[self.df['date']==self.get_last_update()].sort_values(by='confirmed', ascending=False)['Country/Region'].values
    
    def get_current_world(self):
        return self.df.groupby('date').agg({'confirmed':'sum', 'deaths':'sum', 'recovered':'sum', 'sick':'sum'}).reset_index()
