import datetime

import pandas as pd
from fastapi import HTTPException

import app.services.market_data as market_data_service
from app.api.asset.schemas import AssetDetailsOut, AssetDetailsWithPosition
from app.domain.old.finance.returns_calculator import ReturnsCalculator
from app.infra.db.models.constants.currency import CURRENCY
from app.infra.db.models.portfolio import Position
from app.infra.db.repositories.portfolio import PortfolioRepository
from app.utils.df import df_to_named_dict
from app.utils.response import df_response


async def get_asset_details(session, portfolio_id: int, asset_id: int = None) -> dict:
    repo = PortfolioRepository(session)
    asset = await repo.get_asset_details(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail='Ativo não encontrado')

    position = await repo.get(
        Position,
        by={'portfolio_id': portfolio_id, 'asset_id': asset_id},
        order_by='date desc',
        first=True,
    )

    asset_serialized = AssetDetailsOut.model_validate(asset).model_dump()
    asset_serialized_with_position = {
        **asset_serialized,
        'quantity': position.quantity,
        'price': position.price,
        'average_price': position.average_price,
        'value': (position.quantity * position.price),
        'acc_return': (None if pd.isna(position.acc_return) else position.acc_return),
        'twelve_months_return': (
            None if pd.isna(position.twelve_months_return) else position.twelve_months_return
        ),
    }
    return AssetDetailsWithPosition(**asset_serialized_with_position) ##TODO: Será q a camada service deveria conhecer o model pydantic?

async def get_aported_history(
    session, portfolio_id: int
):
    repo = PortfolioRepository(session)
    transactions_df = await repo.get_transactions_df(portfolio_id)
    usd_brl_df = await market_data_service.get_usd_brl_history(session, transactions_df['date'].min())
    transactions_df = transactions_df.merge(usd_brl_df[['date', 'usdbrl']], on='date', how='left')
    transactions_df['amount'] = transactions_df.apply(
        lambda row: row['quantity'] * row['price'] * (row['usdbrl'] if row['currency_id'] == CURRENCY.USD else 1), axis=1
    )
    total_aported = transactions_df.groupby('date')['amount'].sum().reset_index()
    total_aported.rename(columns={'amount': 'aported'}, inplace=True)
    return total_aported

async def get_patrimony_evolution(
    session, portfolio_id: int, 
    asset_id: int = None, 
    asset_type_id: int = None,
    asset_type_ids: list = None, 
    currency_id: int = None
) -> pd.DataFrame:
    
    repo = PortfolioRepository(session)
    portfolio_position_df = await repo.get_portfolio_position_df(
        portfolio_id, 
        asset_id=asset_id, 
        asset_type_id=asset_type_id, 
        asset_type_ids=asset_type_ids, 
        currency_id=currency_id
    )

    if portfolio_position_df.empty:
        return None

    #portfolio_position_df = await _normalize_currency(portfolio_position_df, currency) # TODO: Normalizar currency

    df = portfolio_position_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['patrimony'] = df['quantity'] * df['price']

    total_df = df.groupby('date')['patrimony'].sum().reset_index()
    total_df.rename(columns={'patrimony': 'portfolio'}, inplace=True)

    category_df = df.groupby(['date', 'category'])['patrimony'].sum().reset_index()
    category_pivot = category_df.pivot(
        index='date', columns='category', values='patrimony'
    ).reset_index()

    result = total_df.merge(category_pivot, on='date', how='left')
    
    aported_history = await get_aported_history(session, portfolio_id)
    result = result.merge(aported_history[['date', 'aported']], on='date', how='left')
    result['aported'] = (
        result['aported']
        .fillna(0)
        .cumsum()
    )
    
    return result

async def get_portfolio_returns(
    session, portfolio_id: int
):
    repo = PortfolioRepository(session)
    portfolio_position_df = await repo.get_portfolio_position_df(
        portfolio_id
    )

    returns_calculator = ReturnsCalculator()
    returns = returns_calculator.calculate_returns_portfolio(portfolio_position_df) # TODO: não usar essa classe. 
    
    assets_from_current_position = await repo.get_assets_from_current_position(portfolio_id)
    assets_returns = returns['assets_returns'].copy()
    
    asset_returns = assets_returns[['date'] + assets_from_current_position]
    
    response = {
        'assets': df_to_named_dict(asset_returns),
        'categories': df_to_named_dict(returns['category_returns']),
    }
    
    return response

async def get_asset_returns(
    session,
    portfolio_id: int,
    asset_ids: int,
    start_date: str = None,
    end_date: str = None
):
    repo = PortfolioRepository(session)
    asset_position_df = await repo.get_asset_position_df(
        portfolio_id, asset_ids, start_date, end_date
    )

    if asset_position_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f'Returns not found for asset_ids {asset_ids} in portfolio {portfolio_id}',
        )

    returns_calculator = ReturnsCalculator()
    returns_df = returns_calculator.calculate_asset_returns(asset_position_df)
    return df_response(returns_df)

async def get_portfolio_position(session, portfolio_id: int, date: pd.Timestamp = None, asset_type_id = None) -> list:
    repo = PortfolioRepository(session)
    pos_df = await repo.get_position_on_date(portfolio_id, date, asset_type_id)

    if pos_df is None or pos_df.empty:
        return []

    pos_df['value'] = pos_df['quantity'] * pos_df['price']

    return df_response(pos_df)

async def get_portfolio_position_history(
    session, portfolio_id: int, asset_id: int = None
) -> pd.DataFrame:
    repo = PortfolioRepository(session)
    pos_df = await repo.get_portfolio_position_df(portfolio_id, asset_id=asset_id)

    if pos_df.empty:
        return []

    pos_df['value'] = pos_df['quantity'] * pos_df['price']

    return df_response(pos_df)
