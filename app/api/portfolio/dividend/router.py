from fastapi import APIRouter, Depends, HTTPException, status
from typing_extensions import Annotated

from app.api.portfolio.dividend.schema import (
    Dividend,
    DividendCreateRequest,
    DividendFilters,
    DividendUpdateRequest,
)
from app.infra.db.session import get_session
from app.services.portfolio import portfolio_dividend_service

router = APIRouter(prefix='/dividends', tags=['Portfolio Dividends'])


@router.get('/{portfolio_id}', response_model=list[Dividend])
async def get_portfolio_dividends(
    portfolio_id: int,
    filters: Annotated[DividendFilters, Depends()],
    session = Depends(get_session),
):
    return await portfolio_dividend_service.get_dividends(session, portfolio_id, filters)

@router.post('/')
async def create_dividend(
    dividend: DividendCreateRequest,
    session = Depends(get_session),
):
    return await portfolio_dividend_service.create_dividend(session, dividend)


@router.put('/')
async def update_dividend(
    dividend_data: DividendUpdateRequest,
    session = Depends(get_session),
):
    updated = await portfolio_dividend_service.update_dividend(session, dividend_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dividend not found")
    return updated


@router.delete('/{dividend_id}')
async def delete_dividend(
    dividend_id: int,
    session = Depends(get_session),
):
    deleted = await portfolio_dividend_service.delete_dividend(session, dividend_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dividend not found")
    return {"detail": "Dividend deleted successfully"}