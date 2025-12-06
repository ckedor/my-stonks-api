import hashlib
import hmac
import json
import os
import time
from urllib.parse import urlencode

import pandas as pd
import requests

API_KEY = os.getenv('FOXBIT_API_KEY')
API_SECRET = os.getenv('FOXBIT_API_SECRET')
API_BASE_URL = 'https://api.foxbit.com.br/rest/v3'


class FoxbitClient:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.api_base_url = API_BASE_URL

    def sign(self, method, path, params, body):
        queryString = ''
        if params:
            queryString = urlencode(params)

        rawBody = ''
        if body:
            rawBody = json.dumps(body)

        timestamp = str(int(time.time() * 1000))
        preHash = f'{timestamp}{method.upper()}{"/rest/v3" + path}{queryString}{rawBody}'
        signature = hmac.new(self.api_secret.encode(), preHash.encode(), hashlib.sha256).hexdigest()

        return signature, timestamp

    def request(self, method, path, params=None, body=None):
        signature, timestamp = self.sign(method, path, params, body)
        url = f'{self.api_base_url}{path}'
        headers = {
            'X-FB-ACCESS-KEY': self.api_key,
            'X-FB-ACCESS-TIMESTAMP': timestamp,
            'X-FB-ACCESS-SIGNATURE': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.request(method, url, params=params, json=body, headers=headers)
            return response.json()
        except requests.HTTPError as http_err:
            print(
                f'HTTP Status Code: {http_err.response.status_code}, Error Response Body:',
                http_err.response.json(),
            )
            raise
        except Exception as err:
            print(f'An error occurred: {err}')
            raise

    def get_currencies(self):
        endpoint = '/currencies'

        return self.request('GET', endpoint)

    def get_candlesticks(
        self,
        market_symbol,
        interval='1d',
        start_time=None,
        end_time=None,
        limit=500,
    ):
        endpoint = f'/markets/{market_symbol}/candlesticks'
        params = {'interval': interval, 'limit': limit}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        candlesticks = self.request('GET', endpoint, params)

        close_data = []
        for candle in candlesticks:
            close_datetime = (
                pd.to_datetime(int(candle[5]), unit='ms', utc=True)
                .tz_convert('America/Sao_Paulo')
                .tz_localize(None)
                .replace(hour=0, minute=0, second=0, microsecond=0)
            )
            close_price = float(candle[4])
            close_data.append({'data': close_datetime, 'preco': close_price})

        df_history = pd.DataFrame(close_data)
        return df_history

    def get_user_info(self):
        endpoint = '/me'

        user_info = self.request('GET', endpoint)
        return user_info

    def get_trades(self, ticker):
        endpoint = '/trades'
        params = {'market_symbol': ticker, 'page_size': 100}
        trades = self.request('GET', endpoint, params)
        return trades
