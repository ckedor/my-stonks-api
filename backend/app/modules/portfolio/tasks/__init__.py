# app/modules/portfolio/tasks/__init__.py
"""
Portfolio Celery tasks.
Tasks are auto-discovered by importing this module.
"""

from app.modules.portfolio.tasks.consolidate_all_portfolios import (
    consolidate_all_portfolios,
)
from app.modules.portfolio.tasks.consolidate_fiis_dividends import (
    consolidate_fiis_dividends,
)
from app.modules.portfolio.tasks.consolidate_single_portfolio import (
    consolidate_single_portfolio,
)
from app.modules.portfolio.tasks.recalculate_asset_position import (
    recalculate_position_asset,
)
from app.modules.portfolio.tasks.set_patrimony_evolution_cache import (
    set_patrimony_evolution_cache,
)
from app.modules.portfolio.tasks.set_portfolio_returns_cache import (
    set_portfolio_returns_cache,
)

__all__ = [
    'consolidate_all_portfolios',
    'consolidate_fiis_dividends',
    'consolidate_single_portfolio',
    'recalculate_position_asset',
    'set_patrimony_evolution_cache',
    'set_portfolio_returns_cache',
]
