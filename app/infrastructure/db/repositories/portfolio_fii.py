
import pandas as pd

from app.infrastructure.db.models.asset import Asset
from app.infrastructure.db.models.asset_fii import FII, FIISegment, FIIType
from app.infrastructure.db.repositories.portfolio import PortfolioRepository


class PortfolioFiiRepository(PortfolioRepository):
        
    async def get_position_on_date(self, 
        portfolio_id, 
        date=None, 
        asset_type_id=None, 
        asset_type_ids=None):
        stmt = await self._build_portfolio_position_query(portfolio_id, date)
        
        stmt = (
            stmt.join(FII, FII.asset_id == Asset.id)
            .join(FIISegment, FIISegment.id == FII.segment_id)
            .join(FIIType, FIIType.id == FIISegment.type_id)
            .add_columns(
                FIISegment.name.label("fii_segment"),
                FIIType.name.label("fii_type"),
            )
        )
        
        result = await self.session.execute(stmt)
        df = pd.DataFrame(
            result.all(),
            columns=[
                'date',
                'asset_id',
                'ticker',
                'name',
                'quantity',
                'price',
                'twelve_months_return',
                'acc_return',
                'daily_return',
                'dividend',
                'category',
                'type',
                'type_id',
                'class',
                'fii_segment',
                'fii_type',
            ],
        )
        df['dividend'] = df['dividend'].fillna(0).infer_objects(copy=False)
        df['date'] = pd.to_datetime(df['date'])
        return df
        
        
        
        
        
    