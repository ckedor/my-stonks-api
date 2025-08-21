import pandas as pd

from app.config.logger import logger
from app.infrastructure.db.models.asset import Asset
from app.infrastructure.db.models.constants.asset_type import ASSET_TYPE
from app.infrastructure.db.models.constants.currency import CURRENCY
from app.infrastructure.db.models.constants.fii_segments import FIISegment
from app.infrastructure.db.models.constants.index import INDEX
from app.infrastructure.db.models.market_data import Index
from app.utils.strings import extract_digits

from .alpha_vantage_client import AlphaVantageClient
from .bcb_client import BCBClient
from .brapi_client import BrapiClient
from .crypto_compare_client import CryptoCompareClient
from .mais_retorno_client import MaisRetornoClient
from .status_invest_client import StatusInvestClient
from .tesouro_client import TesouroClient

# from app.infrastructure.integrations.foxbit_client import FoxbitClient
# from app.infrastructure.integrations.status_invest_client import StatusInvestClient
# from app.infrastructure.integrations.tesouro_client import TesouroClient

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
        # self.foxbit_client = FoxbitClient()
        # self.anbima_client = AnbimaClient()
        self.tesouro_client = TesouroClient()

    def get_series_historical_data(
        self, index: Index, init_date: pd.Timestamp = None
    ) -> pd.DataFrame:
        """
        Use: get asset prices and market indexes
        """
        history_df = None

        if index.id == INDEX.USDBRL:
            history_df = self.bcb_api_client.get_usd_brl_quotation(init_date=init_date)
            history_df.rename(columns={'value': 'close'}, inplace=True)

        elif index.id in {INDEX.CDI, INDEX.IPCA}:
            history_df = self.bcb_api_client.get_market_index_history_df(
                index.symbol, init_date=init_date
            )
            history_df.rename(columns={'value': 'close'}, inplace=True)

        elif index.id == INDEX.IFIX:
            history_df = self.alphavantage_client.get_price_history_df(index.symbol)

        else:
            history_df = self.brapi_client.get_price_history_df(
                index.symbol, init_date=init_date, interval='1d'
            )

        return history_df

    def get_asset_prices(self, asset: Asset, init_date) -> pd.DataFrame:
        prices_df = pd.DataFrame()

        if asset.asset_type_id in {
            ASSET_TYPE.ETF,
            ASSET_TYPE.STOCK,
            ASSET_TYPE.FII,
            ASSET_TYPE.BDR,
        }:
            prices_df = self.brapi_client.get_price_history_df(
                asset.ticker, init_date=init_date, interval='1d'
            )

            if prices_df.empty or prices_df['date'].min() > init_date:
                prices_df = self.alphavantage_client.get_price_history_df(asset.ticker)

        elif asset.asset_type.id == ASSET_TYPE.PREV:
            fund_legal_id = extract_digits(asset.fund.legal_id)
            prices_df = self.mais_retorno_client.get_fund_price_history_df(fund_legal_id, init_date)

        elif asset.asset_type.id == ASSET_TYPE.CRIPTO:
            prices_df = self.crypto_compare_client.get_crypto_price_history_df(
                asset.ticker, init_date=init_date
            )

        elif asset.asset_type.id == ASSET_TYPE.TREASURY:
            maturity_date = asset.treasury_bond.maturity_date
            type_name = asset.treasury_bond.type.name
            prices_df = self.tesouro_client.get_precos_tesouro(type_name, maturity_date)

        return prices_df


    def get_all_fiis_df(self):
        try:
            fiis_df = self.status_invest_client.get_fiis_df()
            fiis_df['segment_id'] = fiis_df['segment'].map(
                lambda seg: STATUSINVEST_TO_INTERNAL_SEGMENT.get(seg, FIISegment.OTHERS).value
            )

            return fiis_df

        except Exception as e:
            logger.error(f'Falha ao obter FIIs do Status Invest: {e}')
            raise e
        
    def get_fii_dividends_df(self, tickers: list, max: bool = True):
        provents_df = pd.DataFrame()
        for ticker in tickers:
            try:
                fii_provents_df = self.status_invest_client.get_provents_df(ticker, max=max)
                provents_df = pd.concat([provents_df, fii_provents_df])
            except Exception as e:
                logger.error(f'Falha ao obter dividendos do FII {ticker}: {e}')
                raise e
        return provents_df