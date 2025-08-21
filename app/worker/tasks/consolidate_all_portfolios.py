import asyncio

import nest_asyncio
from celery import shared_task

from app.config.logger import logger
from app.worker.task_runner import run_task
from app.worker.tasks.set_portfolio_returns_cache import set_portfolio_returns_cache


@shared_task(name="consolidate_all_portfolios")
def consolidate_all_portfolios():
    logger.info("🟢 consolidate_all_portfolios")

    from app.infrastructure.db.models.portfolio import Portfolio
    from app.infrastructure.db.repositories.base_repository import DatabaseRepository
    from app.infrastructure.db.session import AsyncSessionLocal
    from app.worker.tasks.consolidate_single_portfolio import (
        consolidate_single_portfolio,
    )
    from app.worker.tasks.set_patrimony_evolution_cache import (
        set_patrimony_evolution_cache,
    )

    async def wrapper():
        async with AsyncSessionLocal() as session:
            repo = DatabaseRepository(session)
            portfolios = await repo.get_all(Portfolio)
            for portfolio in portfolios:
                run_task(consolidate_single_portfolio, portfolio.id)
                run_task(set_patrimony_evolution_cache, portfolio.id)
                run_task(set_portfolio_returns_cache, portfolio.id)

    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wrapper())
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_all_portfolios: {e}", exc_info=True)
