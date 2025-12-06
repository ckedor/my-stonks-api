from fastapi import APIRouter, Depends

from app.entrypoints.worker.task_runner import run_task
from app.infra.db.session import get_session
from app.services.portfolio import portfolio_category_service
from app.worker.tasks.set_patrimony_evolution_cache import set_patrimony_evolution_cache
from app.worker.tasks.set_portfolio_returns_cache import set_portfolio_returns_cache

from .schema import CategoryAssignmentRequest, SaveCategoriesRequest

router = APIRouter(prefix='/category', tags=['Portfolio Category'])


@router.post('/save')
async def save_custom_category(
    payload: SaveCategoriesRequest,
    session = Depends(get_session)
):
    await portfolio_category_service.save_custom_categories(session, payload.categories)
    return {'message': 'Custom category saved successfully.'}


@router.delete('/{category_id}')
async def delete_custom_category(
    category_id: int,
    session = Depends(get_session)
):
    
    await portfolio_category_service.delete_custom_category(session, category_id)
    return {'message': 'Custom category deleted successfully.'}


@router.post('/category_assignment')
async def assign_category_to_assets(
    payload: CategoryAssignmentRequest,
    session = Depends(get_session)
):
    
    await portfolio_category_service.assign_category_to_asset(session, payload)

    run_task(set_patrimony_evolution_cache, payload.portfolio_id)
    run_task(set_portfolio_returns_cache, payload.portfolio_id)
    return {'message': 'Category assigned to assets successfully.'}
