import asyncio

import nest_asyncio
from celery import shared_task

from app.config.logger import logger
from app.modules.portfolio.service.portfolio_consolidator_service import (
    PortfolioConsolidatorService,
)


@shared_task(name="consolidate_fiis_dividends")
def consolidate_fiis_dividends():
    logger.info("🟢 consolidate_fiis_dividends")

    from app.infra.db.models.portfolio import Portfolio
    from app.infra.db.session import AsyncSessionLocal
    from app.modules.portfolio.repositories import PortfolioRepository
    
    async def wrapper():
        async with AsyncSessionLocal() as session:
            repo = PortfolioRepository(session)
            portfolios = await repo.get_all(Portfolio)
            for portfolio in portfolios:
                service = PortfolioConsolidatorService(session)
                await service.consolidate_fii_dividends(portfolio.id)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_fiis_dividends: {e}", exc_info=True)
