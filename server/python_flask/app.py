import sys

sys.path.append("../../code")
import os
dir_path = os.path.dirname(os.path.realpath(__file__))



import test_jonne as tj


import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.manifold import TSNE

from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS

from config import Config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

print("### PYTHON SERVER STARTING ###", dir_path)




Base = declarative_base()

class WFP(Base):
    __tablename__ = 'wfp_v5_retail'
    id = Column(Integer, primary_key=True)
    adm0_name = Column(String)
    cm_name = Column(String)
    mp_price = Column(Float)

class WDI_DATA(Base):
    __tablename__ = 'wdi_data'
    id = Column(Integer, primary_key=True)
    Country_Name = Column(String)
    Country_Code = Column(String)
    Indicator_Name = Column(String)
    Indicator_Code = Column(String)

    years = {}
    for i in range(1960, 2017):
        years[i] = Column(str(i), Integer)

class WHO(Base):
    __tablename__ = 'who'
    id = Column(Integer, primary_key=True)
    # Country = Column(Integer)
    Year = Column(Integer)
    Sex = Column(Integer)
    Cause = Column(String)
    Deaths1 = Column(Float)
    Deaths2 = Column(Float)
    Deaths3 = Column(Float)
    Deaths4 = Column(Float)
    Deaths5 = Column(Float)
    Deaths6 = Column(Float)
    Deaths7 = Column(Float)
    Deaths8 = Column(Float)
    Deaths9 = Column(Float)
    Deaths10 = Column(Float)
    Deaths11 = Column(Float)
    Deaths12 = Column(Float)
    Deaths13 = Column(Float)
    Deaths14 = Column(Float)
    Deaths15 = Column(Float)
    Deaths16 = Column(Float)
    Deaths17 = Column(Float)
    Deaths18 = Column(Float)
    Deaths19 = Column(Float)
    Deaths20 = Column(Float)
    Deaths21 = Column(Float)
    Deaths22 = Column(Float)
    Deaths23 = Column(Float)
    Deaths24 = Column(Float)
    Deaths25 = Column(Float)
    Deaths26 = Column(Float)

    Country = Column(Integer, ForeignKey('who_country_codes.country'))
    child = relationship("WHO_country_codes")

    @hybrid_method
    def total(self, fields):
        return sum(getattr(self, field) for field in fields)

    @total.expression
    def total(cls, fields):
        return sum(getattr(cls, field) for field in fields)

class WHO_country_codes(Base):
    __tablename__ = 'who_country_codes'
    id = Column(Integer, primary_key=True)
    country = Column(Integer)
    name = Column(String)

config = Config()

app = Flask(__name__)
CORS(app)
api = Api(app)



from geopy.geocoders import Nominatim
geolocator = Nominatim()


REGIONAL_FILE_NAME = '../../datasets/Regions/regions.csv'

df_v5 = pd.read_csv('../../datasets/data/WFPVAM_FoodPrices_version5_Retail.csv')
df_v4 = pd.read_csv('../../datasets/data/WFPVAM_FoodPrices_version4_Retail.csv')

df_v5['datetime'] = pd.to_datetime(df_v5.date, format='%Y-%m')
df_v4['datetime'] = pd.to_datetime(df_v4.date, format='%Y-%m')



def merge_regions(df):
    region_df = pd.read_csv(REGIONAL_FILE_NAME)
    region_df.rename(columns={'name': 'adm0_name'}, inplace=True)
    new_regions = region_df.loc[:, ['adm0_name', 'sub-region']]
    df_regions = pd.merge(df, new_regions, on='adm0_name', how='left')
    return df_regions.copy()

df_v5 = merge_regions(df_v5)
df_v4 = merge_regions(df_v4)

### REFUGEES ###
from model.refugees import Refugees
refugees = Refugees()

df_v5 = refugees.merge_refugees(df_v5)
df_v4 = refugees.merge_refugees(df_v4)


### MORTALITY ###

WHO_MORTALITY = "../../datasets/global_mortality_who.csv"

mortality = pd.read_csv(WHO_MORTALITY, skiprows=1)
mortality['Year'] = mortality['Year'].astype(int)

