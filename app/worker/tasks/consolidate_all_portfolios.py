from app.config.logger import logger
from app.worker.task_runner import celery_async_task, run_task
from app.worker.tasks.consolidate_single_portfolio import consolidate_single_portfolio
from app.worker.tasks.set_patrimony_evolution_cache import set_patrimony_evolution_cache
from app.worker.tasks.set_portfolio_returns_cache import set_portfolio_returns_cache


@celery_async_task(name="consolidate_all_portfolios")
async def consolidate_all_portfolios():
    from app.infrastructure.db.models.portfolio import Portfolio
    from app.infrastructure.db.repositories.base_repository import DatabaseRepository
    from app.infrastructure.db.session import AsyncSessionLocal
    logger.info("🟢 consolidate_all_portfolios")
    try:
        async with AsyncSessionLocal() as session:
            repo = DatabaseRepository(session)
            portfolios = await repo.get_all(Portfolio)
            for portfolio in portfolios:
                run_task(consolidate_single_portfolio, portfolio.id)
                run_task(set_patrimony_evolution_cache, portfolio.id)
                run_task(set_portfolio_returns_cache, portfolio.id)
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_all_portfolios: {e}", exc_info=True)
