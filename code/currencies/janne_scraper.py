import json
import pickle
import requests

cookies = {
    '__cfduid': 'd0cdde7b09741f489922f51b8489eb49b1528468423',
    'opc_id': 'F21D1DF0-6B28-11E8-9D13-FB6800000000',
    'tc': '1',
    'ecc-manage-sessionid': 'bd9365ad7751d2d7e9efdea9d431aa47',
    'oanda-login-redirect': 'true',
    'csrftoken': 'liIOsuyAWVHumoQgwVg7XNn8KLMYuFJ0Nri1yctN6MAp4WgsJexNALlL921JeH1H',
    'sessionid': 'ybzyyf8yy3fmk3pnvn50fd8haeh9ngq0',
}

headers = {
    'Host': 'www.oanda.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'nl,en-US;q=0.7,en;q=0.3',
    'Referer': 'https://www.oanda.com/fx-for-business/historical-rates',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
}


responses = []

with open('currencies.txt', 'r') as file:
    lines = file.readlines()
    for l in lines:
        currency = l.strip()
        params = (
            ('source', 'OANDA'),
            ('adjustment', '0'),
            ('base_currency', currency),
            ('start_date', '1984-1-1'),
            ('end_date', '2018-1-1'),
            ('period', 'monthly'),
            ('price', 'mid'),
            ('view', 'graph'),
            ('quote_currency_0', 'USD')
        )

        try:
            response = requests.get('https://www.oanda.com/fx-for-business/historical-rates/api/data/update/', headers=headers, params=params, cookies=cookies)
            responses.append(response.json())
            print("APPENDED ", currency)

        except Exception as e:
            print(e)
            pass

print("DONE SCRAPING")

with open('all_currencies.pkl', 'wb') as f:
    pickle.dump(responses, f)

print("DONE DUMPING")
