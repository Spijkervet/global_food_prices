#/usr/bin/python3
import numpy as np
import pandas as pd
import pickle

def unique_per_cat(df):
    for col in set(df):
        print(col)
        print(df.eval(col).unique())
        print(len(df.eval(col).unique()))

if __name__ == "__main__":
    df = pd.read_csv('WFPVAM_FoodPrices_05-12-2017.csv', encoding="latin-1")
    country_year = df.loc[:,['adm0_name','mp_year']]

    country_dict = {}
    for country in df.adm0_name.unique():
        country_dict[country] = country_year.loc[country_year['adm0_name'] == country]['mp_year'].unique()

    with open('country_year.pk', 'wb') as handle:
        pickle.dump(country_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
