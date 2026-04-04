# app/infra/integrations/market_data_provider.py
import asyncio

import pandas as pd

from app.config.logger import logger
from app.infra.db.models.asset import Asset
from app.infra.db.models.constants.asset_type import ASSET_TYPE
from app.infra.db.models.constants.currency import CURRENCY
from app.infra.db.models.constants.exchange import EXCHANGE
from app.infra.db.models.constants.fii_segments import FIISegment
from app.infra.db.models.constants.index import INDEX
from app.infra.db.models.market_data import Index
from app.utils.strings import extract_digits

from .alpha_vantage_client import AlphaVantageClient
from .bcb_client import BCBClient
from .brapi_client import BrapiClient
from .crypto_compare_client import CryptoCompareClient
from .mais_retorno_client import MaisRetornoClient
from .status_invest_client import StatusInvestClient
from .tesouro_client import TesouroClient

STATUSINVEST_TO_INTERNAL_SEGMENT = {
    'Shoppings': FIISegment.SHOPPING,
    'Papéis': FIISegment.RECEIVABLES,
    'Lajes Corporativas': FIISegment.CORPORATE,
    'Fundo de Fundos': FIISegment.FOF,
    'Misto': FIISegment.HYBRID,
    'Imóveis Residenciais': FIISegment.RESIDENTIAL,
    'Imóveis Industriais e Logísticos': FIISegment.LOGISTICS,
    'Indefinido': FIISegment.OTHERS,
    'Imóveis Comerciais - Outros': FIISegment.HYBRID,
    'Serviços Financeiros Diversos': FIISegment.RECEIVABLES,
    'Agências de Bancos': FIISegment.BANK_AGENCIES,
    'Hotéis': FIISegment.HOTELS,
    'Fundo de Desenvolvimento': FIISegment.DEVELOPMENT,
    'Incorporações': FIISegment.INCORPORATIONS,
    'Varejo': FIISegment.RETAIL,
    'Outros': FIISegment.OTHERS,
    'Educacional': FIISegment.EDUCATIONAL,
    'Logística': FIISegment.LOGISTICS,
    'Hospitalar': FIISegment.HOSPITAL,
    'Exploração de Imóveis': FIISegment.HYBRID,
    'Tecidos. Vestuário e Calçados': FIISegment.SHOPPING,
}


