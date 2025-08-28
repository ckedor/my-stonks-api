from app.infrastructure.db.models.asset import Asset, AssetType, Event
from app.infrastructure.db.models.asset_fii import FIISegment
from app.infrastructure.db.repositories.base_repository import DatabaseRepository


async def list_assets(session):
    repo = DatabaseRepository(session)
    assets = await repo.get(Asset)
    return assets

async def list_asset_types(session):
    repo = DatabaseRepository(session)
    asset_types = await repo.get(AssetType)
    return asset_types

async def list_fii_segments(session):
    repo = DatabaseRepository(session)
    fii_segments = await repo.get(FIISegment)
    return fii_segments

async def list_events(session):
    repo = DatabaseRepository(session)
    events = await repo.get(Event)
    return events

async def create_event(session, event):
    repo = DatabaseRepository(session)
    await repo.create(Event, event.model_dump())
    await session.commit()

async def update_event(session, event):
    repo = DatabaseRepository(session)
    await repo.update(Event, event.model_dump())
    await session.commit()
