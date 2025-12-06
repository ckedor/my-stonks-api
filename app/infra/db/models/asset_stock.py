from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infra.db.base import Base


class Stock(Base):
    __tablename__ = 'stock'
    __table_args__ = {'schema': 'asset'}

    asset_id = Column(Integer, ForeignKey('asset.asset.id'), primary_key=True)
    country = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)

    asset = relationship('Asset', back_populates='stock')