df_v5['Year'] = df_v5['datetime'].dt.year
df_v5['Year'] = df_v5['Year'].astype(int)
df_v5 = pd.merge(df_v5, mortality, left_on=['adm0_name', 'Year'], right_on=['Country', 'Year'])
df_v5.drop(columns=['Country', 'Year'], inplace=True)
df_v5 = df_v5.rename(columns={' Both sexes': 'mortality_sum', ' Male': 'mortality_male', ' Female': 'mortality_female'})

df_v4['Year'] = df_v4['datetime'].dt.year
df_v4['Year'] = df_v4['Year'].astype(int)
df_v4 = pd.merge(df_v4, mortality, left_on=['adm0_name', 'Year'], right_on=['Country', 'Year'])
df_v4.drop(columns=['Country', 'Year'], inplace=True)
df_v4 = df_v5.rename(columns={' Both sexes': 'mortality_sum', ' Male': 'mortality_male', ' Female': 'mortality_female'})


### RATES ###

old_v1 = pd.read_csv('../../datasets/data/WFPVAM_FoodPrices_version1.csv')
all_currencies = pd.read_csv('../../datasets/currencies/all_currencies.csv')
all_currencies.columns = ['cur_name', 'date', 'rate']

old_v1 = pd.merge(old_v1, all_currencies, on=['cur_name', 'date'], how='left')
old_v1['datetime'] = pd.to_datetime(old_v1['date'], format='%Y-%m')

df_v5 = pd.merge(df_v5, old_v1[['adm0_name', 'mkt_name', 'cm_name', 'datetime', 'rate']], on=['adm0_name', 'mkt_name', 'cm_name', 'datetime'], how='left')
df_v4 = pd.merge(df_v4, old_v1[['adm0_name', 'mkt_name', 'cm_name', 'datetime', 'rate']], on=['adm0_name', 'mkt_name', 'cm_name', 'datetime'], how='left')


### GDP ###

gdp = pd.read_csv('../../datasets/GDP/GDP_per_capita.csv')
gdp = gdp.melt(id_vars=['country'])
gdp.columns = [tj.COUNTRY, tj.YEAR, 'GDP']
gdp[tj.YEAR] = gdp[tj.YEAR].astype(int)


df_v5[tj.YEAR] = df_v5['datetime'].dt.year
df_v5[tj.YEAR] = df_v5[tj.YEAR].astype(int)
df_v5 = pd.merge(df_v5, gdp[['adm0_name', tj.YEAR, 'GDP']], on=['adm0_name', tj.YEAR], how='left')
df_v5.drop(columns=['mp_year'], inplace=True)
df_v5['GDP'] = df_v5['GDP'].astype(float)

df_v4[tj.YEAR] = df_v4['datetime'].dt.year
df_v4[tj.YEAR] = df_v4[tj.YEAR].astype(int)
df_v4 = pd.merge(df_v4, gdp[['adm0_name', tj.YEAR, 'GDP']], on=['adm0_name', tj.YEAR], how='left')
df_v4.drop(columns=['mp_year'], inplace=True)
df_v4['GDP'] = df_v4['GDP'].astype(float)


df_v4 = df_v4.rename(columns={'rate': 'Currency Rate', 'frequency': 'Refugees', 'mortality_sum': 'Mortality Rate'})
df_v5 = df_v5.rename(columns={'rate': 'Currency Rate', 'frequency': 'Refugees', 'mortality_sum': 'Mortality Rate'})

def get_dataset(df_num):
    global df_v5
    global df_v4
    if df_num == 0:
        return df_v4
    return df_v5

# print("### DATA LOADED ###")

def get_all_years(df):
    l = []
    years = set(df['datetime'].dt.year)
    for y in years:
        d = {}
        d['year'] = y
        l.append(d)
    return l

def get_all_products(df):
    # l = []
    products = set(df['cm_name'])
    # for p in products:
    #     d = {}
    #     d['product'] = p
    #     l.append(d)
    return list(products)

def get_all_countries(df, regions=[]):
    # l = []
    if regions:
        df = df.loc[df['sub-region'].isin(regions)]

    countries = set(df[tj.COUNTRY])
    # for c in countries:
    #     d = {}
    #     d['country'] = c
    #     l.append(d)
    return list(countries)

