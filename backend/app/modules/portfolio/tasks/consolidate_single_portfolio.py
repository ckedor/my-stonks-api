from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task


@celery_async_task(name="consolidate_single_portfolio")
async def consolidate_single_portfolio(portfolio_id: int):
    from app.infra.db.session import AsyncSessionLocal
    from app.modules.portfolio.service.portfolio_consolidator_service import (
        PortfolioConsolidatorService,
    )
    
    logger.info(f"🟢 consolidate_single_portfolio para {portfolio_id}")
    try:
        async with AsyncSessionLocal() as session:
            service = PortfolioConsolidatorService(session)
            await service.consolidate_position_portfolio(portfolio_id)
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_single_portfolio: {e}", exc_info=True)
