from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import HTTPException

from app.config.logger import logger
from app.domain.finance.trade import average_price
from app.domain.old.finance.fixed_income_calculator import FixedIncomeCalculator
from app.infrastructure.db.models.asset import Asset, Event
from app.infrastructure.db.models.constants.asset_type import ASSET_TYPE
from app.infrastructure.db.models.constants.currency import CURRENCY, CURRENCY_MAP
from app.infrastructure.db.models.constants.user_configuration import USER_CONFIGURATION
from app.infrastructure.db.models.portfolio import (
    Dividend,
    PortfolioUserConfiguration,
    Position,
    Transaction,
)
from app.infrastructure.db.repositories.base_repository import DatabaseRepository
from app.infrastructure.db.repositories.portfolio import PortfolioRepository
from app.infrastructure.integrations.market_data_provider import MarketDataProvider
from app.services import market_data as market_data_service


async def consolidate_position_portfolio(session, portfolio_id):
    logger.info(f'Consolidando posições do portfolio {portfolio_id}')
    
    repo = PortfolioRepository(session)
    positions_df = await repo.get(
        Position,
        by={
            'portfolio_id': portfolio_id,
        },
        order_by='date desc',
        as_df=True,
    )
    if positions_df.empty:
        await recalculate_all_positions_portfolio(session, portfolio_id)
        return

    recent_date = positions_df['date'].max() - pd.DateOffset(days=10)
    asset_ids = positions_df[positions_df['date'] >= recent_date]['asset_id'].unique().tolist()
    for asset_id in asset_ids:
        await recalculate_position_asset(session, portfolio_id, asset_id)

async def recalculate_position_asset(session, portfolio_id, asset_id):
    try:
        repo = PortfolioRepository(session)
        asset = await repo.get(Asset, asset_id, first=True, relations=["treasury_bond", "fixed_income"]) #TODO: eu preciso fazer o select in load do trasury_bond. Mas aqui não faz mt sentido. Repensar.
        transactions_df = await get_transactions(session, portfolio_id, asset_id)
        if transactions_df.empty:
            
            await repo.delete(
                Position,
                by={'asset_id': asset_id, 'portfolio_id': portfolio_id},
            )
            return
        events = await repo.get(Event, order_by='date asc', by={'asset_id': asset.id})
        if len(events) > 0:
            for event in events:
                mask = transactions_df['date'] < pd.to_datetime(event.date)
                transactions_df.loc[mask, 'quantity'] *= event.factor

        prices_df = await get_prices(session, transactions_df, asset, portfolio_id)
        
        start_date = transactions_df['date'].min()
        end_date = prices_df['date'].max()
        full_dates = pd.DataFrame({'date': pd.date_range(start=start_date, end=end_date)})
        position_df = full_dates.merge(prices_df, on='date', how='left')
        position_df = position_df.merge(transactions_df, on='date', how='left')
        
        for col in ['price', 'price_usd', 'average_price', 'average_price_usd']:
            if col in position_df.columns:
                position_df[col] = position_df[col].ffill()
        position_df['quantity'] = position_df['quantity'].fillna(0).cumsum().round(6)
        
        _calculate_returns(position_df)
        
        await _persist_positions_db(session, position_df, transactions_df['date'].min(), asset, portfolio_id)
        logger.info(f'Sucesso ao consolidar ativo: {asset.ticker}')
    except Exception as e:
        logger.error(f'Falha ao calcular posições para {asset.ticker}: {e}')

    
