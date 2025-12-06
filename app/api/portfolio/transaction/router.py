from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Query

from app.entrypoints.worker.task_runner import run_task
from app.infra.db.session import get_session
from app.services.portfolio import portfolio_transaction_service as service
from app.worker.tasks.recalculate_asset_position import recalculate_position_asset

from .schema import Transaction

router = APIRouter(prefix='/transaction', tags=['Portfolio Transaction'])


@router.post('/')
async def create_transaction(
    transaction: Transaction,
    session = Depends(get_session),
):
    await service.create_transaction(session, transaction.model_dump())
    run_task(recalculate_position_asset, transaction.portfolio_id, transaction.asset_id)
    return {'message': 'Transaction created'}


@router.get('/{portfolio_id}')
async def get_transactions(
    portfolio_id: int,
    asset_id: int = Query(None),
    asset_type_ids: Optional[List[int]] = Query(None),
    currency_id: Optional[int] = Query(None),
    session = Depends(get_session),
):
    return await service.get_transactions(
        session,
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        asset_types_ids=asset_type_ids,
        currency_id=currency_id,
    )


@router.put('/')
async def update_transaction(
    transaction: dict,
    session = Depends(get_session),
):
    await service.update_transaction(session, transaction)
    return {'message': 'Transaction updated'}


@router.delete('/{transaction_id}')
async def delete_transaction(
    transaction_id: int,
    portfolio_id: int = Body(...),
    asset_id: int = Body(...),
    session = Depends(get_session),
):
    await service.delete_transaction(session, transaction_id)
    run_task(recalculate_position_asset, portfolio_id, asset_id)
    return {'message': 'Transaction deleted'}
    return {'message': 'Transaction deleted'}
    return {'message': 'Transaction deleted'}
