import asyncio

import nest_asyncio
from celery import shared_task

from app.config.logger import logger


@shared_task(name="consolidate_single_portfolio")
def consolidate_single_portfolio(portfolio_id: int):
    logger.info(f"🟢 consolidate_single_portfolio para {portfolio_id}")

    from app.infrastructure.db.session import AsyncSessionLocal
    from app.services.portfolio import portfolio_consolidator_service

    async def wrapper():
        async with AsyncSessionLocal() as session:
            await portfolio_consolidator_service.consolidate_position_portfolio(session, portfolio_id)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_single_portfolio: {e}", exc_info=True)
