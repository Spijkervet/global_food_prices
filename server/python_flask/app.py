import json
import pandas as pd

from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS

from utils import get_dataset
from config import Config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.sql import func


print("### PYTHON SERVER STARTING ###")

Base = declarative_base()

class WFP(Base):
    __tablename__ = 'wfp_v5_retail'
    id = Column(Integer, primary_key=True)
    Iadm0_name = Column(String)
    cm_name = Column(String)
    mp_price = Column(Float)

config = Config()

app = Flask(__name__)
CORS(app)
api = Api(app)

engine = create_engine('mysql://root:root@mysql:3306/uva', echo=True)


from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

from geopy.geocoders import Nominatim
geolocator = Nominatim()

df = pd.read_sql('SELECT * FROM wfp_v5_retail', engine)
df['datetime'] = pd.to_datetime(df.date, format='%Y-%m')

# print("### DATA LOADED ###")

def get_all_years():
    l = []
    years = set(df['datetime'].dt.year)
    for y in years:
        d = {}
        d['year'] = y
        l.append(d)
    return l

def get_all_products():
    l = []
    products = set(df['cm_name'])
    for p in products:
        d = {}
        d['product'] = p
        l.append(d)
    return l

def get_all_countries():
    l = []
    countries = set(df['Iadm0_name'])
    for c in countries:
        d = {}
        d['country'] = c
        l.append(d)
    return l

def get_prod_avg(prod_name):
    d = []
    for country, avg in session.query(WFP.Iadm0_name, func.avg(WFP.mp_price)).\
        filter_by(cm_name=prod_name).group_by(WFP.Iadm0_name):
        location = geolocator.geocode(country)
        add_d = {}
        add_d['country'] = country
        add_d['average'] = avg
        add_d['lat'] = location.latitude
        add_d['lon'] = location.longitude
        d.append(add_d)
    return d

def get_country_data(countries, years, average=True):
    d = []

    js = {}
    year_d = {}
    send_df = df.loc[df['Iadm0_name'].isin(countries)]
    years_set = set(send_df['datetime'].dt.year)
    year_d['years'] = [y for y in years_set]

    if years:
        send_df = send_df[send_df['datetime'].dt.year.isin(years)]
        if average:
            send_df = send_df.groupby(['Iadm0_name', 'cm_name', 'datetime']).mean()['mp_price'].reset_index()
            js = json.loads(send_df.to_json(orient='records'))
            year_d['data'] = js
    # js.append(year_d)
    return year_d

products = {}

class Years(Resource):
    def get(self):
        years = get_all_years()
        return jsonify(years)

class Products(Resource):
    def get(self):
        products = get_all_products()
        print(products)
        return jsonify(products)

class AvgProducts(Resource):
    def get(self, product_id):
        avg = get_prod_avg(product_id)
        return jsonify(avg)

    def put(self, product_id):
        products[product_id] = request.form['data']
        return {product_id: products[product_id]}

class Countries(Resource):
    def get(self):
        countries = get_all_countries()
        return jsonify(countries)

class CountryData(Resource):
    def get(self):
        args = parser.parse_args()
        countries = args['country']
        years = args['year']

        country_data = get_country_data(countries, years)
        # countries = get_all_countries()
        return jsonify(country_data)

parser = reqparse.RequestParser()
parser.add_argument('country', type=str, action='append')
parser.add_argument('year', type=int, action='append')
parser.add_argument('average', type=bool)

api.add_resource(AvgProducts, '/avg_prod/<string:product_id>')
api.add_resource(Years, '/years')
api.add_resource(Products, '/all_products')
api.add_resource(Countries, '/all_countries')
api.add_resource(CountryData, '/country')


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