def get_all_regions(df):
    l = []
    regions = set(df['sub-region'])
    # for r in regions:
    #     d = {}
    #     d['region'] = r
    #     l.append(d)
    return list(regions)

def get_prod_avg(prod_name):
    d = []
    for country, avg in session.query(WFP.adm0_name, func.avg(WFP.mp_price)).\
        filter_by(cm_name=prod_name).group_by(WFP.adm0_name):
        location = geolocator.geocode(country)
        add_d = {}
        add_d['country'] = country
        add_d['average'] = avg
        add_d['lat'] = location.latitude
        add_d['lon'] = location.longitude
        d.append(add_d)
    return d

def get_mortality(df, regions, countries, years):
    selector = ''

    if countries:
        selector = tj.COUNTRY
        df = df.loc[df[selector].isin(countries)]
    elif regions:
        selector = 'sub-region'
        df = df.loc[df[selector].isin(regions)]

    if years:
        df = df[df['datetime'].dt.year.isin(years)]
        df = df.groupby([selector, 'datetime']).mean()[['Mortality Rate', 'mortality_male', 'mortality_female']].reset_index()
    else:
        df = df.groupby([df[selector], df['datetime'].dt.year]).mean()[['Mortality Rate', 'mortality_male', 'mortality_female']].reset_index()
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y')
    return df.to_json(orient='records')

def get_correlation(df, regions, countries, products, years, correlation, correlator):

    if not correlation:
        correlation = 'cm_name'
    if not correlator:
        correlator = 'mp_price'

    y_axis = correlator
    selector = ''

    if products:
        df = df.loc[df[tj.PROD].isin(products)]

    if countries:
        selector = tj.COUNTRY
        df = df.loc[df[selector].isin(countries)]
    elif regions:
        selector = 'sub-region'
        df = df.loc[df[selector].isin(regions)]

    if years:
        df = df[df['datetime'].dt.year.isin(years)]
        df = df.groupby([selector, 'cm_name', 'Mortality Rate', 'Refugees', 'Currency Rate', 'GDP', 'datetime'])[y_axis].mean().reset_index()
    else:
        df = df.groupby([df[selector], 'cm_name', 'Mortality Rate', 'Refugees', 'Currency Rate', 'GDP', df['datetime'].dt.year])[y_axis].mean().reset_index()
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y')



    prod = df.pivot_table('mp_price', ['adm0_name', 'datetime'], ['cm_name'])
    new = prod.reset_index()
    t = pd.merge(new, df[['adm0_name', 'datetime', 'Mortality Rate', 'Refugees', 'Currency Rate', 'GDP']], on=['adm0_name', 'datetime'])
    result = t.corr(method='pearson')
    return result.to_json()


def get_country_data(df, regions, countries, products, years, average=True):

    d = []

    js = {}
    year_d = {}

    selector = ''
    print(df['datetime'], years)

    if products:
        df = df.loc[df[tj.PROD].isin(products)]

    if countries:
        selector = tj.COUNTRY
        df = df.loc[df[selector].isin(countries)]
    elif regions:
        selector = 'sub-region'
        df = df.loc[df[selector].isin(regions)]

    years_set = set(df['datetime'].dt.year)
    year_d['years'] = [y for y in years_set]

    if years:
        df = df[df['datetime'].dt.year.isin(years)]
        df = df.groupby([selector, 'cm_name', 'datetime']).mean()[['mp_price', 'Gradient']].reset_index()
    else:
        df = df.groupby([df[selector], df['cm_name'], df['datetime'].dt.year]).mean()[['mp_price', 'Gradient']].reset_index()
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y')
    if average:
        js = json.loads(df.to_json(orient='records'))
        year_d['data'] = js
    # js.append(year_d)
    return year_d

def get_country_products(df, regions, countries):

    if regions:
        df = df.loc[df['sub-region'].isin(regions)]

    if countries:
        df = df.loc[df[tj.COUNTRY].isin(countries)]

    products = set(df[tj.PROD])
    return list(products)

