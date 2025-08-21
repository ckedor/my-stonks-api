from typing import List, Optional

import pandas as pd
from sqlalchemy import and_, func, select
from sqlalchemy.orm import joinedload

from app.infrastructure.db.models.asset import Asset, AssetClass, AssetType, Currency
from app.infrastructure.db.models.asset_etf import ETF
from app.infrastructure.db.models.asset_fii import FII, FIISegment
from app.infrastructure.db.models.asset_fixed_income import FixedIncome
from app.infrastructure.db.models.asset_treasury_bond import TreasuryBond
from app.infrastructure.db.models.market_data import Index
from app.infrastructure.db.models.portfolio import (
    Broker,
    CustomCategory,
    CustomCategoryAssignment,
    Dividend,
    Portfolio,
    Position,
    Transaction,
)
from app.infrastructure.db.repositories.base_repository import DatabaseRepository


def get_custom_category_subquery(portfolio_id):
    return (
        select(CustomCategoryAssignment.asset_id, CustomCategory.name.label('category'))
        .join(CustomCategory, CustomCategory.id == CustomCategoryAssignment.custom_category_id)
        .where(CustomCategory.portfolio_id == portfolio_id)
        .subquery()
    )


class PortfolioRepository(DatabaseRepository):
    async def get_asset_details(self, asset_id: int):
        stmt = (
            select(Asset)
            .options(
                joinedload(Asset.asset_type).joinedload(AssetType.asset_class),
                joinedload(Asset.currency),
                joinedload(Asset.stock),
                joinedload(Asset.fii).joinedload(FII.segment).joinedload(FIISegment.type),
                joinedload(Asset.etf).joinedload(ETF.segment),
                joinedload(Asset.fund),
                joinedload(Asset.fixed_income)
                .joinedload(FixedIncome.index)
                .joinedload(Index.currency),
                joinedload(Asset.fixed_income).joinedload(FixedIncome.fixed_income_type),
                joinedload(Asset.treasury_bond).joinedload(TreasuryBond.type),
            )
            .where(Asset.id == asset_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_portfolios(self, user_id: int):
        stmt = (
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .options(joinedload(Portfolio.custom_categories))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_transactions_df(
        self,
        portfolio_id: int,
        asset_id: Optional[int] = None,
        asset_types_ids: Optional[List[int]] = None,
        currency_id: Optional[int] = None,
    ) -> pd.DataFrame:
        cat_assignment_subq = get_custom_category_subquery(portfolio_id)

        stmt = (
            select(
                Transaction.id,
                Transaction.date,
                Transaction.quantity,
                Broker.id.label('broker_id'),
                Broker.name.label('broker'),
                Broker.currency_id.label('currency_id'),
                Transaction.price,
                Asset.id.label('asset_id'),
                Asset.ticker,
                cat_assignment_subq.c.category,
            )
            .join(Asset, Transaction.asset_id == Asset.id)
            .join(Broker, Transaction.broker_id == Broker.id)
            .outerjoin(cat_assignment_subq, cat_assignment_subq.c.asset_id == Asset.id)
            .where(Transaction.portfolio_id == portfolio_id)
            .order_by(Transaction.date)
        )

        if asset_types_ids:
            stmt = stmt.where(Asset.asset_type_id.in_(asset_types_ids))
        elif asset_id:
            stmt = stmt.where(Transaction.asset_id == asset_id)

        result = await self.session.execute(stmt)
        rows = result.all()
        df = pd.DataFrame(
            rows,
            columns=[
                'id',
                'date',
                'quantity',
                'broker_id',
                'broker',
                'currency_id',
                'price',
                'asset_id',
                'ticker',
                'category',
            ],
        )
        df['date'] = pd.to_datetime(df['date'])
        df['quantity'] = df['quantity'].astype(float)
        df['price'] = df['price'].astype(float)
        return df

    async def get_portfolio_dividends(
        self, portfolio_id: int, filters
    ) -> pd.DataFrame:
        cat_assignment_subq = get_custom_category_subquery(portfolio_id)

        stmt = (
            select(
                Dividend.id,
                Dividend.date,
                Dividend.asset_id,
                Asset.ticker,
                Dividend.amount,
                cat_assignment_subq.c.category,
            )
            .join(Asset, Dividend.asset_id == Asset.id)
            .outerjoin(cat_assignment_subq, cat_assignment_subq.c.asset_id == Asset.id)
            .where(Dividend.portfolio_id == portfolio_id)
        )

        if filters.start_date:
            stmt = stmt.where(Dividend.date >= filters.start_date)
        if filters.end_date:
            stmt = stmt.where(Dividend.date <= filters.end_date)
        if filters.asset_id:
            stmt = stmt.where(Dividend.asset_id == filters.asset_id)
        if filters.asset_type_ids:
            stmt = stmt.where(Asset.asset_type_id.in_(filters.asset_type_ids))

        result = await self.session.execute(stmt)
        dividends = result.all()

        return dividends

    async def get_asset_position_df(
        self, portfolio_id: int, asset_ids: list[int], start_date=None, end_date=None
    ) -> pd.DataFrame:
        stmt = (
            select(
                Position.date,
                Position.asset_id,
                Asset.ticker,
                Position.quantity,
                Position.price,
                Currency.name.label('currency'),
                Dividend.amount.label('dividend'),
            )
            .join(Asset, Position.asset_id == Asset.id)
            .outerjoin(
                Dividend,
                and_(
                    Dividend.asset_id == Position.asset_id,
                    Dividend.date == Position.date,
                    Dividend.portfolio_id == Position.portfolio_id,
                ),
            )
            .where(Position.portfolio_id == portfolio_id)
            .where(Position.asset_id.in_(asset_ids))
        )

        if start_date:
            stmt = stmt.where(Position.date >= start_date)
        if end_date:
            stmt = stmt.where(Position.date <= end_date)

        result = await self.session.execute(stmt)
        df = pd.DataFrame(
            result.all(),
            columns=['date', 'asset_id', 'ticker', 'quantity', 'price', 'currency', 'dividend'],
        )
        df['dividend'] = df['dividend'].fillna(0).infer_objects(copy=False)
        df['date'] = pd.to_datetime(df['date'])
        return df

    async def get_portfolio_position_df(
        self, 
        portfolio_id: int, 
        start_date=None, 
        end_date=None, 
        asset_id=None, 
        asset_type_id=None, 
        asset_type_ids=None, 
        currency_id=None,
        asset_ids: Optional[List[int]] = None
    ) -> pd.DataFrame:
        dividend_subquery = (
            select(
                Dividend.asset_id,
                Dividend.portfolio_id,
                Dividend.date,
                func.sum(Dividend.amount).label('total_dividend'),
            )
            .where(Dividend.portfolio_id == portfolio_id)
            .group_by(Dividend.asset_id, Dividend.portfolio_id, Dividend.date)
            .subquery()
        )

        cat_assignment_subq = get_custom_category_subquery(portfolio_id)

        stmt = (
            select(
                Position.date,
                Position.asset_id,
                Asset.ticker,
                Position.quantity,
                Position.price,
                Position.average_price,
                dividend_subquery.c.total_dividend.label('dividend'),
                cat_assignment_subq.c.category,
            )
            .join(Asset, Position.asset_id == Asset.id)
            .outerjoin(
                dividend_subquery,
                and_(
                    dividend_subquery.c.asset_id == Position.asset_id,
                    dividend_subquery.c.date == Position.date,
                    dividend_subquery.c.portfolio_id == Position.portfolio_id,
                ),
            )
            .outerjoin(cat_assignment_subq, cat_assignment_subq.c.asset_id == Position.asset_id)
            .where(Position.portfolio_id == portfolio_id)
            .order_by(Position.date)
        )

        if start_date:
            stmt = stmt.where(Position.date >= start_date)
        if end_date:
            stmt = stmt.where(Position.date <= end_date)
        if asset_id:
            stmt = stmt.where(Position.asset_id == asset_id)
        if asset_ids:
            stmt = stmt.where(Position.asset_id.in_(asset_ids))
        if asset_type_id:
            stmt = stmt.where(Asset.asset_type_id == asset_type_id)
        if asset_type_ids:
            stmt = stmt.where(Asset.asset_type_id.in_(asset_type_ids))

        result = await self.session.execute(stmt)
        df = pd.DataFrame(
            result.all(),
            columns=[
                'date',
                'asset_id',
                'ticker',
                'quantity',
                'price',
                'average_price',
                'dividend',
                'category',
            ],
        )
        df['dividend'] = df['dividend'].fillna(0).infer_objects(copy=False)
        df['date'] = pd.to_datetime(df['date'])
        return df

    async def get_position_on_date(self, portfolio_id, date=None, asset_type_id=None):
        stmt = await self._build_portfolio_position_query(portfolio_id, date, asset_type_id)

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
            ],
        )
        df['dividend'] = df['dividend'].fillna(0).infer_objects(copy=False)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    async def _build_portfolio_position_query(
        self,
        portfolio_id: int,
        date: pd.Timestamp = None,
        asset_type_id: int = None
    ):

        if date:
            search_date = date
        else:
            search_date = await self._get_portfolio_position_latest_date(portfolio_id)
        
        cat_assignment_subq = get_custom_category_subquery(portfolio_id)
        
        stmt = (
            select(
                Position.date,
                Position.asset_id,
                Asset.ticker,
                Asset.name,
                Position.quantity,
                Position.price,
                Position.twelve_months_return,
                Position.acc_return,
                Position.daily_return,
                Dividend.amount.label('dividend'),
                cat_assignment_subq.c.category,
                AssetType.short_name.label('type'),
                AssetType.id.label('type_id'),
                AssetClass.name.label('class'),
            )
            .join(Asset, Position.asset_id == Asset.id)
            .outerjoin(cat_assignment_subq, cat_assignment_subq.c.asset_id == Position.asset_id)
            .join(AssetType, Asset.asset_type_id == AssetType.id)
            .join(AssetClass, AssetType.asset_class_id == AssetClass.id)
            .outerjoin(
                Dividend,
                and_(
                    Dividend.asset_id == Position.asset_id,
                    Dividend.date == Position.date,
                    Dividend.portfolio_id == Position.portfolio_id,
                ),
            )
            .where(Position.portfolio_id == portfolio_id)
            .where(Position.date == search_date)
            .order_by(Position.date)
        )
        
        if asset_type_id:
            stmt = stmt.where(Asset.asset_type_id == asset_type_id)
        
        return stmt
        
    async def _get_portfolio_position_latest_date(
        self,
        portfolio_id: int):
        
        latest_date_stmt = select(func.max(Position.date)).where(
            Position.portfolio_id == portfolio_id
        )
        latest_date_result = await self.session.execute(latest_date_stmt)
        latest_date = latest_date_result.scalar_one_or_none()

        if not latest_date:
            return None

        return pd.to_datetime(latest_date)
    
    async def get_assets_from_current_position(
        self, portfolio_id: int
    ) -> List[int]:
        
        stmt = (
            select(Asset.ticker)
            .join(Position, Position.asset_id == Asset.id)
            .where(
                Position.date == select(func.max(Position.date))
                .where(Position.portfolio_id == portfolio_id)
                .scalar_subquery()
            )
            .where(Position.portfolio_id == portfolio_id)
            .distinct()
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all() if row[0] is not None]
