from app.api.market_data.schemas import MarketIndexesTimeSeries
from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task


@celery_async_task(name="set_indexes_history_cache")
async def set_indexes_history_cache():
    import app.services.market_data as market_data_service
    from app.infra.db.session import AsyncSessionLocal
    from app.services.cache_service import CacheService
    
    logger.info("🟢 Iniciando set_indexes_history_cache")
    try:
        async with AsyncSessionLocal() as session:
            indexes_history = await market_data_service.compute_indexes_history(session)
            serialized = MarketIndexesTimeSeries(**indexes_history).model_dump(mode='json')
            cache = CacheService()
            await cache.set_market_indexes_history(serialized)
    except Exception as e:
        logger.error(f"❌ Erro em set_indexes_history_cache: {e}", exc_info=True)