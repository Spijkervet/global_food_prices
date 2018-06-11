#/usr/bin/python3
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib.dates import drange
from datetime import datetime

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
SOURCE = 'mp_commoditysource'

CONV_PRICE = 0
CONV_CURR = 1
START_CURRENCY = {
    'AFN':'2003-1',
    'AMD':'2006-2',
    'CDF':'2009-1',
    'KGS':'2007-9',
    'MGA':'2005-2',
    'MMK':'2012-5',
    'SDG':'2007-2',
    'SPP':'2018-1',
    'TJS':'2008-7',
    'XOF':'1995-6',
    'ZMW':'2013-2'
    }

def unique_per_cat(df):
    """
    Dit geeft per colum in de dataset de unique values.
    """
    for col in set(df):
        print(col)
        try:
            print(np.sort(df.eval(col).unique()))
        except:
            print(df.eval(col).unique())
        print(len(df.eval(col).unique()))

def show_city(df, city_name):
    df2 = get_values_column(df, CITY, city_name)
    plt.rcParams['axes.prop_cycle'] = "cycler('ls', ['-','--','-.',':']) * cycler(u'color', ['r','g','b','c','k','y','m','934c00'])" #changes the colour of the graph lines
    for prod in df2.eval(PROD).unique():
        if prod == 'Oil (palm)':
            df_tmp = get_values_column(df2, PROD, prod).sort_values(by=[DATE])
            values = df_tmp[PRICE].tolist()
            try:
                values = [(value - min(values)) / (max(values) - min(values)) for value in values]
            except:
                values = [value/value for value in values]

            dates = [float(date.split("-")[0]) + (float(date.split("-")[1]) - 1) / 12 for date in df_tmp[DATE].tolist()]
            plt.plot(dates, values, label=prod)
            print(slice_columns(get_values_column(df2, PROD, prod).sort_values(by=[DATE]),[PROD, SELLER, PRICE, DATE]).values)



    plt.rcParams['legend.fontsize'] = 11
    plt.legend(fancybox=True,loc="best",framealpha=0.8)
    plt.show()

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

def consecutive_dates(serie, gap = 0):
    """
    Dit genereerd de lengte van de tijds intervallen van een pandas.serrie.
    Met gap kan je toelaten dat er eventueel x aantal maanden tussen de data punten zit.
    """
    consecutive_lst = []
    n = 1
    date = list(map(int, serie.iloc[0].split("-")))
    for x in serie.iloc[1:]:
        tmp = list(map(int, x.split("-")))
        if 0 <= (tmp[0] - date[0]) * 12 + tmp[1] - date[1] <= gap + 1:
            n += 1
        else:
            consecutive_lst.append(n)
            n = 1
        date = tmp
    consecutive_lst.append(n)
    return consecutive_lst

def save_to_csv(df, filename):
    """
    Save dataframe to csv.
    """
    df.to_csv(filename, sep=',', encoding='utf-8', index=False)

def join_YEAR_month(df):
    df['date'] = df.eval(YEAR).astype(str)+"-"+df.eval(MONTH).astype(str)

    df = df.drop([YEAR, MONTH], axis=1)
    return df

def remove_Curr(df):
    """
    verwijder currentie somaliland shilling
    """
    return df.loc[df[CURR] != 'Somaliland Shilling']

def change_duplicate_city(df):
    """
    Dit veranderd de naam van steden met de zelfde naam naar stad plus afkorting van het land.
    """
    a = [(city, L) for (L, city),_ in df.groupby([COUNTRY, CITY])]
    City, Land = zip(*a)
    for (c, L) in sorted(a):
        if City.count(c) > 1 and c != 'National Average':
            if L == 'United Republic of Tanzania':
                df.loc[(df[CITY] == c) & (df[COUNTRY] == L), CITY] = c + ' (URT)'
            elif L == 'El Salvador':
                df.loc[(df[CITY] == c) & (df[COUNTRY] == L), CITY] = c + ' (Sal)'
            else:
                df.loc[(df[CITY] == c) & (df[COUNTRY] == L), CITY] = c + ' (' + L[:3] + ')'
    return df

