from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task
from app.infra.db.session import AsyncSessionLocal
from app.infra.redis.redis_service import RedisService


@celery_async_task(name="set_portfolio_returns_cache")
async def set_portfolio_returns_cache(portfolio_id: int):
    from app.modules.portfolio.service.portfolio_position_service import (
        PortfolioPositionService,
    )
    
    logger.info(f"🟢 Iniciando set_portfolio_returns_cache para {portfolio_id}")
    try:
        async with AsyncSessionLocal() as session:
            service = PortfolioPositionService(session)
            portfolio_returns = await service.compute_portfolio_returns(portfolio_id)
            cache = RedisService()
            await cache.set_json(f"portfolio_returns:{portfolio_id}", portfolio_returns)
    except Exception as e:
        logger.error(f"❌ Erro em set_portfolio_returns_cache: {e}", exc_info=True)