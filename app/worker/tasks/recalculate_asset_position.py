import asyncio

import nest_asyncio
from celery import shared_task

from app.config.logger import logger
from app.services.portfolio import portfolio_consolidator_service as service
from app.worker.task_runner import run_task
from app.worker.tasks.set_patrimony_evolution_cache import set_patrimony_evolution_cache
from app.worker.tasks.set_portfolio_returns_cache import set_portfolio_returns_cache


@shared_task(name="recalculate_asset_position")
def recalculate_position_asset(portfolio_id: int, asset_id: int):
    logger.info(f"🟢 recalculate_position_asset {portfolio_id=}, {asset_id=}")

    from app.infrastructure.db.session import AsyncSessionLocal

    async def wrapper():
        async with AsyncSessionLocal() as session:
            await service.recalculate_position_asset(session, portfolio_id, asset_id)
            run_task(set_patrimony_evolution_cache, portfolio_id)
            run_task(set_portfolio_returns_cache, portfolio_id)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em recalculate_position_asset: {e}", exc_info=True)
