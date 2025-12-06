import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config
from app.infra.db.base import Base
from app.main import app
from app.users.decorators import authenticated
from app.users.models import User

# Força ambiente de teste
os.environ['ENVIRONMENT'] = 'testing'

# Lê URL do banco de testes
TEST_DATABASE_URL = os.getenv(
    'DATABASE_URL', 'postgresql://admin:roots123@localhost:5434/my-stonks-api-db-test'
)


engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


def run_migrations():
    config = Config('alembic.ini')
    config.set_main_option('sqlalchemy.url', TEST_DATABASE_URL)
    command.upgrade(config, 'head')


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    run_migrations()
    db = TestingSessionLocal()

    existing_user = db.query(User).filter_by(email='seed@user.com').first()
    if not existing_user:
        user = User(
            username='admin',
            email='seed@user.com',
            hashed_password='123',
            is_superuser=True,
        )
        db.add(user)
        db.flush()
        existing_user = user

    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def truncate_tables():
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name not in {
                'currency',
                'asset_type',
                'asset_class',
                'etf_segment',
                'fii_segment',
                'fii_type',
                'fixed_income_type',
                'treasury_bond_type',
                'user',
            }:
                conn.execute(table.delete())


@pytest.fixture
def db():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture(autouse=True)
def override_authenticated_user():
    fake_user = User(id=1, email='seed@user.com', is_superuser=True)
    app.dependency_overrides[authenticated] = lambda: fake_user
