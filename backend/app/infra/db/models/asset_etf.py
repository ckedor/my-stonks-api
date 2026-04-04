from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infra.db.base import Base


class ETF(Base):
    __tablename__ = 'etf'
    __table_args__ = {'schema': 'asset'}

    asset_id = Column(Integer, ForeignKey('asset.asset.id'), primary_key=True)
    segment_id = Column(Integer, ForeignKey('asset.etf_segment.id'))

    segment = relationship('ETFSegment')
    asset = relationship('Asset', back_populates='etf')


class ETFSegment(Base):
    __tablename__ = 'etf_segment'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return self.name
