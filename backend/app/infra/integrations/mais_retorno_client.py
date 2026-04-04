# app/infra/integrations/mais_retorno_client.py
from datetime import datetime

import pandas as pd

from app.infra.http import AsyncHttpClient


class MaisRetornoClient:
    def __init__(self):
        self.base_url = 'https://api.maisretorno.com/v3'
        self.http = AsyncHttpClient(
            base_url=self.base_url,
            timeout=30.0,
            max_retries=3,
            backoff_factor=1.0,
        )

    async def _get_slug_from_cnpj(self, cnpj: str) -> str:
        endpoint = f'/general/search/{cnpj}'
        response = await self.http.get(endpoint)
        slug = response[0]['slug']
        return slug

    async def get_fund_price_history_df(self, fund_legal_id: str, init_date: datetime) -> pd.DataFrame:
        slug = await self._get_slug_from_cnpj(fund_legal_id)

        start = int(init_date.timestamp() * 1000)
        end = int(datetime.now().timestamp() * 1000)

        endpoint = f'/funds/quotes/{slug}'
        params = {'start_date': start, 'end_date': end}
        response = await self.http.get(endpoint, params=params)

        data = response.get('quotes', [])
        if not data:
            raise ValueError('Nenhum dado de preço encontrado.')

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['d'], unit='ms').dt.normalize()
        df['close'] = df['c']
        df['currency'] = 'BRL'

        df = df.set_index('date').asfreq('D').reset_index()
        df[['close']] = df[['close']].ffill()

        return df[['date', 'close', 'currency']].sort_values('date').reset_index(drop=True)

    async def get_quotes(
        self,
        fund_legal_id: str,
        start_date: datetime = None,
        end_date: datetime = None,
    ):
        history_df = await self.get_fund_price_history_df(fund_legal_id, start_date)
        if start_date:
            history_df = history_df[history_df['date'] >= pd.to_datetime(start_date).normalize()]
        if end_date:
            history_df = history_df[history_df['date'] <= pd.to_datetime(end_date).normalize()]
        return {
            'currency': 'BRL',
            'quotes': history_df[['date', 'close']],
        }

    async def close(self):
        """Close the HTTP client."""
        await self.http.close() 