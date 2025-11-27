from app.config.logger import logger
from app.worker.task_runner import celery_async_task, run_task
from app.worker.tasks.set_patrimony_evolution_cache import set_patrimony_evolution_cache
from app.worker.tasks.set_portfolio_returns_cache import set_portfolio_returns_cache


@celery_async_task(name="recalculate_asset_position")
async def recalculate_position_asset(portfolio_id: int, asset_id: int):
    from app.infrastructure.db.session import AsyncSessionLocal
    from app.services.portfolio import portfolio_consolidator_service as service
    
    logger.info(f"🟢 recalculate_position_asset {portfolio_id=}, {asset_id=}")
    try:
        async with AsyncSessionLocal() as session:
            await service.recalculate_position_asset(session, portfolio_id, asset_id)
            run_task(set_patrimony_evolution_cache, portfolio_id)
            run_task(set_portfolio_returns_cache, portfolio_id)
    except Exception as e:
        logger.error(f"❌ Erro em recalculate_position_asset: {e}", exc_info=True)
