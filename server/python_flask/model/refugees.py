import pandas as pd

class Refugees():

    def __init__(self):
        self.df = pd.read_csv('model/refugees.csv')
        self.lonlat = pd.read_csv('../../datasets/Regions/lonlat.csv')

        self.df = pd.merge(self.df, self.lonlat, left_on='origin', right_on='name', how='left')
        self.df = pd.merge(self.df, self.lonlat, left_on='destination', right_on='name', how='left')

        self.df['datetime'] = pd.to_datetime(self.df.date, format='%Y-%m-%d')
        self.df.drop(columns=['Unnamed: 0'], inplace=True)

    def get_total_refugees(self, origin, years):
        if years is None:
            years = list(range(1900, 2018))
        df = self.df.loc[self.df['datetime'].dt.year.isin(years)]
        return df.loc[df['origin'] == origin]['frequency'].sum()


    def get_yearly_refugees(self, origin, years):
        df = self.df
        if years is None:
            years = list(range(1900, 2018))

        df = df.loc[df['datetime'].dt.year.isin(years)]
        df = df.loc[df['origin'] == origin].groupby(df['datetime']).sum().reset_index()
        return df[['datetime', 'frequency']].to_json(orient='values')


    def get_refugee_destinations(self, origin, years):
        df = self.df
        if years is None:
            years = list(range(1900, 2018))
        df = df.loc[df['datetime'].dt.year.isin(years)]

        df = df.loc[df['origin'].isin(origin)].groupby(['destination', 'latitude_x', 'longitude_x', 'latitude_y', 'longitude_y'])['frequency'].sum().reset_index()
        return df[['destination', 'frequency', 'latitude_x', 'longitude_x', 'latitude_y', 'longitude_y']].to_json(orient='values')


    def merge_refugees(self, other_df):
        refugees_sum = self.df.groupby(['origin', 'datetime']).sum().reset_index()
        return pd.merge(other_df, refugees_sum, left_on=['adm0_name', 'datetime'], right_on=['origin', 'datetime'], how='left')
