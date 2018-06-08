import json

from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine
from flask_restful import Resource, Api
from flask_cors import CORS

from utils import get_dataset
from config import Config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.sql import func

Base = declarative_base()

class WFP(Base):
    __tablename__ = 'wfp'
    id = Column(Integer, primary_key=True)
    adm0_name = Column(String)
    adm1_name = Column(String)
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


def get_prod_avg(prod_name):
    d = []
    for country, avg in session.query(WFP.adm0_name, func.avg(WFP.mp_price)).\
        filter_by(cm_name=prod_name).group_by(WFP.adm0_name):
        location = geolocator.geocode(country)
        d.extend((location.latitude, location.longitude, avg))
    return d


products = {}

class Products(Resource):
    def get(self, product_id):
        avg = get_prod_avg(product_id)
        return jsonify(avg)

    def put(self, product_id):
        products[product_id] = request.form['data']
        return {product_id: products[product_id]}

api.add_resource(Products, '/<string:product_id>')



@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
