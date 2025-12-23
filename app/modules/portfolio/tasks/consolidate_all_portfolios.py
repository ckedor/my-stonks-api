from app.config.logger import logger
from app.entrypoints.worker.task_runner import celery_async_task, run_task
from app.modules.portfolio.tasks.consolidate_single_portfolio import (
    consolidate_single_portfolio,
)
from app.modules.portfolio.tasks.set_patrimony_evolution_cache import (
    set_patrimony_evolution_cache,
)
from app.modules.portfolio.tasks.set_portfolio_returns_cache import (
    set_portfolio_returns_cache,
)


@celery_async_task(name="consolidate_all_portfolios")
async def consolidate_all_portfolios():
    from app.infra.db.models.portfolio import Portfolio
    from app.infra.db.repositories.base_repository import SQLAlchemyRepository
    from app.infra.db.session import AsyncSessionLocal
    logger.info("🟢 consolidate_all_portfolios")
    try:
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyRepository(session)
            portfolios = await repo.get_all(Portfolio)
            for portfolio in portfolios:
                run_task(consolidate_single_portfolio, portfolio.id)
                run_task(set_patrimony_evolution_cache, portfolio.id)
                run_task(set_portfolio_returns_cache, portfolio.id)
    except Exception as e:
        logger.error(f"❌ Erro em consolidate_all_portfolios: {e}", exc_info=True)
