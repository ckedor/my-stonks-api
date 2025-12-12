# app/modules/market_data/tasks/consolidate_indexes_history.py
"""
Celery task to consolidate market indexes from external providers.
"""

from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task, run_task
from app.infra.db.session import AsyncSessionLocal
from app.modules.market_data.service.market_data_service import MarketDataService
from app.modules.market_data.tasks.set_indexes_history_cache import (
    set_indexes_history_cache,
)


@celery_async_task(name="consolidate_indexes_history")
async def consolidate_indexes_history():
    """
    Fetch latest market index data from external providers and update database.
    After consolidation, triggers cache update task.
    """
    logger.info("🟢 consolidate_indexes_history")
    try:
        async with AsyncSessionLocal() as session:
            service = MarketDataService(session)
            await service.consolidate_market_indexes_history()
            run_task(set_indexes_history_cache)
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_indexes_history: {e}", exc_info=True)
