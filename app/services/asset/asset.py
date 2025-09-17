from app.infrastructure.db.models.asset import Asset, AssetType, Event
from app.infrastructure.db.models.asset_fii import FIISegment
from app.infrastructure.db.models.asset_fixed_income import FixedIncome, FixedIncomeType
from app.infrastructure.db.models.constants.currency import CURRENCY
from app.infrastructure.db.repositories.base_repository import DatabaseRepository


async def list_assets(session):
    repo = DatabaseRepository(session)
    assets = await repo.get(Asset)
    return assets

async def list_asset_types(session):
    repo = DatabaseRepository(session)
    asset_types = await repo.get(AssetType)
    return asset_types

async def create_fixed_income(session, fixed_income: dict):
    repo = DatabaseRepository(session)
    asset_obj = {
        "ticker": fixed_income.get('ticker'),
        "name": fixed_income.get('name'),
        "asset_type_id": fixed_income.get('asset_type_id'),
        "currency_id": CURRENCY.BRL,
    }
    asset_ids = await repo.create(Asset, asset_obj)
    
    fixed_income_obj = {
        "asset_id": asset_ids[0],
        "maturity_date": fixed_income.get('maturity_date'),
        "fee": fixed_income.get('fee'),
        "index_id": fixed_income.get('index_id'),
        "fixed_income_type_id": fixed_income.get('fixed_income_type_id'),
    }
    await repo.create(FixedIncome, fixed_income_obj)
    
    await session.commit()
    return {'message': 'OK'}

async def list_fixed_income_types(session):
    repo = DatabaseRepository(session)
    fixed_income_types = await repo.get(FixedIncomeType)
    return fixed_income_types

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
