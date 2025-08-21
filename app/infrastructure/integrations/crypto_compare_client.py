from datetime import datetime

import pandas as pd
import requests

from app.config.settings import settings


class CryptoCompareClient:
    def __init__(self):
        self.api_key = settings.CRYPTO_COMPARE_API_KEY
        self.base_url = 'https://data-api.cryptocompare.com'
        self.headers = {'accept': 'application/json'}

    def get_crypto_price_history_df(
        self, symbol: str, market: str = 'cadli', init_date: datetime = None
    ) -> pd.DataFrame:
        instrument = symbol + '-USD'

        endpoint = '/index/cc/v1/historical/days'
        limit = 2000
        aggregate = 1
        all_data = []

        to_ts = int(datetime.now().timestamp())

        while True:
            params = {
                'market': market,
                'instrument': instrument,
                'limit': limit,
                'aggregate': aggregate,
                'fill': 'true',
                'apply_mapping': 'true',
                'response_format': 'JSON',
                'api_key': self.api_key,
                'to_ts': to_ts,
            }

            response = requests.get(self.base_url + endpoint, headers=self.headers, params=params)
            data = response.json()

            if 'Data' not in data or not data['Data']:
                break

            chunk = data['Data']

            if init_date:
                chunk = [
                    item
                    for item in chunk
                    if datetime.utcfromtimestamp(item['TIMESTAMP']) >= init_date
                ]

            if not chunk:
                break

            all_data.extend(chunk)

            to_ts = chunk[0]['TIMESTAMP'] - 1
            if init_date and datetime.utcfromtimestamp(to_ts) < init_date:
                break

        df = pd.DataFrame(all_data)

        df = df.rename(
            columns={
                'TIMESTAMP': 'date',
                'OPEN': 'open',
                'CLOSE': 'close',
                'HIGH': 'high',
                'LOW': 'low',
                'VOLUME': 'volume',
            }
        )

        df['date'] = pd.to_datetime(df['date'], unit='s')
        df['currency'] = 'USD'
        df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'currency']]
        df = df.sort_values('date').reset_index(drop=True)

        return df
