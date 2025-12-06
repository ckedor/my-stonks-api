from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task
from app.infra.db.session import AsyncSessionLocal


@celery_async_task(name="set_portfolio_returns_cache")
async def set_portfolio_returns_cache(portfolio_id: int):
    from app.services.cache_service import CacheService
    from app.services.portfolio import portfolio_position_service
    
    logger.info(f"🟢 Iniciando set_portfolio_returns_cache para {portfolio_id}")
    try:
        async with AsyncSessionLocal() as session:
            portfolio_returns = await portfolio_position_service.get_portfolio_returns(session, portfolio_id)
            cache = CacheService()
            await cache.set_portfolio_returns(portfolio_returns, portfolio_id)
    except Exception as e:
        logger.error(f"❌ Erro em set_portfolio_returns_cache: {e}", exc_info=True)