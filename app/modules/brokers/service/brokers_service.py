# app/modules/brokers/service/brokers_service.py
"""
Brokers service - handles broker management operations.
"""

from app.infra.db.models.portfolio import Broker
from app.infra.db.repositories.base_repository import SQLAlchemyRepository


class BrokersService:
    def __init__(self, session):
        self.session = session
        self.repo = SQLAlchemyRepository(session)

    async def list_brokers(self):
        brokers = await self.repo.get(Broker)
        return brokers
