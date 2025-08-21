import pandas as pd
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries

from app.config.settings import settings


class AlphaVantageClient:
    def __init__(self):
        self.alpha_vantage_key = settings.ALPHAVANTAGE_KEY

    def get_price_history_df(self, symbol):
        try:
            ts = TimeSeries(key=self.alpha_vantage_key)
            data, metadata = ts.get_daily(symbol=symbol, outputsize='full')
            df = pd.DataFrame.from_dict(data).T
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            df['open'] = df['1. open'].astype(float)
            df['high'] = df['2. high'].astype(float)
            df['low'] = df['3. low'].astype(float)
            df['close'] = df['4. close'].astype(float)

            df = df[['open', 'high', 'low', 'close']]
            df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)

            df = df.reset_index()
            df = df.rename(columns={'index': 'date'})

            if symbol.endswith('.SA'):
                df['currency'] = 'BRL'
            else:
                df['currency'] = 'USD'

            return df[['date', 'open', 'high', 'low', 'close', 'currency']]

        except Exception as e:
            print('AlphaVantage: Erro ao buscar dados históricos: ', str(e))
            raise e

    def get_sp500_history(self):
        try:
            ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
            data, metadata = ts.get_daily(symbol='SPY', outputsize='full')

            data.index = pd.to_datetime(data.index)
            data.sort_index(inplace=True)
            data['preco'] = data['4. close'].astype(float)

            df = data[['preco']]
            df['data'] = df.index

            df.reset_index(drop=True, inplace=True)

            return df[['data', 'preco']]

        except Exception as e:
            print(
                'AlphaVantage: Erro ao buscar dados históricos do S&P 500:',
                str(e),
            )
            raise e

    def get_usd_brl_exchange_rate_alpha_vantage(self):
        try:
            fx = ForeignExchange(key=self.alpha_vantage_key)
            data, _ = fx.get_currency_exchange_daily(
                from_symbol='USD', to_symbol='BRL', outputsize='full'
            )
            df = pd.DataFrame.from_dict(data).T
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            df['BRL/USD'] = df['4. close'].astype(float)
            df = df.reset_index()
            df = df.rename(columns={'index': 'data'})
            return df[['data', 'BRL/USD']]
        except Exception as e:
            raise e