def get_cluster_data(df, countries, products, years):

    if years:
        year_min = str(min(years))
        year_max = str(max(years))
    else:
        year_min = '1992'
        year_max = '2017'

    date_selection = tj.selecton_date(df, year_min + '-01', year_max + '-12')

    dic, data = tj.cluster(date_selection, NGroups = 4, category_dic = {tj.PROD: [], tj.COUNTRY: countries}, \
        mode = 2, Alg = 0, init_mode = 2, norm = True, PCA = True, dim = 20)

    l = []
    for key, value in dic.items():
        d = {}
        d['cluster_group'] = value
        d['label'] = key
        l.append(d)
    return l, dic

def get_tsne_data(df, countries, products, labels):

    dic = {tj.PROD: [], tj.COUNTRY: countries}

    df = tj.df_pivot(df, dic, value = tj.PRICE)
    col = list(df.columns)
    for k, v in labels.items():
        for i in v:
            col[col.index(i)] = k

    data = df.values
    data = data - np.nanmean(data, axis = 0)
    data[np.isnan(data)] = 0

    data = data.T

    X_embedded = TSNE(n_components=2, n_iter=270).fit_transform(data)

    l = {}
    l['data'] = pd.DataFrame(X_embedded).to_json(orient='values')
    l['labels'] = col
    # l = []
    # l = []
    # for key, value in dic.items():
    #     d = {}
    #     d['cluster_group'] = value
    #     l.append(d)
    return l


products = {}

class WHO_data(Resource):
    def get(self):
        args = parser.parse_args()
        countries = args['country']
        years = args['year']
        result = self.get_deaths(countries, years)
        return jsonify(result)

    def get_deaths(self, countries, years):
        d = []
        fields = ['Deaths' + str(i) for i in range(1, 26)]
        for year, country, sum in session.query(WHO.Year, WHO_country_codes, func.sum(WHO.total(fields))).\
            join(WHO.child).\
            group_by(WHO.Year, WHO_country_codes.id).\
            filter_by(name='Ukraine'):
            add_d = {}
            add_d['country'] = country.name
            add_d['year'] = int(year)
            # add_d['sex'] = int(sex)
            add_d['sum'] = float(sum)
            d.append(add_d)
        return d

class WDI_data(Resource):
    def get(self):
        args = parser.parse_args()
        countries = args['country']
        years = args['year']
        result = self.get_deaths(countries, years)
        return jsonify(result)

    def get_deaths(self, countries, years):
        d = []
        fields = ['Deaths' + str(i) for i in range(1, 26)]
        for country, indicator in session.query(WDI_DATA.Country_Name, WDI_DATA.Indicator_Name).\
            filter_by(Country_Name='Afghanistan').\
            filter(WDI_DATA.Indicator_Name.like('%Mortality%')).all():
        # for year, country, sum in session.query(WHO.Year, WHO_country_codes, func.sum(WHO.total(fields))).\
        #     join(WHO.child).\
        #     group_by(WHO.Year, WHO_country_codes.id).\
        #     filter_by(name='Ukraine'):
            add_d = {}
            add_d['country'] = country
            add_d['indicator'] = indicator
            d.append(add_d)
        return d


# SELECT SUM(Deaths1) + SUM(Deaths2) + SUM(Deaths3) + SUM(Deaths4) + SUM(Deaths5) + SUM(Deaths6) + SUM(Deaths7) + SUM(Deaths8) + SUM(Deaths9) + SUM(Deaths10) + SUM(Deaths11) + SUM(Deaths12) + SUM(Deaths13) + SUM(Deaths14) + SUM(Deaths15) + SUM(Deaths16) + SUM(Deaths17) + SUM(Deaths18) + SUM(Deaths19) + SUM(Deaths20) + SUM(Deaths21) + SUM(Deaths22) + SUM(Deaths23) + SUM(Deaths24) + SUM(Deaths25) + SUM(Deaths26), Year, who_country_codes.name FROM `who`
# JOIN who_country_codes ON who_country_codes.country = who.Country
# WHERE who.`Country` = 1400
# GROUP BY `Year`;
#
class Years(Resource):
    def get(self):
        args = parser.parse_args()
        dataset = args['dataset']
        years = get_all_years(get_dataset(dataset))
        return jsonify(years)

class Products(Resource):
    def get(self):
        args = parser.parse_args()
        dataset = args['dataset']
        products = get_all_products(get_dataset(dataset))
        return jsonify(products)

