# app/modules/asset/api/routes.py
"""
Asset API routes.
Handles asset management, asset types, fixed income, and events.
"""

from typing import List

from app.infra.db.session import get_session
from app.modules.asset.api.schemas import (
    Asset,
    AssetEvent,
    AssetType,
    FixedIncomeAsset,
    FixedIncomeType,
)
from app.modules.asset.service.asset_service import AssetService
from fastapi import APIRouter, Depends

router = APIRouter(tags=['Assets'], prefix='/assets')


@router.get('/assets')
async def list_assets(
    session=Depends(get_session),
):
    """List all assets (cached for 24h)"""
    service = AssetService(session)
    return await service.list_assets()


@router.delete('/assets/{asset_id}')
async def delete_asset(
    asset_id: int,
    session=Depends(get_session),
):
    """Delete an asset by ID"""
    service = AssetService(session)
    return await service.delete_asset(asset_id)


@router.get('/types', response_model=List[AssetType])
async def list_asset_types(
    session=Depends(get_session),
):
    """List all asset types"""
    service = AssetService(session)
    return await service.list_asset_types()


@router.post('/fixed_income')
async def create_fixed_income(
    fixed_income: FixedIncomeAsset,
    session=Depends(get_session),
):
    """Create a new fixed income asset"""
    service = AssetService(session)
    return await service.create_fixed_income(fixed_income.model_dump())


@router.get('/fixed_income/types', response_model=List[FixedIncomeType])
async def list_fixed_income_types(
    session=Depends(get_session),
):
    """List all fixed income types"""
    service = AssetService(session)
    return await service.list_fixed_income_types()


@router.get('/fiis/segments')
async def get_segments(
    session=Depends(get_session),
):
    """Get FII segments"""
    service = AssetService(session)
    return await service.list_fii_segments()


@router.get('/events', response_model=List[AssetEvent])
async def list_events(
    session=Depends(get_session),
):
    """List all asset events"""
    service = AssetService(session)
    return await service.list_events()


@router.post('/event')
async def create_event(
    event: AssetEvent,
    session=Depends(get_session),
):
    """Create a new asset event"""
    service = AssetService(session)
    return await service.create_event(event)


@router.put('/event')
async def update_event(
    event: AssetEvent,
    session=Depends(get_session),
):
    """Update an asset event"""
    service = AssetService(session)
    return await service.update_event(event)
