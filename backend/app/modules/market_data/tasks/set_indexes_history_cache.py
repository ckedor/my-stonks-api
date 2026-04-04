# app/modules/market_data/tasks/set_indexes_history_cache.py
"""
Celery task to compute and cache market indexes history.
"""

from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task
from app.infra.db.session import AsyncSessionLocal
from app.infra.redis.redis_service import RedisService
from app.modules.market_data.service.market_data_service import MarketDataService


@celery_async_task(name="set_indexes_history_cache")
async def set_indexes_history_cache():
    """
    Compute market indexes historical returns and store in cache.
    This task is triggered after index consolidation.
    """
    logger.info("🟢 Iniciando set_indexes_history_cache")
    try:
        async with AsyncSessionLocal() as session:
            service = MarketDataService(session)
            indexes_history = await service.compute_indexes_history()
            cache = RedisService()
            await cache.set_json("indexes_history", indexes_history)
    except Exception as e:
        logger.error(f"❌ Erro em set_indexes_history_cache: {e}", exc_info=True)
