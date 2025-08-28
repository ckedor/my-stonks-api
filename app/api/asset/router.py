from typing import List

from fastapi import APIRouter, Depends

from app.infrastructure.db.session import get_session
from app.services.asset import asset as asset_service

from .schemas import Asset, AssetEvent, AssetType

router = APIRouter(tags=['Assets'], prefix='/assets')


@router.get('/assets', response_model=List[Asset])
async def list_assets(
    session = Depends(get_session),
):
    return await asset_service.list_assets(session)


@router.get('/types', response_model=List[AssetType])
async def list_asset_types(
    session = Depends(get_session),
):
    return await asset_service.list_asset_types(session)

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

@router.put('/event')
async def update_event(
    event: AssetEvent,
    session = Depends(get_session),
):
    return await asset_service.update_event(session, event)
