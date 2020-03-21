import pandas as pd
import numpy as np


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
        df_covid_19_pivot = df_covid19.pivot_table(index=['Country/Region', 'date'], columns='type', values='cnt', aggfunc='sum').assign(sick=lambda x: x['confirmed'] - x['deaths'] - x['recovered']).reset_index()
        return df_covid_19_pivot
    def get_last_update(self):
        return self.df.date.max()
    
    def get_countries(self):
        return self.df[self.df['date']==self.get_last_update()].nlargest(20, 'confirmed')['Country/Region'].values
    
    def get_current_world(self):
        return self.df.groupby('date').agg({'confirmed':'sum', 'deaths':'sum', 'recovered':'sum', 'sick':'sum'}).reset_index()
