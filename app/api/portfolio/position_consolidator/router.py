from fastapi import APIRouter, Depends

from app.infrastructure.db.repositories.portfolio import PortfolioRepository
from app.infrastructure.db.session import get_session
from app.services.portfolio import portfolio_consolidator_service as service
from app.users.views import current_superuser
from app.worker.task_runner import run_task
from app.worker.tasks.set_patrimony_evolution_cache import set_patrimony_evolution_cache
from app.worker.tasks.set_portfolio_returns_cache import set_portfolio_returns_cache

router = APIRouter(tags=['Portfolio Consolidator'], dependencies=[Depends(current_superuser)])


@router.post('/{portfolio_id}/consolidate')
async def consolidate_portfolio(
    portfolio_id: int,
    session = Depends(get_session)
):
    await service.consolidate_position_portfolio(session, portfolio_id)
    run_task(set_patrimony_evolution_cache, portfolio_id)
    run_task(set_portfolio_returns_cache, portfolio_id)
    return {'message': 'OK'}


@router.post('/{portfolio_id}/recalculate_asset_position')
async def consolidate_portfolio_asset(
    portfolio_id: int,
    asset_id: int,
    session = Depends(get_session)
):
    await service.recalculate_position_asset(session, portfolio_id, asset_id)
    run_task(set_patrimony_evolution_cache, portfolio_id)
    run_task(set_portfolio_returns_cache, portfolio_id)
    return {'message': 'OK'}


@router.post('/{portfolio_id}/recalculate_all_positions')
async def recalculate_all_positions(
    portfolio_id: int,
    session = Depends(get_session)
):
    await service.recalculate_all_positions_portfolio(session, portfolio_id)
    run_task(set_patrimony_evolution_cache, portfolio_id)
    run_task(set_portfolio_returns_cache, portfolio_id)
    return {'message': 'OK'}