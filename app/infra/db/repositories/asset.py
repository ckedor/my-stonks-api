from app.infra.db.repositories.base_repository import DatabaseRepository


class AssetRepository(DatabaseRepository):
    def __init__(self, session):
        super().__init__(session)