class MarketDataProvider:
    def __init__(self):
        self.brapi_client = BrapiClient()
        self.bcb_api_client = BCBClient()
        self.alphavantage_client = AlphaVantageClient()
        self.mais_retorno_client = MaisRetornoClient()
        self.crypto_compare_client = CryptoCompareClient()
        self.status_invest_client = StatusInvestClient()
        self.tesouro_client = TesouroClient()

    async def get_series_historical_data(
        self, index: Index, init_date: pd.Timestamp = None
    ) -> pd.DataFrame:
        """
        Use: get asset prices and market indexes
        """
        history_df = None

        if index.id == INDEX.USDBRL:
            history_df = await self.bcb_api_client.get_usd_brl_quotation(init_date=init_date)
            history_df.rename(columns={'value': 'close'}, inplace=True)

        elif index.id in {INDEX.CDI, INDEX.IPCA}:
            history_df = await self.bcb_api_client.get_market_index_history_df(
                index.symbol, init_date=init_date
            )
            history_df.rename(columns={'value': 'close'}, inplace=True)

        elif index.id == INDEX.IFIX:
            history_df = await self.alphavantage_client.get_price_history_df(index.symbol)

        else:
            history_df = await self.brapi_client.get_price_history_df(
                index.symbol, init_date=init_date, interval='1d'
            )

        return history_df

    async def get_asset_prices(self, asset: Asset, init_date) -> pd.DataFrame:
        prices_df = pd.DataFrame()
        source = 'unknown'

        if asset.asset_type_id in {
            ASSET_TYPE.ETF,
            ASSET_TYPE.STOCK,
            ASSET_TYPE.FII,
            ASSET_TYPE.BDR,
        }:
            prices_df = await self.brapi_client.get_price_history_df(
                asset.ticker, init_date=init_date, interval='1d'
            )

            if prices_df.empty:
                prices_df = await self.alphavantage_client.get_price_history_df(asset.ticker)

        elif asset.asset_type.id == ASSET_TYPE.PREV:
            fund_legal_id = extract_digits(asset.fund.legal_id)
            prices_df = await self.mais_retorno_client.get_fund_price_history_df(fund_legal_id, init_date)

        elif asset.asset_type.id == ASSET_TYPE.CRIPTO:
            prices_df = await self.crypto_compare_client.get_crypto_price_history_df(
                asset.ticker, init_date=init_date
            )

        elif asset.asset_type.id == ASSET_TYPE.TREASURY:
            maturity_date = asset.treasury_bond.maturity_date
            type_name = asset.treasury_bond.type.name
            prices_df = await self.tesouro_client.get_precos_tesouro(type_name, maturity_date)

        return prices_df

    async def get_all_fiis_df(self):
        try:
            fiis_df = await self.status_invest_client.get_fiis_df()
            fiis_df['segment_id'] = fiis_df['segment'].map(
                lambda seg: STATUSINVEST_TO_INTERNAL_SEGMENT.get(seg, FIISegment.OTHERS).value
            )

            return fiis_df

        except Exception as e:
            logger.error(f'Falha ao obter FIIs do Status Invest: {e}')
            raise e

    async def get_fii_dividends_df(self, tickers: list, max: bool = True):
        """Busca dividendos de FIIs em paralelo."""
        async def fetch_provents(ticker):
            try:
                return await self.status_invest_client.get_provents_df(ticker, max=max)
            except Exception as e:
                logger.error(f'Falha ao obter dividendos do FII {ticker}: {e}')
                raise e

        tasks = [fetch_provents(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        
        provents_df = pd.concat(results, ignore_index=True) if results else pd.DataFrame()
        return provents_df

    async def get_asset_quotes(
        self,
        ticker: str,
        asset_type: str | None = None,
        exchange: str | None = None,
        date: str = None,
        start_date: str = None,
        end_date: str = None,
        treasury_maturity_date: str = None,
        treasury_type: str = None,
    ) -> dict:
        if date:
            start_date = pd.to_datetime(date)
            end_date = pd.to_datetime(date)

        history = {}
        
        if asset_type in {
            ASSET_TYPE.ETF.name,
            ASSET_TYPE.STOCK.name,
            ASSET_TYPE.FII.name,
            ASSET_TYPE.BDR.name,
        }:
            history = await self.brapi_client.get_quotes(
                ticker,
                start_date,
                end_date,
                interval='1d',
            )
            if not history['quotes']:
                ticker_with_suffix = ticker + '.SA' if exchange == EXCHANGE.B3 else ticker
                history = await self.alphavantage_client.get_quotes(
                    ticker_with_suffix,
                    init_date=start_date,
                    end_date=end_date,
                )

        elif asset_type == ASSET_TYPE.CRIPTO.name:
            history = await self.crypto_compare_client.get_quotes(
                ticker,
                start_date=start_date,
                end_date=end_date,
            )

        elif asset_type == ASSET_TYPE.PREV.name:
            history = await self.mais_retorno_client.get_quotes(
                extract_digits(ticker),
                start_date=start_date,
            )

        elif asset_type == ASSET_TYPE.TREASURY.name:
            history = await self.tesouro_client.get_quotes(
                treasury_type,
                pd.to_datetime(treasury_maturity_date),
                start_date=start_date,
                end_date=end_date,
            )

        return {
            'ticker': ticker,
            'asset_type': asset_type,
            'currency': history.get('currency'),
            'quotes': history.get('quotes', []),
        }

    async def close(self):
        """Close all HTTP clients."""
        await asyncio.gather(
            self.brapi_client.close(),
            self.bcb_api_client.close(),
            self.mais_retorno_client.close(),
            self.crypto_compare_client.close(),
            self.status_invest_client.close(),
            self.tesouro_client.close(),
        )