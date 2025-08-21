from datetime import datetime

import numpy as np
import pandas as pd

from app.infrastructure.db.models.asset import Asset
from app.infrastructure.db.models.asset_fixed_income import FixedIncome
from app.infrastructure.db.models.constants.asset_fixed_income_type import (
    ASSET_FIXED_INCOME_TYPE,
)
from app.infrastructure.db.models.market_data import IndexHistory
from app.infrastructure.db.models.portfolio import Dividend
from app.infrastructure.db.repositories.base_repository import DatabaseRepository


## TODO: O FixedIncomeCalculator não deve depender do DatabaseRepository. Além disso deve ser movida a logica de negócio pra funcção pura em finanças
class FixedIncomeCalculator:
    def __init__(self, repo: DatabaseRepository):
        self.repo = repo

    async def calculate_asset_prices(
        self, asset: Asset, portfolio_id: int, transactions_df: pd.DataFrame
    ):
        fixed_income = await self.repo.get(FixedIncome, by={'asset_id': asset.id}, first=True)

        fee = fixed_income.fee
        index = fixed_income.index
        type_id = fixed_income.fixed_income_type_id

        index_history_df = await self.repo.get(IndexHistory, by={'index_id': index.id}, as_df=True)

        if index_history_df.empty:
            raise ValueError(f'Não existe dados de histórico do índice {index.short_name}')

        pos_df = self._merge_index_history_and_transactions(transactions_df, index_history_df)
        pos_df = pos_df[['date', 'transaction_price_brl', 'quantity', 'close']]

        pos_df['dividend'] = 0

        dividends_df = await self.repo.get(
            Dividend,
            by={'portfolio_id': portfolio_id, 'asset_id': asset.id},
            as_df=True,
        )
        if not dividends_df.empty:
            pos_df = pd.merge(pos_df, dividends_df, on=['date'], how='left')
            pos_df['dividend'] = pos_df['amount'].fillna(0)

        if type_id == ASSET_FIXED_INCOME_TYPE.FIXED_RATE:
            raise Exception('Non implemented')

        elif type_id == ASSET_FIXED_INCOME_TYPE.INDEX_PLUS:
            return await self._get_prices_fixed_income(1, fee, pos_df)

        elif type_id == ASSET_FIXED_INCOME_TYPE.PERC_INDEX:
            return await self._get_prices_fixed_income(fee, 0, pos_df)

    @staticmethod
    def _merge_index_history_and_transactions(transaction_df, index_history_df):
        transaction_df['date'] = pd.to_datetime(transaction_df['date'])

        init_date = transaction_df['date'].min()
        final_date = datetime.today()

        all_dates = pd.date_range(start=init_date, end=final_date, freq='D')
        pos_df = pd.DataFrame(all_dates, columns=['date'])

        pos_df = pd.merge(
            pos_df,
            transaction_df[['date', 'quantity', 'transaction_price_brl']],
            on='date',
            how='left',
        )
        pos_df['quantity'] = pos_df['quantity'].fillna(0)
        pos_df['quantity'] = pos_df['quantity'].cumsum()
        pos_df = pos_df[pos_df['quantity'] > 0]

        pos_df = pd.merge(
            pos_df.sort_values('date'),
            index_history_df.sort_values('date'),
            on='date',
            how='left',
        )
        pos_df['close'] = pos_df['close'].fillna(0)
        return pos_df

    @staticmethod
    async def _get_prices_fixed_income(index_multiplier, prefixed_factor, pos_df):
        initial_price = pos_df.loc[0, 'transaction_price_brl']
        pos_df['close'] = pos_df['close'].fillna(0).astype(float)
        pos_df['init_price'] = initial_price
        pos_df['dividend'] = pos_df['dividend'].fillna(0).astype(float)

        pos_df['daily_index_factor'] = pos_df['close'].apply(
            lambda x: 1 + x / 100 * float(index_multiplier)
        )
        pos_df['index_factor_accumulated'] = pos_df['daily_index_factor'].cumprod()

        pos_df['fixed_rate_factor'] = 1
        if prefixed_factor > 0:
            daily_fee = (1 + float(prefixed_factor)) ** (1 / 252) - 1
            pos_df['acum_dates'] = pos_df['date'].apply(
                lambda x: np.busday_count(pos_df['date'].min().date(), x.date())
            )
            pos_df['fixed_rate_factor'] = (1 + daily_fee) ** pos_df['acum_dates']

        dividend_per_unit = np.where(
            (pos_df['dividend'] > 0) & (pos_df['quantity'] > 0),
            pos_df['dividend'] / pos_df['quantity'],
            0.0,
        )
        dividend_cumsum = np.cumsum(dividend_per_unit)

        pos_df['price'] = (
            initial_price * pos_df['index_factor_accumulated'] * pos_df['fixed_rate_factor']
        )
        pos_df['price'] -= dividend_cumsum

        pos_df['close'] = pos_df['price']
        return pos_df[['date', 'close']]
