#/usr/bin/python3
import numpy as np
import pandas as pd
import pickle


import os
from download import download
from matplotlib import pyplot as plt

import test_jonne as jonne


COUNTRY = 'adm0_name'
REGION = 'adm1_name'
CITY = 'mkt_name'
PROD = 'cm_name'
CURR = 'cur_name'
SELLER = 'pt_name'
UNIT = 'um_name'
MONTH = 'mp_month'
YEAR = 'mp_year'
DATE = 'date'
PRICE = 'mp_price'



# #%matplotlib inline

# url_2 = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
# regional_file_name = "regions.csv"

# url = "http://vam.wfp.org/sites/data/WFPVAM_FoodPrices_05-12-2017.csv"
# file_name = 'WFPVAM_FoodPrices_05-12-2017.csv'

# def get_dataset(url, file_name):
#     if not os.path.isfile(file_name):
#         download(url, file_name)
    
#     return pd.read_csv(file_name, encoding='latin-1')

# df = get_dataset(url, file_name)

# region_df = get_dataset(url_2, regional_file_name)



# df = pd.read_csv('WFPVAM_FoodPrices_version1.csv')




def days_gap(date0, date1):
    """
    return het aantal dagen dat geen data beschikbaar is 
    """
    date0 = list(map(int, date0.split("-")))
    date1 = list(map(int, date1.split("-")))
    return (((date1[0] - date0[0]) * 12) + (date1[1] - date0[1])) - 1



def next_month(date):
    """
    return de volgende maand
    """
    date = list(map(int, date.split("-")))
    date[1] = date[1] + 1 
    if date[1] == 13:
        date[1] = 1
        date[0] += 1
    return "-".join(list(map(str, date)))



def gaps(df, gap = 2, limit_missing_data = 2):
    for product in df.cm_name.unique():
        cities = df.loc[df.cm_name == product,'mkt_name'].unique()
        for city in cities:
            dates_city = df.loc[(df.cm_name == product) & (df.mkt_name == city),'date']
            list_dates_city = dates_city.tolist()
            for dateN, date in enumerate(list_dates_city[:-1]):
                missing_gap = days_gap(date, (list_dates_city[dateN + 1]))
                if 0 < missing_gap - 1 <= gap:
                    complete_row = df.loc[(df.cm_name == product) & (df.mkt_name == city) & (df.date == date)].copy()
                    
                    price_date0 = df.loc[(df.cm_name == product) & (df.mkt_name == city) & (df.date == date),'mp_price']
                    price_date1 = df.loc[(df.cm_name == product) & (df.mkt_name == city) & (df.date == list_dates_city[dateN + 1]),'mp_price']
                    
                    price_difference = abs(price_date0.values[0] - price_date1.values[0])
                    
                    next_month2 = date
                    price_next_month = price_date0
                    for day in range(missing_gap):
                        gradient = price_difference / (missing_gap+1)
                        next_month2 = next_month(next_month2)
                        
                        price_next_month = price_next_month + gradient
                        
                        complete_row['mp_price'] = price_next_month
                        complete_row['date'] = next_month2
                                                
                        df = df.append(complete_row)
    return df
                


if __name__ == "__main__":
    df = pd.read_csv('WFPVAM_FoodPrices_version3_Retail.csv')


    print(gaps(df))