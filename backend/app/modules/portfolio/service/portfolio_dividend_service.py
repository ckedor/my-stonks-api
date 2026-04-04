# app/modules/portfolio/service/portfolio_dividend_service.py
"""
Portfolio dividend service - handles dividend management.
"""

import pandas as pd
from app.infra.db.models.asset import Asset
from app.infra.db.models.constants.currency import CURRENCY
from app.infra.db.models.portfolio import Dividend
from app.modules.market_data.service.market_data_service import MarketDataService
from app.modules.portfolio.api.dividend.schema import DividendFilters
from app.modules.portfolio.repositories import PortfolioRepository


class PortfolioDividendService:
    def __init__(self, session):
        self.session = session
        self.repo = PortfolioRepository(session)

    async def _get_usdbrl_rate(self, date) -> float:
        market_service = MarketDataService(self.session)
        df = await market_service.get_usd_brl_history(start_date=pd.Timestamp(date) - pd.DateOffset(days=10))
        df = df.sort_values('date')
        df = df[df['date'] <= pd.Timestamp(date)]
        if df.empty:
            raise ValueError(f'USD/BRL rate not found for date {date}')
        return float(df.iloc[-1]['usdbrl'])

    async def _fill_dual_currency(self, data: dict, asset_id: int) -> dict:
        asset = await self.repo.get(Asset, id=asset_id)
        if not asset:
            raise ValueError(f'Asset {asset_id} not found')

        rate = await self._get_usdbrl_rate(data['date'])

        if asset.currency_id == CURRENCY.USD:
            data['amount_usd'] = data['amount']
            data['amount'] = data['amount'] * rate
        else:
            data['amount_usd'] = data['amount'] / rate

        return data

    async def get_dividends(
        self,
        portfolio_id: int,
        filters: DividendFilters,
        currency: str = 'BRL',
    ) -> pd.DataFrame:
        dividends = await self.repo.get_portfolio_dividends(
            portfolio_id, filters, currency=currency
        )
        return dividends

    async def create_dividend(self, dividend_data):
        data = dividend_data.dict()
        data = await self._fill_dual_currency(data, data['asset_id'])
        dividend = await self.repo.create(Dividend, data)
        await self.session.commit()
        return dividend

    async def update_dividend(self, dividend_data):
        existing_dividend = await self.repo.get(Dividend, dividend_data.id)
        if not existing_dividend:
            return None

        update_data = dividend_data.dict(exclude_unset=True)

        if 'amount' in update_data:
            date = update_data.get('date', existing_dividend.date)
            update_data['date'] = date
            update_data = await self._fill_dual_currency(update_data, existing_dividend.asset_id)

        updated_dividend = await self.repo.update(Dividend, update_data)
        
        await self.session.commit()
        return updated_dividend

    async def delete_dividend(self, dividend_id: int):
        existing_dividend = await self.repo.get(Dividend, dividend_id)
        if not existing_dividend:
            return None

        deleted = await self.repo.delete(Dividend, dividend_id)
        await self.session.commit()
        return deleted