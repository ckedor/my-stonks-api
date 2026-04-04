from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'public'}

    id: Mapped[int] = mapped_column(primary_key=True)
    username = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str]
    is_active: Mapped[bool]
    is_superuser: Mapped[bool]
    is_verified: Mapped[bool]
