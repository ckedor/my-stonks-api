# app/modules/market_data/tasks/__init__.py
"""
Market data Celery tasks.
Tasks are auto-discovered by importing this module.
"""

from app.modules.market_data.tasks.consolidate_indexes_history import (
    consolidate_indexes_history,
)
from app.modules.market_data.tasks.set_indexes_history_cache import (
    set_indexes_history_cache,
)

__all__ = [
    'consolidate_indexes_history',
    'set_indexes_history_cache',
]
