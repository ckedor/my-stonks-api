from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task, run_task
from app.worker.tasks.set_indexes_history_cache import set_indexes_history_cache


@celery_async_task(name="consolidate_indexes_history")
async def consolidate_indexes_history():
    from app.infra.db.session import AsyncSessionLocal
    from app.services import market_data
    logger.info("🟢 consolidate_indexes_history")
    try:
        async with AsyncSessionLocal() as session:
            await market_data.consolidate_market_indexes_history(session)
            run_task(set_indexes_history_cache)
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_indexes_history: {e}", exc_info=True)
