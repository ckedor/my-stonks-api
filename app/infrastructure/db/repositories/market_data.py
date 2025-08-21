import pandas as pd
from sqlalchemy import select

from app.infrastructure.db.models.market_data import Index, IndexHistory
from app.infrastructure.db.repositories.base_repository import DatabaseRepository


class MarketDataRepository(DatabaseRepository):
    async def get_index_history_df(
        self,
        start_date: str = None,
    ) -> pd.DataFrame:
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
