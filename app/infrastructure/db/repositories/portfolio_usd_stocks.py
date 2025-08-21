
import pandas as pd
from sqlalchemy import or_

from app.infrastructure.db.models.asset import Asset
from app.infrastructure.db.models.asset_stock import Stock
from app.infrastructure.db.models.constants.asset_type import ASSET_TYPE
from app.infrastructure.db.models.constants.currency import CURRENCY
from app.infrastructure.db.repositories.portfolio import PortfolioRepository


class PortfolioUsdStocksRepository(PortfolioRepository):
        
    async def get_position_on_date(
        self, 
        portfolio_id, 
        date=None, 
        asset_type_id=None,
        asset_type_ids=None, 
        currency_id=None):
        
        stmt = await self._build_portfolio_position_query(portfolio_id, date)
        
        stmt = (
            stmt.join(Stock, Stock.asset_id == Asset.id, isouter=True)
            .add_columns(
                Stock.country,
                Stock.sector,
                Stock.industry
            )
            .where(
                or_(
                    Asset.asset_type_id == ASSET_TYPE.STOCK,
                    Asset.asset_type_id == ASSET_TYPE.ETF,
                )
            )
            .where(Asset.currency_id == CURRENCY.USD)
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
                'currency',
                'currency_id',
                'dividend',
                'category',
                'type',
                'type_id',
                'class',
                'country',
                'sector',
                'industry',
            ],
        )
        df['dividend'] = df['dividend'].fillna(0).infer_objects(copy=False)
        df['date'] = pd.to_datetime(df['date'])
        return df
        
        
        
        
        
    