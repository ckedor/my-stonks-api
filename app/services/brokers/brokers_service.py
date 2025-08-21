from app.infrastructure.db.models.portfolio import Broker
from app.infrastructure.db.repositories.base_repository import DatabaseRepository


async def list_brokers(session):
    repo = DatabaseRepository(session)
    brokers = await repo.get(Broker)
    return brokers