from datetime import datetime

import pandas as pd
import requests


class MaisRetornoClient:
    def __init__(self):
        self.base_url = 'https://api.maisretorno.com/v3'

    def _get_slug_from_cnpj(self, cnpj: str) -> str:
        url = f'{self.base_url}/general/search/{cnpj}'
        response = requests.get(url)
        response.raise_for_status()

        slug = response.json()[0]['slug']
        return slug

    def get_fund_price_history_df(self, fund_legal_id: str, init_date: datetime) -> pd.DataFrame:
        slug = self._get_slug_from_cnpj(fund_legal_id)

        start = int(init_date.timestamp() * 1000)
        end = int(datetime.now().timestamp() * 1000)

        url = f'{self.base_url}/funds/quotes/{slug}'
        params = {'start_date': start, 'end_date': end}
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json().get('quotes', [])
        if not data:
            raise ValueError('Nenhum dado de preço encontrado.')

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['d'], unit='ms').dt.normalize()
        df['close'] = df['c']
        df['currency'] = 'BRL'
        
        df = df.set_index('date').asfreq('D').reset_index()
        df[['close']] = df[['close']].fillna(method='ffill')
        
        return df[['date', 'close', 'currency']].sort_values('date').reset_index(drop=True)
    
    def get_quotes(
        self,
        fund_legal_id: str, 
        start_date: datetime = None, 
        end_date: datetime = None,
    ):
        history_df = self.get_fund_price_history_df(fund_legal_id, start_date)
        if start_date:
            history_df = history_df[history_df['date'] >= pd.to_datetime(start_date).normalize()]
        if end_date:
            history_df = history_df[history_df['date'] <= pd.to_datetime(end_date).normalize()]
        return {
            'currency': 'BRL',
            'quotes': history_df[['date', 'close']], 
        } 