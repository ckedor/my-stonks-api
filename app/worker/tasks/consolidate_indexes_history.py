import asyncio

import nest_asyncio
from celery import shared_task

from app.config.logger import logger
from app.services import market_data
from app.worker.task_runner import run_task
from app.worker.tasks.set_indexes_history_cache import set_indexes_history_cache


@shared_task(name="consolidate_indexes_history")
def consolidate_indexes_history():
    logger.info("🟢 consolidate_indexes_history")

    from app.infrastructure.db.session import AsyncSessionLocal
    async def wrapper():
        async with AsyncSessionLocal() as session:
            await market_data.consolidate_market_indexes_history(session)
            run_task(set_indexes_history_cache)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_indexes_history: {e}", exc_info=True)
