import asyncio

import nest_asyncio
from celery import shared_task

from app.config.logger import logger
from app.services.portfolio import portfolio_position_service


@shared_task(name="set_portfolio_returns_cache")
def set_portfolio_returns_cache(portfolio_id):
    logger.info(f"🟢 Iniciando set_portfolio_returns_cache")
    from app.infrastructure.db.session import AsyncSessionLocal
    from app.services.cache_service import CacheService

    async def wrapper():
        async with AsyncSessionLocal() as session:
            portfolio_returns = await portfolio_position_service.get_portfolio_returns(session, portfolio_id)
            cache = CacheService()
            await cache.set_portfolio_returns(portfolio_returns, portfolio_id)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em set_portfolio_returns_cache: {e}", exc_info=True)