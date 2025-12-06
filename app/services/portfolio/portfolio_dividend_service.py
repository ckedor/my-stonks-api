import pandas as pd
from requests import session

from app.api.portfolio.dividend.schema import DividendFilters
from app.infra.db.models.portfolio import Dividend
from app.infra.db.repositories.portfolio import PortfolioRepository


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
    
    repo = PortfolioRepository(session)
    dividend = await repo.create(Dividend, dividend_data.dict())
    await session.commit()
    return dividend

async def update_dividend(session, dividend_data):
    repo = PortfolioRepository(session)
    
    existing_dividend = await repo.get(Dividend, dividend_data.id)
    if not existing_dividend:
        return None

    update_data = dividend_data.dict(exclude_unset=True)
    updated_dividend = await repo.update(Dividend, update_data)
    
    await session.commit()
    return updated_dividend

async def delete_dividend(session, dividend_id: int):
    repo = PortfolioRepository(session)
    existing_dividend = await repo.get(Dividend, dividend_id)
    if not existing_dividend:
        return None

    deleted = await repo.delete(Dividend, dividend_id)
    await session.commit()
    return deleted