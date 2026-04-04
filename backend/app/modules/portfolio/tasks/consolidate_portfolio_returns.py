from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task


@celery_async_task(name="consolidate_portfolio_returns")
async def consolidate_portfolio_returns(portfolio_id: int):
    from app.infra.db.session import AsyncSessionLocal
    from app.modules.portfolio.service.portfolio_returns_consolidator_service import (
        PortfolioReturnsConsolidatorService,
    )

    logger.info(f"🟢 consolidate_portfolio_returns para {portfolio_id}")
    try:
        async with AsyncSessionLocal() as session:
            service = PortfolioReturnsConsolidatorService(session)
            await service.consolidate_returns(portfolio_id)
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_portfolio_returns: {e}", exc_info=True)
