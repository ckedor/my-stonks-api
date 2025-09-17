from typing import List

from fastapi import APIRouter, Depends

from app.infrastructure.db.session import get_session
from app.services.asset import asset as asset_service

from .schemas import Asset, AssetEvent, AssetType, FixedIncomeAsset, FixedIncomeType

router = APIRouter(tags=['Assets'], prefix='/assets')


@router.get('/assets', response_model=List[Asset])
async def list_assets(
    session = Depends(get_session),
):
    return await asset_service.list_assets(session)

@router.delete('/assets/{asset_id}')
async def delete_asset(
    asset_id: int,
    session = Depends(get_session),
):
    return await asset_service.delete_asset(session, asset_id)

@router.get('/types', response_model=List[AssetType])
async def list_asset_types(
    session = Depends(get_session),
):
    return await asset_service.list_asset_types(session)

@router.post('/fixed_income')
async def create_fixed_income(
    fixed_income: FixedIncomeAsset,
    session = Depends(get_session),
):
    return await asset_service.create_fixed_income(session, fixed_income.model_dump())

@router.get('/fixed_income/types', response_model=List[FixedIncomeType])
async def list_fixed_income_types(
    session = Depends(get_session),
):
    return await asset_service.list_fixed_income_types(session)

@router.get('/fiis/segments')
async def get_segments(
    session = Depends(get_session),
):
    return await asset_service.list_fii_segments(session)

@router.get('/events', response_model=List[AssetEvent])
async def list_events(
    session = Depends(get_session),
):
    return await asset_service.list_events(session)

@router.post('/event')
async def create_event(
    event: AssetEvent,
    session = Depends(get_session),
):
    return await asset_service.create_event(session, event)

@router.put('/event')
async def update_event(
    event: AssetEvent,
    session = Depends(get_session),
):
    return await asset_service.update_event(session, event)