def remove_Region(df):
    """
    Dit verwijderd de kolom regio uit de dataframe.
    """
    return df.drop(REGION, axis=1)

def remove_less_then(df, m = 12, gap = 0):
    """
    Dit verwijderd alle data producten per markt/stad dat hebben minder dan m data punten.
    """
    return df.groupby([CITY, PROD]).filter(lambda x: len(x) > m and max(consecutive_dates(x.eval(DATE), gap = gap)) > m)

def is_earlier_date(date0, date1):
    """
    return true als date1 na date0 is.
    """
    date0 = list(map(int, date0.split("-")))
    date1 = list(map(int, date1.split("-")))
    return ((date0[0] - date1[0]) * 12 + date0[1] - date1[1]) <= 0

def check_date(curr, date):
    """
    Dit controleerd of de datum niet voor de start datum van de currency is.
    """
    if curr in START_CURRENCY:
        return is_earlier_date(START_CURRENCY[curr], date)
    else:
        return True

def remove_unvalid_curr_dates(df):
    """
    verwijder all data punten van currencies waar geen exchange rate van bekend is of niet bestaat.
    """
    return df.groupby([CURR, DATE]).filter(lambda x: check_date(x.eval(CURR).iloc[0], x.eval(DATE).iloc[0]))


def norm_price_curr(row, col):
    """
    verander de prijs in de row op basis van de currency, zodat de currency USD wordt.
    """
    UNIT_PRICE_CONVERTER[row.get(UNIT)][Col]

import time

def norm_curr(df):
    """
    normalize data prijzen door alles naar USD te zetten en verwijder CURR kolom.
    """
    curr_df = pd.read_csv('all_currencies.csv')
    # curr_dic_df = {}
    # for curr in curr_df['base_currency'].unique():
    #     curr_dic_df[curr] = get_values_column(curr_df, 'base_currency', curr)
    # print('done make dict from currency table')
    #
    # df[PRICE] = df.apply(lambda row: row.get(PRICE) * get_values_column(curr_dic_df[row[CURR]], 'datetime', row[DATE]).iloc[0]['rate'], axis = 1)
    
    t = time.clock()
    for curr in curr_df['base_currency'].unique():
        print(curr)
        a = get_values_column(curr_df, 'base_currency', curr)
        x = df.loc[df[CURR] == curr]
        x[PRICE] = x.apply(lambda row: row.get(PRICE) * get_values_column(a, 'datetime', row.get(DATE)).iloc[0].get('rate'), axis = 1)
    print(t - time.clock())
    return df.drop(CURR, axis=1)


if __name__ == "__main__":
    df = pd.read_csv('WFPVAM_FoodPrices_version1.csv')
    # print(df.shape)
    print(df)
    df = norm_curr(remove_unvalid_curr_dates(df))
    print(df)
    unique_per_cat(df)
    # print(df.size)







    # transform the dataframe of all_currencies to our standards
    # curr_df = pd.read_csv('all_currencies.txt')
    # curr_df = curr_df.drop('quote_currency', axis=1)
    # curr_df['base_currency'] = curr_df.apply(lambda row: 'NIS' if row.get('base_currency') == 'ILS' else row.get('base_currency'), axis=1)
    # curr_df['datetime'] = curr_df.apply(lambda row: '-'.join(list(map(str,map(int, row.get('datetime').split('-')[:2])))), axis = 1)
    # save_to_csv(curr_df, 'all_currencies.csv')


    # per currency het aantal jaren
    # [print(n+'\n', sorted(x[DATE].unique())[:4],'\n', sorted(x[DATE].unique())[-10:], '\n\n' ) for n,x in df.groupby([CURR])]




    # per product en stad kijken of het 1 seller is.
    # print({(df_group.eval(SELLER).unique()[0],df_group.eval(SELLER).unique()[1], group) for group, df_group in df.groupby([COUNTRY, CITY, PROD]) if len(df_group.eval(SELLER).unique()) > 1})




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
