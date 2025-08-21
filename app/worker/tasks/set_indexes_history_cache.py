import asyncio

import nest_asyncio
from celery import shared_task

import app.services.market_data as market_data_service
from app.api.market_data.schemas import MarketIndexesTimeSeries
from app.config.logger import logger


@shared_task(name="set_indexes_history_cache")
def set_indexes_history_cache():
    logger.info(f"🟢 Iniciando set_indexes_history_cache")
    from app.infrastructure.db.session import AsyncSessionLocal
    from app.services.cache_service import CacheService

    async def wrapper():
        async with AsyncSessionLocal() as session:
            cache = CacheService()
            indexes_history = await market_data_service.compute_indexes_history(session)
            serialized = MarketIndexesTimeSeries(**indexes_history).model_dump(mode='json')
            await cache.set_market_indexes_history(serialized)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em set_indexes_history_cache: {e}", exc_info=True)