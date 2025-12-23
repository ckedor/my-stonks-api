# app/modules/asset/service/asset_service.py
"""
Asset service - handles asset management operations.
"""

from app.infra.db.models.asset import Asset, AssetType, Event
from app.infra.db.models.asset_fii import FIISegment
from app.infra.db.models.asset_fixed_income import FixedIncome, FixedIncomeType
from app.infra.db.models.constants.currency import CURRENCY
from app.infra.db.models.portfolio import Transaction
from app.infra.db.repositories.base_repository import SQLAlchemyRepository


class AssetService:
    def __init__(self, session):
        self.session = session
        self.repo = SQLAlchemyRepository(session)

    async def list_assets(self):
        assets = await self.repo.get(Asset)
        return assets

    async def delete_asset(self, asset_id: int):
        ## TODO: Fazer deletes cascade apropriados no BANCO
        await self.repo.delete(FixedIncome, by={"asset_id": asset_id})
        await self.repo.delete(Transaction, by={"asset_id": asset_id})
        await self.repo.delete(Asset, asset_id)
        
        await self.session.commit()
        return {'message': 'OK'}

    async def list_asset_types(self):
        asset_types = await self.repo.get(AssetType)
        return asset_types

    async def create_fixed_income(self, fixed_income: dict):
        asset_obj = {
            "ticker": fixed_income.get('ticker'),
            "name": fixed_income.get('name'),
            "asset_type_id": fixed_income.get('asset_type_id'),
            "currency_id": CURRENCY.BRL,
        }
        asset_ids = await self.repo.create(Asset, asset_obj)
        
        fixed_income_obj = {
            "asset_id": asset_ids[0],
            "maturity_date": fixed_income.get('maturity_date'),
            "fee": fixed_income.get('fee'),
            "index_id": fixed_income.get('index_id'),
            "fixed_income_type_id": fixed_income.get('fixed_income_type_id'),
        }
        await self.repo.create(FixedIncome, fixed_income_obj)
        
        await self.session.commit()
        return {'message': 'OK'}

    async def list_fixed_income_types(self):
        fixed_income_types = await self.repo.get(FixedIncomeType)
        return fixed_income_types

    async def list_fii_segments(self):
        fii_segments = await self.repo.get(FIISegment)
        return fii_segments

    async def list_events(self):
        events = await self.repo.get(Event)
        return events

    async def create_event(self, event):
        await self.repo.create(Event, event.model_dump())
        await self.session.commit()

    async def update_event(self, event):
        await self.repo.update(Event, event.model_dump())
        await self.session.commit()