async def get_transactions(session, portfolio_id, asset_id):
    repo = PortfolioRepository(session)
    trans_df = await repo.get_transactions_df(
        portfolio_id=portfolio_id,
        asset_id=asset_id
    )

    if trans_df.empty:
        return trans_df

    trans_df['date'] = pd.to_datetime(trans_df['date'])
    trans_df = trans_df.sort_values(by='date')

    trans_df = (
        trans_df.groupby('date', as_index=False)
        .apply(
            lambda g: pd.Series({
                'quantity': g['quantity'].sum(),
                'price': (g['price'] * g['quantity']).sum() / g['quantity'].sum(),
                'currency_id': g['currency_id'].iloc[0],
            })
        )
        .reset_index(drop=True)
    )
    
    usd_brl_df = await market_data_service.get_usd_brl_history(session, trans_df['date'].min())

    trans_df = trans_df.merge(usd_brl_df[['date', 'usdbrl']], on='date', how='left')
    trans_df['transaction_price_brl'] = trans_df.apply(
        lambda row: row['price'] if row['currency_id'] == 1 else row['price'] * row['usdbrl'],
        axis=1
    )
    trans_df['transaction_price_usd'] = trans_df.apply(
        lambda row: row['price'] if row['currency_id'] == 2 else row['price'] / row['usdbrl'],
        axis=1
    )
    
    trans_df['average_price'] = average_price(trans_df, price_col='transaction_price_brl')
    trans_df['average_price_usd'] = average_price(trans_df, price_col='transaction_price_usd')
    trans_df = trans_df[['date', 'quantity', 'transaction_price_brl', 'average_price', 'average_price_usd']]
    return trans_df

async def get_prices(session, asset_transactions_df, asset, portfolio_id):
    init_date = asset_transactions_df['date'].min()
    repo = DatabaseRepository(session)
    fixed_income_calculator = FixedIncomeCalculator(repo)
    market_data_provider = MarketDataProvider()
    if _is_fixed_income(asset):
        prices_df = await fixed_income_calculator.calculate_asset_prices(
            asset, portfolio_id, asset_transactions_df
        )
        prices_df['currency'] = CURRENCY.BRL
    else:
        prices_df = market_data_provider.get_asset_prices(asset, init_date)
        prices_df = _extend_value_to_today(prices_df, 'close')
        prices_df = prices_df[['date', 'close', 'currency']]
        prices_df['currency'] = prices_df['currency'].map(CURRENCY_MAP)
        prices_df['currency'] = prices_df['currency'].ffill()

    usd_brl_df = await market_data_service.get_usd_brl_history(session, asset_transactions_df['date'].min())
    prices_df = prices_df.merge(usd_brl_df[['date', 'usdbrl']], on='date', how='left')
    
    prices_df['price'] = prices_df.apply(
        lambda row: row['close'] if row['currency'] == CURRENCY.BRL else row['close'] * row['usdbrl'],
        axis=1
    )
    prices_df['price_usd'] = prices_df.apply(
        lambda row: row['close'] if row['currency'] == CURRENCY.USD else row['close'] / row['usdbrl'],
        axis=1
    )
    prices_df = prices_df[['date', 'price', 'price_usd']]
    prices_df = prices_df[prices_df['date'] >= init_date]
    
    return prices_df
    

async def _persist_positions_db(
    session, position_df: pd.DataFrame, min_date: pd.Timestamp, asset: Asset, portfolio_id: int
):
    repo = PortfolioRepository(session)
    position_df['asset_id'] = asset.id
    position_df['portfolio_id'] = portfolio_id
    position_df = position_df[Position.COLUMNS]
    for col in ['quantity', 'portfolio_id', 'asset_id']:
        if col in position_df.columns:
            position_df.loc[:, col] = position_df[col].ffill()
    position_df = position_df[position_df['date'] >= min_date]
    
    position_df = position_df[position_df['quantity'] != 0]
    values = position_df.to_dict(orient='records')

    max_date = position_df['date'].max()

    await repo.delete(
        Position,
        by={
            'portfolio_id': portfolio_id,
            'asset_id': asset.id,
            'date__gt': max_date,
        }
    )

    await repo.upsert_bulk(Position, values, unique_columns=['portfolio_id', 'asset_id', 'date'])
    await session.commit()

async def recalculate_all_positions_portfolio(session, portfolio_id):
    repo = PortfolioRepository(session)
    transactions_df = await repo.get(
        Transaction, by={'portfolio_id': portfolio_id}, as_df=True
    )

    if transactions_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f'Transactions not found for portfolio {portfolio_id}',
        )

    asset_ids = transactions_df['asset_id'].unique().tolist()
    for asset_id in asset_ids:
        await recalculate_position_asset(session, portfolio_id, asset_id)

