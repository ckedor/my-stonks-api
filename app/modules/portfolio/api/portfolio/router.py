from fastapi import APIRouter, Depends

from app.infra.db.session import get_session
from app.modules.portfolio.api.portfolio.schemas import (
    CreatePortfolioRequest,
    Portfolio,
    UpdatePortfolioRequest,
)
from app.modules.portfolio.service.portfolio_base_service import PortfolioBaseService
from app.modules.users.models import User
from app.modules.users.views import current_active_user

router = APIRouter(tags=['Portfolio'])


@router.post('/create')
async def create_portfolio(
    portfolio: CreatePortfolioRequest,
    user: User = Depends(current_active_user),
    session = Depends(get_session),
):
    service = PortfolioBaseService(session)
    return await service.create_portfolio(portfolio, user.id)


@router.get('/list', response_model=list[Portfolio])
async def list_user_portfolios(
    user: User = Depends(current_active_user),
    session = Depends(get_session),
):
    service = PortfolioBaseService(session)
    return await service.list_user_portfolios(user.id)


@router.put('/')
async def update_portfolio(
    payload: UpdatePortfolioRequest,
    session = Depends(get_session),
):
    service = PortfolioBaseService(session)
    await service.update_portfolio(payload)
    return {'message': 'Portfolio updated successfully.'}


@router.delete('/{portfolio_id}')
async def delete_portfolio(
    portfolio_id: int,
    session = Depends(get_session),
):
    service = PortfolioBaseService(session)
    await service.delete_portfolio(portfolio_id)
    return {'message': 'Portfolio deleted successfully.'}
