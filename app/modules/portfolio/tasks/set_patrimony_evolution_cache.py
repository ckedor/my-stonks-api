from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task
from app.infra.redis.redis_service import RedisService


@celery_async_task(name="set_patrimony_evolution_cache")
async def set_patrimony_evolution_cache(portfolio_id: int):
    from app.infra.db.session import AsyncSessionLocal
    from app.modules.portfolio.service.portfolio_position_service import (
        PortfolioPositionService,
    )
    
    logger.info(f"🟢 Iniciando set_patrimony_evolution_cache para {portfolio_id}")
    try:
        async with AsyncSessionLocal() as session:
            service = PortfolioPositionService(session)
            patrimony_evolution = await service.compute_patrimony_evolution(portfolio_id)
            cache = RedisService()
            await cache.set_json(f"patrimony_evolution:{portfolio_id}", patrimony_evolution)
    except Exception as e:
        logger.error(f"❌ Erro em set_patrimony_evolution_cache: {e}", exc_info=True)