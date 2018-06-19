#/usr/bin/python3
import numpy as np
import pandas as pd
import pickle
import time
import matplotlib.pyplot as plt
from matplotlib.dates import drange
from datetime import datetime
import cluster as clus
import copy

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

NON_FOOD = [
    'Wage (non-qualified labour)',
    'Wage (non-qualified labour, non-agricultural)',
    'Wage (non-qualified labour, non-agricultural)',
    'Wage (qualified labour)',
    'Exchange rate',
    'Exchange rate (unofficial)',
    'Transport (public)',
    ]

START_CURRENCY = {
    'AFN':'2003-1',
    'AMD':'2006-2',
    'CDF':'2009-1',
    'KGS':'2007-9',
    'MGA':'2005-2',
    'MMK':'2012-5',
    'SDG':'2007-2',
    'SSP':'2018-1',
    'TJS':'2008-7',
    'XOF':'1995-6',
    'ZMW':'2013-2'
    }

UNIT_PRICE_CONVERTER = {
    '1.5 KG': (1.5, 'KG'), '5 KG': (5.0, 'KG'), '1.8 KG': (1.8, 'KG'),
    '2 KG': (2.0, 'KG'), '12.5 KG': (12.5, 'KG'), '10 KG': (10.0, 'KG'),
    '60 KG': (60.0, 'KG'), '18 KG': (18.0, 'KG'), '25 KG': (25.0, 'KG'),
    '3 KG': (3.0, 'KG'), '3.5 KG': (3.5, 'KG'), '12 KG': (12.0, 'KG'),
    '500 G': (0.5, 'KG'), '125 G': (0.125, 'KG'), '90 KG': (90.0, 'KG'),
    'Pound': (0.45359237, 'KG'), '380 G': (0.380, 'KG'), '85 G': (0.085, 'KG'),
    '45 KG': (45.0, 'KG'), '100 KG': (100.0, 'KG'), '50 KG': (50.0, 'KG'),
    '91 KG': (91.0, 'KG'), '650 G': (0.650, 'KG'), '115 G': (0.115, 'KG'),
    '350 G': (0.350, 'KG'), '385 G': (0.385, 'KG'), '11.5 KG': (11.5, 'KG'),
    '400 G': (0.400, 'KG'), '150 G': (0.150, 'KG'), '160 G': (0.160, 'KG'),
    '200 G': (0.200, 'KG'), '185 G': (0.185, 'KG'), '750 G': (0.750, 'KG'),
    '168 G': (0.168, 'KG'), 'Libra': (0.329, 'KG'), 'MT': (1000.0, 'KG'),
    'Marmite': (2.445, 'KG'),
    'Gallon': (3.78541178, 'L'), '500 ML': (0.500, 'L'), '750 ML': (0.750, 'L'),
    '1.5 L': (1.5, 'L'), '3 L': (3.0, 'L'), 'Cubic Meter': (1000.0, 'L'),
    '5 L': (5.0, 'L'),
    '10 pcs': (10.0, 'Unit'), '30 pcs': (30.0, 'Unit'), 'Dozen': (12.0, "Unit"),
    'Loaf': (1, 'Unit')
    }

