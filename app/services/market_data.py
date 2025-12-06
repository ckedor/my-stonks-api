from datetime import datetime
from decimal import Decimal
from enum import Enum

import pandas as pd

from app.config.logger import logger
from app.domain.finance.returns import calculate_acc_returns_from_prices
from app.infra.db.models.constants.index import INDEX
from app.infra.db.models.market_data import Index, IndexHistory
from app.infra.db.repositories.base_repository import DatabaseRepository
from app.infra.db.repositories.market_data import MarketDataRepository
from app.infra.integrations.market_data_provider import MarketDataProvider
from app.services.cache_service import CacheService
from app.utils.df import df_to_named_dict


async def list_indexes(session):
    repo = DatabaseRepository(session)
    indexes = await repo.get(Index)
    return indexes


async def get_indexes_history(session, start_date: pd.Timestamp = None) -> pd.DataFrame:
    cache = CacheService()
    cached = await cache.get_market_indexes_history()
    if cached:
        return cached
    
    return await compute_indexes_history(session, start_date)
    
    
async def compute_indexes_history(session, start_date: pd.Timestamp = None):
    repo = MarketDataRepository(session)
    
    start_date = start_date or pd.Timestamp(datetime.today()) - pd.DateOffset(years=5)
    index_history_df = await repo.get_index_history_df(start_date)

    index_history_returns_df = pd.DataFrame()

    usdbrl_df = index_history_df[index_history_df['index_name'] == 'USD/BRL'].copy()
    usdbrl_df['usdbrl'] = usdbrl_df['value'].astype(float)
    usdbrl_df = usdbrl_df[['date', 'usdbrl']]

    for index_name in index_history_df['index_name'].unique():
        index_series = index_history_df[index_history_df['index_name'] == index_name].copy()
        index_series.index = index_series['date']
        index_series = index_series.drop(columns=['date'])
        index_series[index_name] = index_series['value'].astype(float)
        index_series = index_series.sort_index()

        if index_name in {'NASDAQ', 'S&P500'}:
            index_series = pd.merge(index_series, usdbrl_df, on='date', how='left')
            index_series[index_name] *= index_series['usdbrl'].astype(float)
            index_series.index = index_series['date']

        index_series = index_series[[index_name]]

        if index_name in {'IPCA', 'CDI'}:
            index_series = _build_index_from_percent(index_series)

        returns_df = calculate_acc_returns_from_prices(index_series)
        if index_history_returns_df.empty:
            index_history_returns_df = returns_df
        else:
            index_history_returns_df = index_history_returns_df.join(returns_df, how='outer')
    index_history_returns_df = index_history_returns_df.reset_index().rename(
        columns={'index': 'date'}
    )
    
    result = df_to_named_dict(index_history_returns_df)
    return result

def _build_index_from_percent(series: pd.Series, base_value: float = 100.0) -> pd.Series:
    pct_series = series.fillna(0) / 100
    return base_value * (1 + pct_series).cumprod()

async def consolidate_market_indexes_history(session):
    logger.info('Consolidando histórico de índices de mercado')
    
    repo = MarketDataRepository(session)
    indexes = await repo.get_all(Index, relations=['currency'])

    for index in indexes:
        try:
            await _consolidate_index(index, session)
        except Exception as e:
            logger.warning(f'Falha ao consolidar {index.symbol}: {e}')

async def _consolidate_index(index: Index, session):
    repo = MarketDataRepository(session)
    most_recent = await repo.get(
        IndexHistory,
        by={'index_id': index.id},
        order_by='date desc',
        first=True,
    )

    init_date = most_recent.date - pd.DateOffset(days=10) if most_recent else None

    market_data_provider = MarketDataProvider()
    history_df = market_data_provider.get_series_historical_data(
        index, init_date=init_date
    ).copy()

    history_df = _extend_indexes_to_today(history_df, index.id)
    history_df['index_id'] = index.id
    cols = [col for col in IndexHistory.COLUMNS if col in history_df.columns]
    history_df = history_df[cols]

    history = history_df.to_dict(orient='records')
    await repo.upsert_bulk(IndexHistory, history, unique_columns=['index_id', 'date'])
    await session.commit()
    logger.info(f'{index.short_name} consolidado')

def _extend_indexes_to_today(history_df: pd.DataFrame, index_id) -> pd.DataFrame:
    df = history_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    full_range = pd.DataFrame({
        'date': pd.date_range(start=df['date'].min(), end=datetime.today(), freq='D')
    })
    df = pd.merge(full_range, df, on='date', how='left')

    if index_id in {INDEX.IPCA, INDEX.CDI}:
        df['close'] = df['close'].fillna(0)

    df['close'] = df['close'].ffill()
    return df

async def get_usd_brl_history(session, as_df=True) -> pd.DataFrame:
    #cache = CacheService()
    #cached = await cache.get_usd_brl_history()
    #if cached:
    #    if as_df:
    #        df = pd.DataFrame(cached)
    #        df['date'] = pd.to_datetime(df['date'])
    #        return df
    #    return cached

    min_required_date = pd.Timestamp.today() - pd.DateOffset(years=10)

    repo = MarketDataRepository(session)
    usdbrl = await repo.get(
        IndexHistory,
        by={'index_id': INDEX.USDBRL, 'date__gte': min_required_date},
    )
    if not usdbrl:
        raise ValueError('USD/BRL history not found')
    
    payload = [
        {
            "date": o.date.isoformat(),
            "usdbrl": float(o.close) if isinstance(o.close, Decimal) else (float(o.close) if o.close is not None else None),
        }
        for o in usdbrl
    ]
    #await cache.set_usd_brl_history(payload)

    if as_df:
        df = pd.DataFrame(payload)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return payload

async def get_asset_quotes(
    ticker: str,
    asset_type: str | None = None,
    exchange: str | None = None,
    date: str = None,
    start_date: str = None,
    end_date: str = None,
    treasury_type: str = None,
    treasury_maturity_date: str = None
) -> float | None:
    market_data_provider = MarketDataProvider()
    
    return market_data_provider.get_asset_quotes(
        ticker,
        asset_type,
        exchange,
        date,
        start_date,
        end_date,
        treasury_type=treasury_type,
        treasury_maturity_date=treasury_maturity_date,
    )
    
    
