from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.infra.db.session import get_session
from app.modules.asset.api.schemas import AssetDetailsWithPosition
from app.modules.portfolio.service.portfolio_position_service import (
    PortfolioPositionService,
)
from app.utils.response import df_response

router = APIRouter(tags=['Portfolio Position'])


@router.get('/{portfolio_id}/returns')
async def get_portfolio_returns(
    portfolio_id: int,
    session = Depends(get_session)
):
    service = PortfolioPositionService(session)
    returns = await service.get_portfolio_returns(portfolio_id)
    return returns


@router.get('/{portfolio_id}/asset_returns')
async def get_portfolio_asset_returns(
    portfolio_id: int,
    asset_ids: list[int] = Query(...),
    start_date: str = None,
    end_date: str = None,
    session = Depends(get_session),
):
    service = PortfolioPositionService(session)
    asset_returns = await service.get_asset_acc_returns(portfolio_id, asset_ids, start_date, end_date)
    return df_response(asset_returns)

@router.get('/{portfolio_id}/position')
async def get_portfolio_position(
    portfolio_id: int,
    group_by_broker: bool = Query(False),
    session = Depends(get_session),
):
    service = PortfolioPositionService(session)
    return await service.get_portfolio_position(portfolio_id, group_by_broker=group_by_broker)


@router.get('/{portfolio_id}/position_history')
async def get_portfolio_position_history(
    portfolio_id: int,
    asset_id: int = Query(None),
    session = Depends(get_session),
):
    service = PortfolioPositionService(session)
    return await service.get_portfolio_position_history(portfolio_id, asset_id)


@router.get('/{portfolio_id}/patrimony_evolution')
async def get_patrimony_evolution(
    portfolio_id: int,
    asset_id: int = Query(None),
    asset_type_id: int = Query(None),
    asset_type_ids: Optional[List[int]] = Query(None),
    session = Depends(get_session),
):
    service = PortfolioPositionService(session)
    evolution = await service.get_patrimony_evolution(portfolio_id, asset_id, asset_type_id, asset_type_ids)
    return evolution


@router.get('/asset/details', response_model=AssetDetailsWithPosition)
async def get_asset_details(
    portfolio_id: int,
    asset_id: int = Query(None),
    session = Depends(get_session)
):
    service = PortfolioPositionService(session)
    asset_details = await service.get_asset_details(portfolio_id, asset_id)
    return asset_details

@router.get('/{portfolio_id}/asset/analysis')
async def get_asset_analysis(
    portfolio_id: int,
    asset_id: int = Query(None),
    session = Depends(get_session)
):
    service = PortfolioPositionService(session)
    asset_analysis = await service.get_asset_analysis(portfolio_id, asset_id)
    return asset_analysis