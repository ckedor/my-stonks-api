import asyncio

import nest_asyncio
from celery import shared_task

from app.config.logger import logger
from app.services.portfolio import portfolio_position_service


@shared_task(name="set_patrimony_evolution_cache")
def set_patrimony_evolution_cache(portfolio_id: int):
    logger.info(f"🟢 Iniciando set_patrimony_evolution_cache para {portfolio_id}")
    from app.infrastructure.db.session import AsyncSessionLocal
    from app.services.cache_service import CacheService

    async def wrapper():
        async with AsyncSessionLocal() as session:
            cache = CacheService()
            patrimony_evolution = await portfolio_position_service.get_patrimony_evolution(session, portfolio_id)
            await cache.set_patrimony_evolution_cache(patrimony_evolution, portfolio_id)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em set_patrimony_evolution_cache: {e}", exc_info=True)