UNIT_PROD_PRICE_CONVERTER = {
    "Fuel (diesel)": ('KG', 'L', 0.851),
    "Milk (pasteurized)": ('KG', 'L', 1.04), "Milk": ('KG', 'L', 1.04),
    "Oil (olive)": ('KG', 'L', 0.913), "Oil (palm)": ('KG', 'L', 0.913),
    "Oil (sunflower)": ('KG', 'L', 0.921), "Oil (groundnut)": ('KG', 'L', 0.921),
    "Oil (soybean)": ('KG', 'L', 0.921), "Oil (vegetable)": ('KG', 'L', 0.921),
    "Eggs": ('KG', 'Unit', 16.66667)
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
    """
    verander de kolommen jaar en maand naar 1 kolom met jaar-maand
    """
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
    City, _ = zip(*a)
    for (c, L) in sorted(a):
        if City.count(c) > 1 and c != 'National Average':
            if L == 'United Republic of Tanzania':
                df.loc[(df[CITY] == c) & (df[COUNTRY] == L), CITY] = c + ' (URT)'
            elif L == 'El Salvador':
                df.loc[(df[CITY] == c) & (df[COUNTRY] == L), CITY] = c + ' (Sal)'
            else:
                df.loc[(df[CITY] == c) & (df[COUNTRY] == L), CITY] = c + ' (' + L[:3] + ')'
    return df

def norm_all_currencies():
    """
    transform the dataframe of all_currencies to our standards
    """
    curr_df = pd.read_csv('all_currencies.txt')
    curr_df = curr_df.drop('quote_currency', axis=1)
    curr_df['base_currency'] = curr_df.apply(lambda row: 'NIS' if row.get('base_currency') == 'ILS' else row.get('base_currency'), axis=1)
    curr_df['datetime'] = curr_df.apply(lambda row: '-'.join(list(map(str,map(int, row.get('datetime').split('-')[:2])))), axis = 1)
    save_to_csv(curr_df, 'all_currencies.csv')

def remove_Region(df):
    """
    Dit verwijderd de kolom regio uit de dataframe.
    """
    return df.drop(REGION, axis=1)

def without_non_food(df):
    """
    returns all "real", not service, products.
    """
    return df[~df.cm_name.isin(NON_FOOD)]

def remove_non_measures(df):
    """
    verwijder geen vaste maten uit de df.
    """
    return df[~df[UNIT].isin(['Cuartilla', 'Head', '100 Tubers'])]

def change_dubble_unit_names(df):
    """
    Dit veranderd alle producten die een unit en kg hebben in verschillende producten.
    """
    for prod, group_df in df.groupby([PROD]):
        if group_df[UNIT].nunique() > 1:
            df.loc[(df[PROD] == prod) & (df[UNIT] == 'Unit'), PROD] = prod + ' (Unit)'
    return df

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

def norm_curr(df):
    """
    normalize data prijzen door alles naar USD te zetten.
    Data waar geen currency rate van is wordt verwijderd.
    CURR kolom wordt ook verwijderd.
    source: https://www.oanda.com/fx-for-business/historical-rates
    """
    df = remove_unvalid_curr_dates(df)
    curr_df = pd.read_csv('all_currencies.csv')
    curr_df.columns = [CURR, DATE, 'rate']

    # Only join things from the main dataframe (WFPVAM_FoodPrices_version1.csv with a LEFT join)
    df = pd.DataFrame.merge(df, curr_df, on=[CURR, DATE], how='left')
    df[PRICE] = df[PRICE].multiply(df['rate'], axis = 'index')
    return df.drop(['rate', CURR], axis = 1)

def norm_unit(df):
    """
    normalize de data op basis van de units.
    Dit zorgt ervoor dat zoveel mogelijk producten dezelfde units hebben (KG en L).
    En dat alle producten maar 1 unit hebben.
    source conversion: http://www.webconversiononline.com/weightof.aspx
    source Marmite: https://www.enfants-soleil.org/spip.php?article122
    source Eggs: https://en.wikipedia.org/wiki/Chicken_egg_sizes
    meeste komen uit oude soviet landen en vanuit gaand dat het gemiddelde van alle
    Eggs het gemiddelde gewicht is, is dit 60gr.

    op basis van zelfde statitieken voor is het logisch dat een Unit 1 pcs/loaf is.

    min          avg     max         std
    0.063 		 0.135 	 8.125 		 0.11677 	 Eggs Unit
    0.012 		 0.112 	 0.253 		 0.04438 	 Eggs pcs

    (avg)    mp_price
    um_name
    KG       1.341224
    Loaf     0.438143
    Unit     0.520290

    (std)    mp_price
    um_name
    KG       0.750623
    Loaf     0.052283
    Unit     0.510107
    """

    df_unit = pd.DataFrame.from_dict(UNIT_PRICE_CONVERTER, orient = 'index')
    df_unit.columns = ['factor', 'unit_new']

    df = pd.DataFrame.merge(df, df_unit, left_on = UNIT, how = 'left', right_index = True)

    df.unit_new.fillna(df.eval(UNIT), inplace = True)


    df[PRICE] = df[PRICE].divide(df['factor'], axis='index', fill_value = 1)

    df.drop([UNIT,'factor'], axis=1, inplace = True)
    df.rename(columns = {'unit_new': UNIT}, inplace = True)

    for product, (unit_N, unit_O, conversion) in UNIT_PROD_PRICE_CONVERTER.items():
        # CREATES MASK
        df_product = df[PROD] == product
        df_unit_O = df[UNIT] == unit_O

        df.loc[df_product & df_unit_O, PRICE] = df[df_product & df_unit_O][PRICE].apply(lambda x: x * conversion)
        df.loc[df_product & df_unit_O, UNIT] = unit_N

    df = change_dubble_unit_names(df)
    return remove_non_measures(df)

def split_national_average(df):
    """
    returnt twee dataframes: 1 dataframe met alle rijen die national average bevatten
    en 1 dataframe alleen gaat over de steden en niet de national averages
    """
    return [df.loc[df[CITY] == 'National Average'], df.loc[df[CITY] != 'National Average']]

def split_sellers(df):
    """
    returns dataframes for all different types of sellers with the seller names.
    """
    return [(seller, df.loc[df['pt_name'] == seller].drop([SELLER], axis = 1)) for seller in df.eval(SELLER).unique()]

def norm_GDP(df):
    """
    normaliseer de dataframe op basis van GDP.
    Alle data waar geen GDP voor is wordt verwijderd.
    source: http://www.imf.org/external/datamapper/PPPPC@WEO/OEMDC/ADVEC/WEOWORLD
    """

    GDP_df = pd.read_csv('GDP_per_capita.csv')
    GDP_df = GDP_df.melt(id_vars=['country'])
    GDP_df.columns = [COUNTRY, YEAR, 'GDP']

    df_date = df[DATE].str.split('-', expand = True).rename(columns = {0: YEAR, 1: MONTH})

    df = pd.DataFrame.merge(df, df_date, how='left', left_index=True, right_index=True)
    df = pd.DataFrame.merge(df, GDP_df, on=[COUNTRY, YEAR], how='left')

    df['GDP'] = df['GDP'].astype(float)
    df[PRICE] = df['GDP'].divide(df[PRICE], axis = 'index')
    df.dropna(inplace = True)
    return df.drop([YEAR, MONTH, 'GDP'], axis = 1)

def make_diff(df):
    """
    geeft de diff van de dataset per product en stad.
    Het eerste datapunt van de group is verwijderd omdat hier geen diff van is.
    """
    df['Diff'] = df.groupby([CITY, PROD])[PRICE].transform(pd.Series.diff)
    df.dropna(inplace = True)
    return df

def previous_month(date):
    """
    return de vorige maand
    """
    date = list(map(int, date.split("-")))
    date[1] = date[1] - 1
    if date[1] == 0:
        date[1] = 12
        date[0] -= 1
    return "-".join(list(map(str, date)))

def norm_gap(df, gap = 2, min_length = 6):
    """
    Normalize gaps in de dataset en verwijder losse punten plus adds de diff van de prijzen.
    """
    t = time.clock()
    print(time.clock() - t)
    # add year and month.
    df_date = df[DATE].str.split('-', expand = True).rename(columns = {0: YEAR, 1: MONTH})
    df_date = df_date.astype(int)
    df = pd.DataFrame.merge(df, df_date, how='left', left_index=True, right_index=True)
    df['Year'] = df[YEAR]
    df['Month'] = df[MONTH]
    df = df.sort_values(by=[COUNTRY, CITY, PROD, 'Year', 'Month']).reset_index(drop=True)

    # calc gap
    df[YEAR] = df.groupby([CITY, PROD])[YEAR].transform(pd.Series.diff)
    df[MONTH] = df[MONTH].diff()
    df[YEAR] = df[YEAR] * 12
    df['GAP'] = df[YEAR].add(df[MONTH]) - 1

    # price diff
    df['Price_diff'] = df[PRICE].diff()
    df['Gradient'] = df['Price_diff'].divide(df['GAP'] + 1)

    print('preprocessing done')
    print(time.clock() - t)
    # verwijder losse lijn stukken
    n = 0
    df2 = df.copy()
    for index, row in df.iterrows():
        n += 1
        if row['GAP'] > gap or np.isnan(row['GAP']):
            if n < min_length:
                drop_index = [m for m in range(index - 1, index - n - 1, -1)]
                df.drop(df2.index[drop_index], inplace = True)
            n = 0

    print('removing data done')
    print(time.clock() - t)

    #voeg onbrekende punten toe aan de dataset
    df2 = df[:0]
    for index, row in df[(df['GAP'] != 0) & (df['GAP'].notnull()) & (df['GAP'] <= gap)].iterrows():
        month = row[DATE]
        price = row[PRICE]
        for _ in range(int(row['GAP'])):
            month = previous_month(month)
            row[DATE] = month
            row['Year'], row['Month'] = list(map(int, month.split('-')))
            price -= row['Gradient']
            row[PRICE] = price
            df2 = df2.append(row)

    df.dropna(inplace = True)
    df = pd.concat([df, df2])
    df = df.sort_values(by=[COUNTRY, CITY, PROD, 'Year', 'Month']).reset_index(drop=True)
    print(time.clock() - t)
    return df.drop([YEAR, MONTH, 'GAP', 'Price_diff', 'Year', 'Month'], axis = 1)


def df_to_np_date_price(df, selectDic = {PROD : ['Millet']}, value = PRICE):
    """
    Dit maakt van een df een numpy array waar de rows datums zijn,
    de columns de geselecteerd column combinaties en
    de values zijn de value (PRICE/Gradient)

    De functie returned de row names, column names en een numpy array met de values.
    """
    condition = (df[PROD] != 'tmp')
    df['Info'] = ""
    for col, selection in selectDic.items():
        if selection:
            condition &= (df[col].isin(selection))
        df['Info'] +=  df[col] + ' - '

    df = df.loc[condition]
    make_sortable_date(df)
    df = df.pivot_table(index = DATE, columns = 'Info', values = value, aggfunc = np.mean)
    return df.index.values, list(df), df.values.T

def make_sortable_date(df):
    """
    Deze functie zorgt ervoor dat de dataframe gesoteerd kan worden op date.
    """
    pd.set_option('mode.chained_assignment', None)
    df.loc[:, DATE] = [x if len(x) == 7 else x[:5] + '0' + x[5:] for x in df[DATE].values]
    pd.set_option('mode.chained_assignment', 'warn')
    return df

def cluster(df, NGroups = 2, category_dic = {PROD: [], COUNTRY: ['Ethiopia']}, mode = 0, Alg = 0, init_mode = 0, norm = False, PCA = False, dim = 10):
    """
    cluster de dataframe aan de hand van de category_dic en mode.

    category_dic is waar je op categoriseerd. Een lege lijst betekend alles.
    mode:
        - 0 pakt de PRICE als value
        - 1 pakt de Gradient als value
        - 2 pakt de PRICE en Gradient als value
    Alg:
        - 0 pakt de distance als clustering method
        - 1 pakt de cosine als clustering method
    init_mode:
        - 0 zorgt ervoor dat de category cluster toegewezen krijgen door de range(NGroups) te herhalen en daarna opvullen met 0. bijv 0 1 2 0 1 2 0 0
        - 1 zorgt ervoor dat de category cluster toegewezen krijgen door de eerste n categorieen cluster 0 te geven dan 1 etc. bijv. 0 0 0 1 1 1 2 2
        - 2 zorgt ervoor dat de category random cluster toegewezen krijgen.
    norm:
        - False is niet genormaliseerde data
        - True is genormaliseerde data
    PCA:
        - False pas PCA niet toe
        - True pas PCA wel toe. (plotten kan dan niet meer, tenzij je niet dim gebruikt)
    """
    value = PRICE
    if mode == 1:
        value = 'Gradient'

    # creeer de dataset voor k-means
    dates, categories, data = df_to_np_date_price(df, category_dic, value = value)
    print(categories) #print de catogorien die worden geclusterd
    print(len(categories))

    if norm:
        data = (data - np.nanmin(data, axis = 1)[:, None]) / (np.nanmax(data, axis = 1) - np.nanmin(data, axis = 1))[:, None]

    if mode == 2:
        _, _, data2 = df_to_np_date_price(df, category_dic, value = 'Gradient')
        tmp_data = data

        if norm:
            data2 = (data2 - np.nanmin(data2, axis = 1)[:, None]) / (np.nanmax(data2, axis = 1) - np.nanmin(data2, axis = 1))[:, None]

        data = np.concatenate((data, data2), axis = 1)

    # clustering, als het verschil tussen de het nieuwe en oude gemiddelde convergeert is is het clusteren klaar.
    i = 0
    if PCA and norm:
        data = clus.PCA(data, dim)
    datagroup = clus.clustering(data, NGroups, init_mode)
    while np.max(np.sqrt(np.nansum((datagroup.GroupAvg - datagroup.NewGroupAvg)**2, axis = 1))) > 0.01 and i < 100:
        print(datagroup.data[:,-1]) #print de tussen stappen van k-means
        if Alg == 0:
            datagroup.Clustering()
        elif Alg == 1:
            datagroup.Clustering2()
        i += 1

    # maak de data weer met alleen PRICE
    if mode == 2:
        data = tmp_data

    # maak een dictionary met de cluster groepen.
    dic = {}
    for cat, group in zip(categories, datagroup.data[:,-1]):
        if group in dic:
            dic[group].append(cat)
        else:
            dic[group] = [cat]

    # print de dictionary
    for group, catLst in dic.items():
        print(group, len(catLst))
        print(catLst)

    # plot de geselecteerde data
    plt.rcParams['axes.prop_cycle'] = "cycler('ls', ['-','--','-.',':']) * cycler(u'color', ['r','g','b','c','k','y','m','934c00'])" #changes the colour of the graph lines
    for i, row in enumerate(data):
        # if i == 0:
        #     continue
        # if i > 3:
        #     break
        D = [float(date.split("-")[0]) + (float(date.split("-")[1]) - 1) / 12 for date in dates]
        plt.plot(D, row, label=categories[i])

    # plot de cluster gemiddelde
    # for i in range(NGroups):
    #     D = [float(date.split("-")[0]) + (float(date.split("-")[1]) - 1) / 12 for date in dates]
    #     if mode == 2:
    #         plt.plot(D, datagroup.NewGroupAvg[i, :data.shape[1]], label=i)
    #     else:
    #         plt.plot(D, datagroup.NewGroupAvg[i, :], label=i)

    # plot
    plt.rcParams['legend.fontsize'] = 11
    plt.legend(fancybox=True,loc="best",framealpha=0.8)
    plt.show(True)
    return dic, data

def selecton_date(df, low, high):
    """
    select rows based on dates between low and high.
    low and high must be 7 char long. bijv. 2012-01 and not 2012-1.
    """
    df = make_sortable_date(df)
    return df.loc[(df[DATE] >= low) & (df[DATE] <= high)]

if __name__ == "__main__":
    df = pd.read_csv('WFPVAM_FoodPrices_version4_Retail.csv')
    # df = without_non_food(df)
    # print(df[PROD].unique())
    cluster(df, NGroups = 3, category_dic = {PROD: [], COUNTRY: ['Ethiopia']}, mode = 2, Alg = 0, init_mode = 2, norm = False, PCA = False, dim = 20)







    # maak de version2 dataframes
    # df = pd.read_csv('WFPVAM_FoodPrices_version1.csv')
    # for tmp_df1 in split_national_average(norm_unit(norm_curr(without_non_food(df)))):
    #     for (seller, tmp_df2) in split_sellers(tmp_df1):
    #         if tmp_df2[CITY].iloc[0] == 'National Average':
    #             save_to_csv(tmp_df2, 'WFPVAM_FoodPrices_version2_Nat_' + seller + '.csv')
    #         else:
    #             save_to_csv(tmp_df2, 'WFPVAM_FoodPrices_version2_' + seller + '.csv')




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
