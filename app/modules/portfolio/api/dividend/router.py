from app.infra.db.session import get_session
from app.modules.portfolio.api.dividend.schema import (
    Dividend,
    DividendCreateRequest,
    DividendFilters,
    DividendUpdateRequest,
)
from app.modules.portfolio.service.portfolio_dividend_service import (
    PortfolioDividendService,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing_extensions import Annotated

router = APIRouter(prefix='/dividends', tags=['Portfolio Dividends'])


@router.get('/{portfolio_id}', response_model=list[Dividend])
async def get_portfolio_dividends(
    portfolio_id: int,
    filters: Annotated[DividendFilters, Depends()],
    currency: str = Query('BRL'),
    session = Depends(get_session),
):
    service = PortfolioDividendService(session)
    return await service.get_dividends(portfolio_id, filters, currency=currency)

@router.post('/')
async def create_dividend(
    dividend: DividendCreateRequest,
    session = Depends(get_session),
):
    service = PortfolioDividendService(session)
    return await service.create_dividend(dividend)


@router.put('/')
async def update_dividend(
    dividend_data: DividendUpdateRequest,
    session = Depends(get_session),
):
    service = PortfolioDividendService(session)
    updated = await service.update_dividend(dividend_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dividend not found")
    return updated


@router.delete('/{dividend_id}')
async def delete_dividend(
    dividend_id: int,
    session = Depends(get_session),
):
    service = PortfolioDividendService(session)
    deleted = await service.delete_dividend(dividend_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dividend not found")
    return {"detail": "Dividend deleted successfully"}