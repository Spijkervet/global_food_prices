import json
import pickle
import datetime
import csv

lists = []
file_name = 'all_currencies.csv'

with open('all_currencies.pkl', 'rb') as f:
    lists = pickle.load(f)

with open(file_name, 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',')
    filewriter.writerow(['quote_currency', 'base_currency', 'datetime', 'rate'])
    for js in lists:
        base_currency = js['widget'][0]['baseCurrency']
        quote_currency = js['widget'][0]['quoteCurrency']
        data = js['widget'][0]['data']
        for d in data:
            unix_timestamp = d[0] / 1000
            rate = d[1]
            filewriter.writerow([quote_currency, base_currency, datetime.datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d'), rate])
