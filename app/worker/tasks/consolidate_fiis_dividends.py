import asyncio

import nest_asyncio
from celery import shared_task

from app.config.logger import logger
from app.services.portfolio import portfolio_consolidator_service


@shared_task(name="consolidate_fiis_dividends")
def consolidate_fiis_dividends():
    logger.info("🟢 consolidate_fiis_dividends")

    from app.infrastructure.db.models.portfolio import Portfolio
    from app.infrastructure.db.repositories.portfolio import PortfolioRepository
    from app.infrastructure.db.session import AsyncSessionLocal
    
    async def wrapper():
        async with AsyncSessionLocal() as session:
            repo = PortfolioRepository(session)
            portfolios = await repo.get_all(Portfolio)
            for portfolio in portfolios:
                await portfolio_consolidator_service.consolidate_fii_dividends(session, portfolio.id)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_fiis_dividends: {e}", exc_info=True)
