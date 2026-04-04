
import pandas as pd

from app.infra.db.models.asset import Asset
from app.infra.db.models.asset_fii import FII, FIISegment, FIIType
from app.infra.db.models.asset_fixed_income import FixedIncome, FixedIncomeType
from app.infra.db.models.asset_treasury_bond import TreasuryBond, TreasuryBondType
from app.infra.db.models.constants.asset_type import ASSET_TYPE
from app.infra.db.models.market_data import Index
from app.modules.portfolio.repositories.portfolio_repository import PortfolioRepository


class PortfolioFixedIncomeRepository(PortfolioRepository):
    async def get_position_on_date(self, 
        portfolio_id, 
        date=None, 
        asset_type_id=None, 
        asset_type_ids=None
        ):
        stmt = await self._build_portfolio_position_query(portfolio_id, date)
        
        stmt = stmt.where(Asset.asset_type_id.in_([ASSET_TYPE.TREASURY, ASSET_TYPE.CDB, ASSET_TYPE.DEB, ASSET_TYPE.CRI, ASSET_TYPE.CRA, ASSET_TYPE.LCA]))
        
        stmt = (
            stmt.join(FixedIncome, FixedIncome.asset_id == Asset.id, isouter=True)
            .join(FixedIncomeType, FixedIncomeType.id == FixedIncome.fixed_income_type_id, isouter=True)
            .join(Index, Index.id == FixedIncome.index_id, isouter=True)
            .join(TreasuryBond, TreasuryBond.asset_id == Asset.id, isouter=True)
            .join(TreasuryBondType, TreasuryBondType.id == TreasuryBond.type_id, isouter=True)
            .add_columns(
                FixedIncome.maturity_date.label("fixed_income_maturity_date"),
                FixedIncome.fee.label("fixed_income_fee"),
                Index.short_name.label("fixed_income_index_name"),
                FixedIncomeType.name.label("fixed_income_type"),
                TreasuryBond.maturity_date.label("treasury_bond_maturity_date"),
                TreasuryBondType.name.label("treasury_bond_type"),
                TreasuryBondType.code.label("treasury_bond_code"),
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
                'fixed_income_maturity_date',
                'fixed_income_fee',
                'fixed_income_index_name',
                'fixed_income_type',
                'treasury_bond_maturity_date',
                'treasury_bond_type',
                'treasury_bond_code'
            ],
        )
        df['dividend'] = df['dividend'].fillna(0).infer_objects(copy=False)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = df['quantity'] * df['price']
        df = df.sort_values(by='value', ascending=False)
        return df
        
        
        
        
        
    