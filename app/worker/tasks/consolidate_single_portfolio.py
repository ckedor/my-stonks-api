from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task


@celery_async_task(name="consolidate_single_portfolio")
async def consolidate_single_portfolio(portfolio_id: int):
    from app.infra.db.session import AsyncSessionLocal
    from app.services.portfolio import portfolio_consolidator_service
    
    logger.info(f"🟢 consolidate_single_portfolio para {portfolio_id}")
    try:
        async with AsyncSessionLocal() as session:
            await portfolio_consolidator_service.consolidate_position_portfolio(session, portfolio_id)
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_single_portfolio: {e}", exc_info=True)