@staticmethod
def _is_fixed_income(asset):
    return asset.asset_type.id in {
        ASSET_TYPE.CRI,
        ASSET_TYPE.CRA,
        ASSET_TYPE.DEB,
        ASSET_TYPE.CDB,
        ASSET_TYPE.LCA,
    }

@staticmethod
def _calculate_returns(position_df):
    # BRL
    position_df['daily_return'] = position_df['price'].pct_change(fill_method=None).fillna(0)
    position_df['acc_return'] = (1 + position_df['daily_return']).cumprod() - 1

    position_df['twelve_months_return'] = None
    position_df['date_12m_ago'] = position_df['date'] - pd.DateOffset(years=1)
    acc_map_brl = position_df.set_index('date')['acc_return']
    position_df['acc_return_12m_ago'] = position_df['date_12m_ago'].map(acc_map_brl)
    position_df['twelve_months_return'] = (
        position_df['acc_return'] - position_df['acc_return_12m_ago']
    )

    # USD
    position_df['daily_return_usd'] = (
        position_df['price_usd'].pct_change(fill_method=None).fillna(0)
    )
    position_df['acc_return_usd'] = (1 + position_df['daily_return_usd']).cumprod() - 1

    acc_map_usd = position_df.set_index('date')['acc_return_usd']
    position_df['acc_return_usd_12m_ago'] = position_df['date_12m_ago'].map(acc_map_usd)
    position_df['twelve_months_return_usd'] = (
        position_df['acc_return_usd'] - position_df['acc_return_usd_12m_ago']
    )

    return position_df

@staticmethod
def _extend_value_to_today(
    prices_df: pd.DataFrame, value_field: str, date_field: str = 'date'
) -> pd.DataFrame:
    df = prices_df.copy()
    df[date_field] = pd.to_datetime(df[date_field])
    full_range = pd.DataFrame({
        date_field: pd.date_range(start=df[date_field].min(), end=datetime.today(), freq='D')
    })
    df = pd.merge(full_range, df, on=date_field, how='left')
    df[value_field] = df[value_field].ffill()

    return df

async def consolidate_fii_dividends(session, portfolio_id: int):
    repo = PortfolioRepository(session)
    user_configuration = await repo.get(
        PortfolioUserConfiguration, 
        by={'portfolio_id': portfolio_id, 
            'configuration_name_id': USER_CONFIGURATION.FIIS_DIVIDENDS_INTEGRATION
            }, 
        first=True
    )
    if user_configuration.enabled is False:
        return
    
    logger.info(f'Consolidando dividendos de FIIs do portfolio {portfolio_id}')
    positions_df = await repo.get_portfolio_position_df(
        portfolio_id=portfolio_id,
        asset_type_id=ASSET_TYPE.FII,
        start_date=pd.Timestamp.now() - pd.DateOffset(days=30),
    )
    if positions_df.empty:
        return
    
    market_data_provider = MarketDataProvider()
    fii_dividends_df = market_data_provider.get_fii_dividends_df(
        positions_df['ticker'].unique().tolist()
    )
    
    merged_df = positions_df.merge(
        fii_dividends_df,
        on=['ticker', 'date'],
        how='left'
    )
    merged_df['value_per_share'] = merged_df['value_per_share'].fillna(0)
    if 'dividend' not in merged_df.columns:
        merged_df['dividend'] = 0
        
    original_dividends = merged_df['dividend'].copy()

    merged_df['dividend'] = np.where(
        merged_df['dividend'] == 0,
        round(merged_df['quantity'] * merged_df['value_per_share'], 2),
        merged_df['dividend']
    )

    new_dividends_df = merged_df[(original_dividends == 0) & (merged_df['dividend'] > 0)]
    
    if new_dividends_df.empty:
        logger.info(f'Nenhum novo dividendo de FIIs encontrado para o portfolio {portfolio_id}')
        return
    
    for _, row in new_dividends_df.iterrows():
        await repo.create(
            Dividend,
            {
                'portfolio_id': portfolio_id,
                'asset_id': row['asset_id'],
                'date': row['date'],
                'amount': row['dividend']
            }
        )
    await session.commit()
    logger.info(f"Dividendos de {row['ticker']} na data {row['date']} consolidados com sucesso")

