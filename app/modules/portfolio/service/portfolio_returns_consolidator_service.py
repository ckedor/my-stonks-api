# app/modules/portfolio/service/portfolio_returns_consolidator_service.py
"""
Service to consolidate portfolio and category returns into the database.
"""

import pandas as pd

from app.config.logger import logger
from app.domain.finance.performance_metrics import cagr
from app.infra.db.models.portfolio import (
    CategoryReturn,
    CustomCategory,
    CustomCategoryAssignment,
    PortfolioReturn,
)
from app.modules.portfolio.domain.returns import (
    calculate_category_acc_return,
    calculate_portfolio_acc_return,
    calculate_portfolio_daily_returns,
)
from app.modules.portfolio.repositories import PortfolioRepository


class PortfolioReturnsConsolidatorService:
    def __init__(self, session):
        self.session = session
        self.repo = PortfolioRepository(session)

    async def consolidate_returns(self, portfolio_id: int):
        logger.info(f"Consolidando retornos do portfolio {portfolio_id}")

        portfolio_position_df = await self.repo.get_portfolio_position_df(portfolio_id)

        if portfolio_position_df.empty:
            logger.warning(f"Sem posições para portfolio {portfolio_id}")
            return

        pos_df = calculate_portfolio_daily_returns(portfolio_position_df)

        await self._consolidate_portfolio_returns(pos_df, portfolio_id)
        await self._consolidate_category_returns(pos_df, portfolio_id)

        await self.session.commit()
        logger.info(f"Retornos consolidados com sucesso para portfolio {portfolio_id}")

    async def consolidate_category_returns(self, portfolio_id: int):
        logger.info(f"Consolidando retornos das categorias do portfolio {portfolio_id}")

        portfolio_position_df = await self.repo.get_portfolio_position_df(portfolio_id)

        if portfolio_position_df.empty:
            logger.warning(f"Sem posições para portfolio {portfolio_id}")
            return

        pos_df = calculate_portfolio_daily_returns(portfolio_position_df)
        await self._consolidate_category_returns(pos_df, portfolio_id)

        await self.session.commit()
        logger.info(f"Retornos das categorias consolidados para portfolio {portfolio_id}")

    async def _consolidate_portfolio_returns(self, pos_df: pd.DataFrame, portfolio_id: int):
        df = pos_df.copy()
        df['weighted_return'] = (df['value'] / df['net_value_day']) * df['asset_return']
        grouped = df.groupby('date')['weighted_return'].sum().reset_index()
        grouped.rename(columns={'weighted_return': 'daily_return'}, inplace=True)
        grouped['acc_return'] = (1 + grouped['daily_return']).cumprod() - 1

        # Calculate CAGR for each date
        grouped['cagr'] = None
        returns_series = grouped.set_index('date')['daily_return']
        for i in range(1, len(grouped)):
            partial = returns_series.iloc[:i + 1]
            if len(partial) >= 2:
                grouped.loc[grouped.index[i], 'cagr'] = cagr(partial)

        grouped['portfolio_id'] = portfolio_id
        grouped['date'] = grouped['date'].dt.date

        records = grouped[PortfolioReturn.COLUMNS].to_dict(orient='records')
        await self.repo.upsert_bulk(
            PortfolioReturn, records, unique_columns=['portfolio_id', 'date']
        )

    async def _consolidate_category_returns(self, pos_df: pd.DataFrame, portfolio_id: int):
        # Build category name -> id mapping
        categories = await self.repo.get(
            CustomCategory, by={'portfolio_id': portfolio_id}
        )
        if not categories:
            return

        cat_name_to_id = {cat.name: cat.id for cat in categories}

        df = pos_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['asset_id', 'date'])

        # Calculate category daily returns (same logic as calculate_category_acc_return)
        df['base_value'] = (df['value'] - df['contribution']).replace(0, pd.NA)
        df['base_value_prev'] = df.groupby('asset_id')['base_value'].shift(1)
        df['category_base_prev_total'] = df.groupby(['date', 'category'])[
            'base_value_prev'
        ].transform('sum')

        df['category_weight'] = df['base_value_prev'] / df['category_base_prev_total'].replace(
            0, pd.NA
        )
        df['category_weight'] = pd.to_numeric(df['category_weight'], errors='coerce').fillna(0)
        df['category_weighted_return'] = df['category_weight'] * df['asset_return']

        daily = df.groupby(['date', 'category'])['category_weighted_return'].sum().reset_index()
        daily.rename(columns={'category_weighted_return': 'daily_return'}, inplace=True)

        all_records = []
        for cat_name, cat_df in daily.groupby('category'):
            cat_id = cat_name_to_id.get(cat_name)
            if cat_id is None:
                continue

            cat_df = cat_df.sort_values('date').reset_index(drop=True)
            cat_df['acc_return'] = (1 + cat_df['daily_return']).cumprod() - 1

            # Calculate CAGR for each date
            cat_df['cagr'] = None
            returns_series = cat_df.set_index('date')['daily_return']
            for i in range(1, len(cat_df)):
                partial = returns_series.iloc[:i + 1]
                if len(partial) >= 2:
                    cat_df.loc[cat_df.index[i], 'cagr'] = cagr(partial)

            cat_df['portfolio_id'] = portfolio_id
            cat_df['custom_category_id'] = cat_id
            cat_df['date'] = cat_df['date'].dt.date

            all_records.extend(cat_df[CategoryReturn.COLUMNS].to_dict(orient='records'))

        if all_records:
            await self.repo.upsert_bulk(
                CategoryReturn,
                all_records,
                unique_columns=['portfolio_id', 'custom_category_id', 'date'],
            )
