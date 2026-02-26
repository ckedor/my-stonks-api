# app/modules/portfolio/service/portfolio_position_service.py
"""
Portfolio position service - handles position queries and analysis.
"""

import datetime
from typing import Any

import numpy as np
import pandas as pd
from fastapi import HTTPException

from app.domain.finance.performance_metrics import annualize_rets
from app.domain.finance.returns import calculate_returns
from app.infra.db.models.constants.currency import CURRENCY
from app.infra.db.models.constants.index import INDEX
from app.infra.db.models.portfolio import Position
from app.infra.redis.decorators import cached
from app.infra.redis.redis_service import RedisService
from app.modules.asset.api.schemas import AssetDetailsOut, AssetDetailsWithPosition
from app.modules.market_data.service.market_data_service import MarketDataService
from app.modules.portfolio.domain.asset_analysis import calculate_asset_analysis
from app.modules.portfolio.domain.returns import (
    calculate_asset_acc_returns,
    calculate_portfolio_daily_returns,
    calculate_returns_portfolio,
)
from app.modules.portfolio.repositories import PortfolioRepository
from app.utils.df import df_to_dict_list, df_to_named_dict
from app.utils.response import df_response


class PortfolioPositionService:
    def __init__(self, session):
        self.session = session
        self.repo = PortfolioRepository(session)
        self.market_data_service = MarketDataService(session)
        self.cache = RedisService()

    async def get_asset_details(self, portfolio_id: int, asset_id: int = None) -> dict:
        asset = await self.repo.get_asset_details(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail='Ativo não encontrado')

        position = await self.repo.get(
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
        return AssetDetailsWithPosition(**asset_serialized_with_position)
    
    async def get_asset_analysis(self, portfolio_id: int, asset_id: int) -> dict:
        asset_position_df = await self.repo.get_asset_position_df(
            portfolio_id, [asset_id], start_date=None, end_date=None
        )

        if asset_position_df.empty:
            return None

        returns = calculate_portfolio_daily_returns(asset_position_df)
        returns = returns[['date', 'asset_return']]
        
        asset_returns = returns.set_index('date')['asset_return']
        start_date = returns['date'].min()
            
        benchmarks = {}

        cdi_history = await self.market_data_service.get_index_history(start_date, INDEX.CDI)
        benchmarks['CDI'] = cdi_history

        category = await self.repo.get_asset_category(portfolio_id, asset_id)
        if category.benchmark_id != INDEX.CDI:
            benchmark_history = await self.market_data_service.get_index_history(
                start_date, category.benchmark_id
            )
            benchmarks[category.benchmark.short_name] = benchmark_history
        

        result = calculate_asset_analysis(asset_returns, benchmarks)

        return result


    async def get_aported_history(self, portfolio_id: int):
        transactions_df = await self.repo.get_transactions_df(portfolio_id)
        usd_brl_df = await self.market_data_service.get_usd_brl_history(transactions_df['date'].min())
        transactions_df = transactions_df.merge(usd_brl_df[['date', 'usdbrl']], on='date', how='left')
        transactions_df['amount'] = transactions_df.apply(
            lambda row: row['quantity'] * row['price'] * (row['usdbrl'] if row['currency_id'] == CURRENCY.USD else 1), axis=1
        )
        total_aported = transactions_df.groupby('date')['amount'].sum().reset_index()
        total_aported.rename(columns={'amount': 'aported'}, inplace=True)
        return total_aported

    @cached(key_prefix="patrimony_evolution", cache=lambda self: self.cache, ttl=3600)
    async def get_patrimony_evolution(
        self, 
        portfolio_id: int,
        asset_id: int = None, 
        asset_type_id: int = None,
        asset_type_ids: list = None,
    ) -> pd.DataFrame:
        return await self.compute_patrimony_evolution(
            portfolio_id, asset_id, asset_type_id, asset_type_ids,
        )
        
    async def compute_patrimony_evolution(
        self, portfolio_id: int,
        asset_id: int = None, 
        asset_type_id: int = None,
        asset_type_ids: list = None,
    ) -> pd.DataFrame:
        portfolio_position_df = await self.repo.get_portfolio_position_df(
            portfolio_id, 
            asset_id=asset_id, 
            asset_type_id=asset_type_id, 
            asset_type_ids=asset_type_ids,
        )

        if portfolio_position_df.empty:
            return None

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
        
        aported_history = await self.get_aported_history(portfolio_id)
        result = result.merge(aported_history[['date', 'aported']], on='date', how='left')
        result['acc_aported'] = (
            result['aported']
            .fillna(0)
            .cumsum()
        )
        
        return df_to_dict_list(result)

    async def get_portfolio_returns(self, portfolio_id: int):
        return await self.compute_portfolio_returns(portfolio_id)
    
    async def compute_portfolio_returns(self, portfolio_id: int):
        portfolio_position_df = await self.repo.get_portfolio_position_df(portfolio_id)

        returns = calculate_returns_portfolio(portfolio_position_df)
        
        assets_from_current_position = await self.repo.get_assets_from_current_position(portfolio_id)
        assets_returns = returns['assets_returns'].copy()
        
        asset_returns = assets_returns[['date'] + assets_from_current_position]
        
        response = {
            'assets': df_to_named_dict(asset_returns),
            'categories': df_to_named_dict(returns['category_returns']),
        }
        
        return response

    async def get_asset_acc_returns(
        self,
        portfolio_id: int,
        asset_ids: list[int],
        start_date: str = None,
        end_date: str = None
    ):
        daily_returns_df = await self.get_asset_returns(portfolio_id, asset_ids, start_date, end_date)
        returns_df = calculate_asset_acc_returns(daily_returns_df)
        return returns_df
    
    async def get_asset_returns(
        self,
        portfolio_id: int,
        asset_ids: list[int],
        start_date: str = None,
        end_date: str = None
    ):
        asset_position_df = await self.repo.get_asset_position_df(
            portfolio_id, asset_ids, start_date, end_date
        )

        if asset_position_df.empty:
            return None

        daily_returns_df = calculate_portfolio_daily_returns(asset_position_df)
        return daily_returns_df[['date', 'asset_return']]
    

    async def get_portfolio_position(
        self, 
        portfolio_id: int,
        date: pd.Timestamp = None,
        asset_type_id = None,
        group_by_broker: bool = False,
        ) -> list:
        if group_by_broker:
            pos_df = await self.repo.get_position_on_date_by_broker(
                portfolio_id, date, asset_type_id
            )
        else:
            pos_df = await self.repo.get_position_on_date(
                portfolio_id, date, asset_type_id
            )
        
        if pos_df is None or pos_df.empty:
            return []

        pos_df['value'] = pos_df['quantity'] * pos_df['price']

        return df_response(pos_df)

    async def get_portfolio_position_history(
        self, portfolio_id: int, asset_id: int = None
    ) -> pd.DataFrame:
        pos_df = await self.repo.get_portfolio_position_df(portfolio_id, asset_id=asset_id)

        if pos_df.empty:
            return []

        pos_df['value'] = pos_df['quantity'] * pos_df['price']

        return df_response(pos_df)