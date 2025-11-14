from typing import List

from fastapi import APIRouter, Depends
from fastapi.params import Query

import app.services.market_data as service
from app.infrastructure.db.models.constants.asset_type import ASSET_TYPE
from app.infrastructure.db.models.constants.exchange import EXCHANGE
from app.infrastructure.db.session import get_session
from app.users.models import User
from app.users.views import current_active_user, current_superuser
from app.worker.task_runner import run_task
from app.worker.tasks.set_indexes_history_cache import set_indexes_history_cache

from .schemas import (
    MarketIndex,
    MarketIndexesTimeSeries,
    QuoteResponse,
    USD_BRL_History,
)

router = APIRouter(prefix='/market_data', tags=['Market Data'], dependencies=[Depends(current_active_user)])


@router.get('/indexes', response_model=List[MarketIndex])
async def list_indexes(
    session = Depends(get_session),
):
    return await service.list_indexes(session)

@router.get('/indexes/time_series', response_model=MarketIndexesTimeSeries)
async def get_indexes_time_series(
    session = Depends(get_session),
):
    return await service.get_indexes_history(session)

@router.get('/indexes/usd_brl', response_model=USD_BRL_History)
async def get_usd_brl_history(
    session = Depends(get_session),
):
    return await service.get_usd_brl_history(session, as_df=False)

@router.post('/indexes/consolidate_history')
async def consolidate_market_indexes_history(
    _: User = Depends(current_superuser),
    session = Depends(get_session),
):
    await service.consolidate_market_indexes_history(session)
    run_task(set_indexes_history_cache)
    return {'message': 'OK'}


@router.get('/quotes', response_model=QuoteResponse)
async def get_asset_quotes(
    ticker: str,
    asset_type:  str | None = Query(
        default=None,
        enum=[e.name for e in ASSET_TYPE],
    ),
    exchange: EXCHANGE | None = Query(default=None),
    date: str = None,
    start_date: str = None,
    end_date: str = None,
    treasury_type: str = None,
    treasury_maturity_date: str = None,
):
    return await service.get_asset_quotes(
        ticker,
        asset_type,
        exchange,
        date,
        start_date,
        end_date,
        treasury_type,
        treasury_maturity_date,
    )