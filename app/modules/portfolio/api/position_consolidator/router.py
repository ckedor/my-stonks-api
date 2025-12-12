from fastapi import APIRouter, Depends

from app.entrypoints.worker.task_runner import run_task
from app.infra.db.session import get_session
from app.modules.portfolio.repositories import PortfolioRepository
from app.modules.portfolio.service.portfolio_consolidator_service import (
    PortfolioConsolidatorService,
)
from app.modules.portfolio.tasks.set_patrimony_evolution_cache import (
    set_patrimony_evolution_cache,
)
from app.modules.portfolio.tasks.set_portfolio_returns_cache import (
    set_portfolio_returns_cache,
)
from app.modules.users.views import current_superuser

router = APIRouter(tags=['Portfolio Consolidator'], dependencies=[Depends(current_superuser)])


@router.post('/{portfolio_id}/consolidate')
async def consolidate_portfolio(
    portfolio_id: int,
    session = Depends(get_session)
):
    service = PortfolioConsolidatorService(session)
    await service.consolidate_position_portfolio(portfolio_id)
    run_task(set_patrimony_evolution_cache, portfolio_id)
    run_task(set_portfolio_returns_cache, portfolio_id)
    return {'message': 'OK'}


@router.post('/{portfolio_id}/recalculate_asset_position')
async def consolidate_portfolio_asset(
    portfolio_id: int,
    asset_id: int,
    session = Depends(get_session)
):
    service = PortfolioConsolidatorService(session)
    await service.recalculate_position_asset(portfolio_id, asset_id)
    run_task(set_patrimony_evolution_cache, portfolio_id)
    run_task(set_portfolio_returns_cache, portfolio_id)
    return {'message': 'OK'}


@router.post('/{portfolio_id}/recalculate_all_positions')
async def recalculate_all_positions(
    portfolio_id: int,
    session = Depends(get_session)
):
    service = PortfolioConsolidatorService(session)
    await service.recalculate_all_positions_portfolio(portfolio_id)
    run_task(set_patrimony_evolution_cache, portfolio_id)
    run_task(set_portfolio_returns_cache, portfolio_id)
    return {'message': 'OK'}