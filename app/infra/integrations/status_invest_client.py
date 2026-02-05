# app/infra/integrations/status_invest_client.py
import json
from enum import IntEnum

import pandas as pd

from app.infra.http import AsyncHttpClient


class Category(IntEnum):
    FII = 2


class StatusInvestClient:
    def __init__(self):
        self.base_url = 'https://statusinvest.com.br'
        self.http = AsyncHttpClient(
            base_url=self.base_url,
            headers={'User-Agent': 'Chrome/112.0.0.0'},
            timeout=30.0,
            max_retries=3,
            backoff_factor=1.0,
        )

    async def get(self, endpoint, params=None):
        return await self.http.get(endpoint, params=params)

    async def get_provents_df(self, ticker, max=True):
        endpoint = '/fii/companytickerprovents'
        params = {'ticker': ticker, 'chartProventsType': 2 if max else 3}
        response = await self.get(endpoint, params)
        provents = response['assetEarningsModels']
        provents_df = pd.DataFrame(provents)
        provents_df.rename(columns={'pd': 'date', 'v': 'value_per_share'}, inplace=True)
        provents_df['date'] = pd.to_datetime(provents_df['date'], format='%d/%m/%Y')
        provents_df['ticker'] = ticker
        return provents_df[['ticker', 'date', 'value_per_share']]

    async def get_fiis_df(self):
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
            data = await self.get(endpoint, params)
            if len(data["list"]) == 0:
                break
            all_data.extend(data["list"])
            page += 1

        fiis_df = pd.DataFrame(all_data)
        return fiis_df

    async def close(self):
        """Close the HTTP client."""
        await self.http.close()
