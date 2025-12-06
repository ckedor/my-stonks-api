from fastapi import APIRouter, Depends

import app.services.portfolio.portfolio_base_service as portfolio_service
from app.api.portfolio.portfolio.schemas import (
    CreatePortfolioRequest,
    Portfolio,
    UpdatePortfolioRequest,
)
from app.infra.db.session import get_session
from app.users.models import User
from app.users.views import current_active_user

router = APIRouter(tags=['Portfolio'])


@router.post('/create')
async def create_portfolio(
    portfolio: CreatePortfolioRequest,
    user: User = Depends(current_active_user),
    session = Depends(get_session),
):

    return await portfolio_service.create_portfolio(session, portfolio, user.id)


@router.get('/list', response_model=list[Portfolio])
async def list_user_portfolios(
    user: User = Depends(current_active_user),
    session = Depends(get_session),
):
    return await portfolio_service.list_user_portfolios(session, user.id)


@router.put('/')
async def update_portfolio(
    payload: UpdatePortfolioRequest,
    session = Depends(get_session),
):
    await portfolio_service.update_portfolio(session, payload)
    return {'message': 'Portfolio updated successfully.'}


@router.delete('/{portfolio_id}')
async def delete_portfolio(
    portfolio_id: int,
    session = Depends(get_session),
):
    await portfolio_service.delete_portfolio(session, portfolio_id)
    return {'message': 'Portfolio deleted successfully.'}
