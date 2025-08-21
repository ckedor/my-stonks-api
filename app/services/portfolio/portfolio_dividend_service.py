import pandas as pd

from app.api.portfolio.dividend.schema import DividendFilters
from app.infrastructure.db.models.portfolio import Dividend
from app.infrastructure.db.repositories.portfolio import PortfolioRepository


async def get_dividends(
    session,
    portfolio_id: int,
    filters: DividendFilters
) -> pd.DataFrame:
    repo = PortfolioRepository(session)
    dividends = await repo.get_portfolio_dividends(
        portfolio_id, filters
    )
    return dividends

async def create_dividend(session, dividend_data):
    async with session.begin():
        repo = PortfolioRepository(session)
        dividend = await repo.create(Dividend, dividend_data.dict())
        return dividend

async def update_dividend(session, dividend_data):
    repo = PortfolioRepository(session)
    async with session.begin():
        existing_dividend = await repo.get(Dividend, dividend_data.id)
        if not existing_dividend:
            return None

        update_data = dividend_data.dict(exclude_unset=True)
        updated_dividend = await repo.update(Dividend, update_data)
    
    return updated_dividend

async def delete_dividend(session, dividend_id: int):
    async with session.begin():
        repo = PortfolioRepository(session)
        existing_dividend = await repo.get(Dividend, dividend_id)
        if not existing_dividend:
            return None

        return await repo.delete(Dividend, dividend_id)