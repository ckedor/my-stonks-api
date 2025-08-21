from typing import List

import numpy as np
import pandas as pd

from app.infrastructure.db.models.portfolio import Transaction
from app.infrastructure.db.repositories.portfolio import PortfolioRepository
from app.utils.response import df_response
from app.worker.task_runner import run_task
from app.worker.tasks.recalculate_asset_position import recalculate_position_asset


async def create_transaction(session, transaction: dict) -> None:
    async with session.begin():
        repo = PortfolioRepository(session)
        transaction['date'] = pd.to_datetime(transaction['date']).date()
        await repo.create(Transaction, transaction)

async def get_transactions(session, portfolio_id: int, asset_id: int = None, asset_types_ids: List[int] = None, currency_id: int = None) -> pd.DataFrame:
    repo = PortfolioRepository(session)
    transactions_df = await repo.get_transactions_df(portfolio_id, asset_id, asset_types_ids, currency_id)
    transactions_df['original_price'] = transactions_df['price'].copy()
    ##transactions_df = await ._normalize_currency(transactions_df, CURRENCY.BRL) #TODO: Normalize Currency

    transactions_df = _calculate_profits(transactions_df)
    transactions_df['type'] = np.where(transactions_df['quantity'] > 0, 'Compra', 'Venda')

    transactions_df['value'] = transactions_df['quantity'] * transactions_df['price']
    transactions_df['acc_quantity'] = transactions_df.groupby('asset_id')['quantity'].cumsum()
    transactions_df['position'] = transactions_df['acc_quantity'] * transactions_df['price']
    transactions_df['profit_pct'] = np.where(
        transactions_df['type'] == 'Venda',
        (transactions_df['realized_profit'] / abs(transactions_df['value'])) * 100,
        np.nan,
    )
    transactions_df['portfolio_id'] = portfolio_id
    transactions_df.sort_values(by=['date'], inplace=True)
    return df_response(transactions_df)

async def update_transaction(session, transaction: dict) -> None:
    async with session.begin():
        repo = PortfolioRepository(session)
        old_portfolio = await repo.get(Transaction, transaction.get('id'), first=True)
        old_portfolio_id = old_portfolio.portfolio_id
    
        transaction['date'] = pd.to_datetime(transaction['date']).date()
        repo = PortfolioRepository(session)
        await repo.update(Transaction, transaction)
        
    run_task(recalculate_position_asset, transaction['portfolio_id'], transaction['asset_id'])
    if transaction['portfolio_id'] != old_portfolio_id:
        run_task(recalculate_position_asset, old_portfolio_id, transaction['asset_id'])

async def delete_transaction(session, transaction_id) -> None:
    async with session.begin():
        repo = PortfolioRepository(session)
        await repo.delete(Transaction, id=transaction_id)
    
    
def _calculate_profits(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(by=['asset_id', 'date']).copy()
    df['average_price'] = None
    df['realized_profit'] = None

    for _, group in df.groupby('asset_id'):
        quantity_held = 0.0
        total_cost = 0.0

        for idx, row in group.iterrows():
            qty = row['quantity']
            price = row['price']

            if qty > 0:
                total_cost += qty * price
                quantity_held += qty
                avg_price = total_cost / quantity_held if quantity_held else 0
                df.at[idx, 'average_price'] = avg_price
                df.at[idx, 'realized_profit'] = 0.0
            else:
                avg_price = total_cost / quantity_held
                realized_profit = -qty * (price - avg_price)

                quantity_held += qty
                total_cost = avg_price * quantity_held if quantity_held > 0 else 0

                df.at[idx, 'average_price'] = avg_price
                df.at[idx, 'realized_profit'] = realized_profit

    return df