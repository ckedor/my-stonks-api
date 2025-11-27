from app.config.logger import logger
from app.worker.task_runner import celery_async_task


@celery_async_task(name="set_patrimony_evolution_cache")
async def set_patrimony_evolution_cache(portfolio_id: int):
    from app.infrastructure.db.session import AsyncSessionLocal
    from app.services.cache_service import CacheService
    from app.services.portfolio import portfolio_position_service
    
    logger.info(f"🟢 Iniciando set_patrimony_evolution_cache para {portfolio_id}")
    try:
        async with AsyncSessionLocal() as session:
            patrimony_evolution = await portfolio_position_service.get_patrimony_evolution(session, portfolio_id)
            cache = CacheService()
            await cache.set_patrimony_evolution_cache(patrimony_evolution, portfolio_id)
    except Exception as e:
        logger.error(f"❌ Erro em set_patrimony_evolution_cache: {e}", exc_info=True)