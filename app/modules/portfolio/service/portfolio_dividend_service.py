# app/modules/portfolio/service/portfolio_dividend_service.py
"""
Portfolio dividend service - handles dividend management.
"""

import pandas as pd

from app.infra.db.models.portfolio import Dividend
from app.modules.portfolio.api.dividend.schema import DividendFilters
from app.modules.portfolio.repositories import PortfolioRepository


class PortfolioDividendService:
    def __init__(self, session):
        self.session = session
        self.repo = PortfolioRepository(session)

    async def get_dividends(
        self,
        portfolio_id: int,
        filters: DividendFilters
    ) -> pd.DataFrame:
        dividends = await self.repo.get_portfolio_dividends(
            portfolio_id, filters
        )
        return dividends

    async def create_dividend(self, dividend_data):
        dividend = await self.repo.create(Dividend, dividend_data.dict())
        await self.session.commit()
        return dividend

    async def update_dividend(self, dividend_data):
        existing_dividend = await self.repo.get(Dividend, dividend_data.id)
        if not existing_dividend:
            return None

        update_data = dividend_data.dict(exclude_unset=True)
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