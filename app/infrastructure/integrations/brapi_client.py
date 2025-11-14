import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from app.config.settings import settings

logger = logging.getLogger(__name__)


class BrapiClient:
    def __init__(self):
        self.api_token = settings.BRAPI_API_TOKEN
        self.base_url = 'https://brapi.dev/api'
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {self.api_token}'})

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f'{self.base_url}{endpoint}'
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ValueError(f'Error fetching data from BRAPI: {e}') from e

    def _get_quotes(
        self, tickers, range='1y', interval='1d', modules='summaryProfile'
    ) -> Dict[str, Any]:
        endpoint = f'/quote/{",".join(tickers)}'
        params = {'range': range, 'interval': interval, 'modules': modules, 'fundamental':True}
        return self._get(endpoint, params)

    def available_stocks(self, search: Optional[str] = None):
        endpoint = '/available'
        params = {'search': search}
        return self._get(endpoint, params)
    
    def list_stocks(self, search: Optional[str] = None):
        endpoint = '/quote/list'
        params = {'search': search}
        return self._get(endpoint, params)

    @staticmethod
    def _brapi_range_from_init_date(init_date: datetime | pd.Timestamp | None) -> str:
        if init_date is None:
            return 'max'

        today = pd.Timestamp.today().normalize()
        init_date = pd.Timestamp(init_date).normalize()
        delta_days = (today - init_date).days

        ranges = [
            ('1d', 1),
            ('5d', 5),
            ('1mo', 30),
            ('3mo', 90),
            ('6mo', 180),
            ('1y', 365),
            ('2y', 730),
            ('5y', 1825),
            ('10y', 3650),
            ('max', 36500),
        ]

        for range_name, max_days in ranges:
            if delta_days <= max_days:
                return range_name

        return 'max'

    def extend_values_to_today(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.sort_values('date').reset_index(drop=True)
        last_date = df['date'].max()
        today = pd.Timestamp.today().normalize()

        if last_date < today:
            full_range = pd.date_range(start=last_date, end=today, freq='D')
            extended_df = pd.DataFrame({'date': full_range})
            df = pd.merge(extended_df, df, on='date', how='left')
            df[['open', 'high', 'low', 'close', 'volume']] = df[
                ['open', 'high', 'low', 'close', 'volume']
            ].fillna(method='ffill')

        return df

    def get_price_history_df(self, ticker: str, init_date, interval: str = '1d') -> pd.DataFrame:
        range = self._brapi_range_from_init_date(init_date)
        asset_quotes = self._get_quotes([ticker], range, interval)

        try:
            asset = asset_quotes['results'][0]
            history = asset.get('historicalDataPrice', [])
            df = pd.DataFrame(history)
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df['currency'] = asset.get('currency')
            df['date'] = pd.to_datetime(df['date'], unit='s').dt.normalize()
            df = self.extend_values_to_today(df)
            
            return df

        except Exception as e:
            raise ValueError(
                f'Erro ao buscar dados do BRApi. Ticker: {ticker}. Erro: {str(e)}'
            ) from e
            
    def get_quotes(
        self, 
        ticker: str, 
        init_date, 
        end_date = None,
        interval: str = '1d'
    ) -> List[Dict[str, Any]]:
        
        df = self.get_price_history_df(ticker, init_date, interval)
        if interval == '1d':
            df = df.set_index('date').asfreq('D').reset_index()
            df = df.fillna(method='ffill').fillna(method='bfill')
        if end_date:
            end_date = pd.to_datetime(end_date).normalize()
            df = df[df['date'] <= end_date]
        if init_date:
            init_date = pd.to_datetime(init_date).normalize()
            df = df[df['date'] >= init_date]

        currency = df['currency'].iloc[0] if not df.empty else None
        quotes = df[['date', 'open', 'high', 'low', 'close', 'volume']].to_dict(orient='records')
        return {
            'ticker': ticker,
            'currency': currency,
            'quotes': quotes,
        }

    def get_dividends(
        self, tickers: Union[str, List[str]], range: str = '1y'
    ) -> List[Dict[str, Any]]:
        endpoint = f'/quote/{",".join(tickers)}'
        params = {'range': range, 'interval': '1d', 'dividends': 'true'}
        response = self._get(endpoint, params)
        dividends = []
        for result in response['results']:
            dividend_data = result['dividendsData']
            cash_dividends = dividend_data['cashDividends']
            if len(cash_dividends) <= 1:
                continue
            for cash_dividend in cash_dividends:
                date = datetime.strptime(
                    cash_dividend['paymentDate'], '%Y-%m-%dT%H:%M:%S.%fZ'
                ).date()
                dividends.append({
                    'symbol': result['symbol'],
                    'value_per_share': cash_dividend['rate'],
                    'date': date,
                    'currency': result['currency'],
                })
        return dividends
