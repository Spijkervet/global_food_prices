#/usr/bin/python3
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib.dates import drange
import datetime

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

def calc_diff(df, n = 1):
    """
    geeft de diverentiaal terug van de dataset.
    """

    return np.diff(df[PRICE], n, axis = 0)

if __name__ == "__main__":
    df = pd.read_csv('WFPVAM_FoodPrices_compressed.csv')
    # unique_per_cat(df)
    df2 = remove_less_then(remove_Region(change_duplicate_city(remove_Curr(join_YEAR_month(df)))), gap = 2)
    unique_per_cat(df2)
    save_to_csv(df2, 'WFPVAM_FoodPrices_version1.csv')



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
