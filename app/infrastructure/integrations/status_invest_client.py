import json
from enum import IntEnum

import pandas as pd
import requests


class Category(IntEnum):
    FII = 2

class StatusInvestClient:
    def __init__(self):
        self.base_url = 'https://statusinvest.com.br'

    def get(self, endpoint, params=None):
        url = self.base_url + endpoint
        headers = {'User-Agent': 'Chrome/112.0.0.0'}
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_provents_df(self, ticker, max=True):
        endpoint = '/fii/companytickerprovents'
        params = {'ticker': ticker, 'chartProventsType': 2 if max else 3}
        response = self.get(endpoint, params)
        provents = response['assetEarningsModels']
        provents_df = pd.DataFrame(provents)
        provents_df.rename(columns={'pd': 'date', 'v': 'value_per_share'}, inplace=True)
        provents_df['date'] = pd.to_datetime(provents_df['date'], format='%d/%m/%Y')
        provents_df['ticker'] = ticker
        return provents_df[['ticker', 'date', 'value_per_share']]

    def get_fiis_df(self):
        endpoint = '/category/advancedsearchresultpaginated'
        search = {
            "Segment": "",
            "Gestao": "",
            "my_range": "0;20",
            "dy": {"Item1": None, "Item2": None},
            "p_vp": {"Item1": None, "Item2": None},
            "percentualcaixa": {"Item1": None, "Item2": None},
            "numerocotistas": {"Item1": None, "Item2": None},
            "dividend_cagr": {"Item1": None, "Item2": None},
            "cota_cagr": {"Item1": None, "Item2": None},
            "liquidezmediadiaria": {"Item1": None, "Item2": None},
            "patrimonio": {"Item1": None, "Item2": None},
            "valorpatrimonialcota": {"Item1": None, "Item2": None},
            "numerocotas": {"Item1": None, "Item2": None},
            "lastdividend": {"Item1": None, "Item2": None}
        }

        all_data = []
        page = 0
        take = 99
        category = Category.FII

        while True:
            params = {
                'search': json.dumps(search),
                'orderColumn': '',
                'isAsc': '',
                'page': page,
                'take': take,
                'CategoryType': category
            }
            data = self.get(endpoint, params)
            if len(data["list"]) == 0:
                break
            all_data.extend(data["list"])
            page += 1

        fiis_df = pd.DataFrame(all_data)
        return fiis_df
