from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.api.asset.schemas import AssetDetailsWithPosition
from app.infrastructure.db.repositories.portfolio import PortfolioRepository
from app.infrastructure.db.session import get_session
from app.services.cache_service import CacheService
from app.services.portfolio import portfolio_position_service as service
from app.utils.response import df_response

router = APIRouter(tags=['Portfolio Position'])


@router.get('/{portfolio_id}/returns')
async def get_portfolio_returns(
    portfolio_id: int,
    session = Depends(get_session)
):
    cache = CacheService()
    cached = await cache.get_portfolio_returns(portfolio_id)
    if cached:
        return cached

    returns = await service.get_portfolio_returns(session, portfolio_id)
    return returns


@router.get('/{portfolio_id}/asset_returns')
async def get_portfolio_asset_returns(
    portfolio_id: int,
    asset_ids: list[int] = Query(...),
    start_date: str = None,
    end_date: str = None,
    session = Depends(get_session),
):
    return await service.get_asset_returns(session, portfolio_id, asset_ids, start_date, end_date)


@router.get('/{portfolio_id}/position')
async def get_portfolio_position(
    portfolio_id: int,
    session = Depends(get_session),
):
    return await service.get_portfolio_position(session, portfolio_id)


@router.get('/{portfolio_id}/position_history')
async def get_portfolio_position_history(
    portfolio_id: int,
    asset_id: int = Query(None),
    session = Depends(get_session),
):
    return await service.get_portfolio_position_history(session, portfolio_id, asset_id)


@router.get('/{portfolio_id}/patrimony_evolution')
async def get_patrimony_evolution(
    portfolio_id: int,
    asset_id: int = Query(None),
    asset_type_id: int = Query(None),
    asset_type_ids: Optional[List[int]] = Query(None),
    currency_id: Optional[int] = Query(None),
    session = Depends(get_session),
):
    cache = CacheService()

    if asset_id is None and asset_type_id is None and asset_type_ids is None and currency_id is None:
        cached = await cache.get_patrimony_evolution_cache(portfolio_id)
        if cached:
            return cached

    evolution = await service.get_patrimony_evolution(session, portfolio_id, asset_id, asset_type_id, asset_type_ids, currency_id)
    return df_response(evolution)


@router.get('/asset/details', response_model=AssetDetailsWithPosition)
async def get_asset_details(
    portfolio_id: int,
    asset_id: int = Query(None),
    session = Depends(get_session)
):
    asset_details = await service.get_asset_details(session, portfolio_id, asset_id)
    return asset_details
