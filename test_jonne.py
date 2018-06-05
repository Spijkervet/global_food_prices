#/usr/bin/python3
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt


COUNTRY = 'adm0_name'
REGION = 'adm1_name'
CITY = 'mkt_name'
PROD = 'cm_name'
CURR = 'cur_name'
SELLER = 'pt_name'
UNIT = 'um_name'
MONTH = 'mp_month'
YEAR = 'mp_year'
DATE = 'datetime'
PRICE = 'mp_price'
SOURCE = 'mp_commoditysource'


def unique_per_cat(df):
    """
    Dit geeft per colum in de dataset de unique values.
    """
    for col in set(df):
        print(col)
        print(df.eval(col).unique())
        print(len(df.eval(col).unique()))

def slice_columns(df, column_names):
    """
    df = dataset
    colum_names = lijst met kolommen

    return nieuwe dataset met de gegeven kolommen.
    """
    return df.loc[:,column_names]

def get_values_column(df, column_name, value):
    """
    df = dataset
    column_name = kolom waarin je wil zoeken
    value = waarde die je uit de kolom wil.

    return nieuwe dataset met alle rijen die alleen de value in de gegeven kolommen bevatten.
    """
    return df.loc[df[column_name] == value]

def save_to_csv(df, filename):
    """
    Save dataframe to csv.
    """
    df.to_csv(filename, sep=',', encoding='utf-8', index=False)

def join_YEAR_month(df):
    df['datetime'] = pd.to_datetime(df.eval(YEAR)*10000+df.eval(MONTH)*100+1, format='%Y%m%d')
    df = df.drop([YEAR, MONTH], axis=1)
    return df

if __name__ == "__main__":
    df = pd.read_csv('WFPVAM_FoodPrices_c_CURR_DATE.csv')
    print(df)
    # save_to_csv(join_YEAR_month(df), 'WFPVAM_FoodPrices_c_CURR_DATE.csv')


    df2 = get_values_column(df, CITY, 'Fayzabad')
    prod_city_dic = {}
    for prod in df2.eval(PROD).unique():
        df_tmp = get_values_column(df2, PROD, prod).sort_values(by=[YEAR, MONTH])
        df_tmp = slice_columns(df_tmp, [])
        print(df_tmp)
        # prod_city_dic[prod] =
    #
    #
    # plt.plot(value, time)
    # plt.show()










    # check currency per country
    # country_curr = slice_columns(df, [COUNTRY, CURR, YEAR])
    # for country in df.eval(COUNTRY).unique():
    #     print(country, get_values_column(country_curr, COUNTRY, country)[CURR].unique())








    # welke jaren per land
    # country_year = slice_columns(df, [COUNTRY, YEAR])
    # country_dict = {}
    # for country in df.eval(COUNTRY).unique():
    #     country_dict[country] = get_values_column(country_year, COUNTRY, country)[YEAR].unique()





    # with open('country_year.pk', 'wb') as handle:
    #     pickle.dump(country_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
