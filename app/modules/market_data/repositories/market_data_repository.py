# app/modules/market_data/repositories/market_data_repository.py
"""
Market data repository - handles database operations for indexes and their history.
"""

import pandas as pd
from sqlalchemy import select

from app.infra.db.models.market_data import Index, IndexHistory
from app.infra.db.repositories.base_repository import DatabaseRepository


class MarketDataRepository(DatabaseRepository):
    """Repository for market data operations"""
    
    async def get_index_history_df(
        self,
        start_date: str = None,
    ) -> pd.DataFrame:
        """
        Get index history as DataFrame.
        Joins Index and IndexHistory tables to include index metadata.
        """
        stmt = select(
            IndexHistory.date,
            IndexHistory.close.label('value'),
            Index.symbol.label('index_symbol'),
            Index.short_name.label('index_name'),
        ).join(Index, IndexHistory.index_id == Index.id)

        if start_date:
            stmt = stmt.where(IndexHistory.date >= start_date)

        result = await self.session.execute(stmt)
        rows = result.all()

        df = pd.DataFrame(rows, columns=['date', 'value', 'index_symbol', 'index_name'])
        df['date'] = pd.to_datetime(df['date'])

        return df