class AvgProducts(Resource):
    def get(self, product_id):
        avg = get_prod_avg(product_id)
        return jsonify(avg)

    def put(self, product_id):
        products[product_id] = request.form['data']
        return {product_id: products[product_id]}

class Regions(Resource):
    def get(self):
        args = parser.parse_args()
        dataset = args['dataset']
        regions = get_all_regions(get_dataset(dataset))
        return jsonify(regions)

class Countries(Resource):
    def get(self):
        args = parser.parse_args()
        dataset = args['dataset']
        regions = args['region']
        countries = get_all_countries(get_dataset(dataset), regions)
        return jsonify(countries)

class CountryData(Resource):
    def get(self):
        args = parser.parse_args()
        countries = args['country']
        dataset = args['dataset']
        regions = args['region']
        products = args['product']
        years = args['year']

        country_data = get_country_data(get_dataset(dataset), regions, countries, products, years)
        return jsonify(country_data)

class CountryProducts(Resource):
    def get(self):
        args = parser.parse_args()
        countries = args['country']
        dataset = args['dataset']
        regions = args['region']
        # years = args['year']
        country_data = get_country_products(get_dataset(dataset), regions, countries)
        return jsonify(country_data)

class Cluster(Resource):
    def get(self):
        args = parser.parse_args()
        countries = args['country']
        product = args['product']
        dataset = args['dataset']
        years = args['year']
        cluster_data, cluster_dic = get_cluster_data(get_dataset(dataset), countries, product, years)
        tsne_data = get_tsne_data(get_dataset(dataset), countries, product, cluster_dic)

        merged = {}
        merged['kmeans'] = cluster_data
        merged['tsne'] = tsne_data
        return jsonify(merged)


class RefugeesData(Resource):
    def get(self):
        args = parser.parse_args()
        countries = args['country']
        years = args['year']

        # only single country.
        total = refugees.get_total_refugees(countries[0], years)
        refugees_data = {}
        refugees_data['total'] = int(total)
        refugees_data['time'] = refugees.get_yearly_refugees(countries[0], years)
        return jsonify(refugees_data)


class RefugeesDestination(Resource):
    def get(self):
        args = parser.parse_args()
        countries = args['country']
        years = args['year']

        # only single country.
        total = refugees.get_refugee_destinations(countries, years)
        refugees_data = {}
        refugees_data['destinations'] = total
        return jsonify(refugees_data)

class Correlation(Resource):
    def get(self):
        args = parser.parse_args()
        dataset = args['dataset']
        regions = args['region']
        countries = args['country']
        products = args['product']
        years = args['year']
        correlation = args['correlation']
        correlator = args['correlator']
        correlation_data = get_correlation(get_dataset(dataset), regions, countries, products, years, correlation, correlator)
        return jsonify(correlation_data)

class Mortality(Resource):
    def get(self):
        args = parser.parse_args()
        dataset = args['dataset']
        regions = args['region']
        countries = args['country']
        years = args['year']
        mortality_data = get_mortality(get_dataset(dataset), regions, countries, years)
        return jsonify(mortality_data)

parser = reqparse.RequestParser()
parser.add_argument('region', type=str, action='append')
parser.add_argument('country', type=str, action='append')
parser.add_argument('product', type=str, action='append')
parser.add_argument('year', type=int, action='append')
parser.add_argument('average', type=bool)
parser.add_argument('dataset', type=int)
parser.add_argument('correlation', type=str)
parser.add_argument('correlator', type=str)

api.add_resource(AvgProducts, '/avg_prod/<string:product_id>')
api.add_resource(Years, '/years')
api.add_resource(Products, '/all_products')
api.add_resource(Countries, '/all_countries')
api.add_resource(Regions, '/all_regions')
api.add_resource(CountryData, '/country')
api.add_resource(CountryProducts, '/country_products')
api.add_resource(Cluster, '/cluster')
api.add_resource(WHO_data, '/who')
api.add_resource(WDI_data, '/wdi')


api.add_resource(RefugeesData, '/refugees')
api.add_resource(RefugeesDestination, '/refugees_destinations')
api.add_resource(Correlation, '/correlation')
api.add_resource(Mortality, '/mortality')


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
