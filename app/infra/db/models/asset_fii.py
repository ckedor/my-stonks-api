from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infra.db.base import Base


class FIISegment(Base):
    __tablename__ = 'fii_segment'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    type_id = Column(Integer, ForeignKey('asset.fii_type.id'))

    type = relationship('FIIType', lazy='joined')

    def __repr__(self):
        return self.name + ' - ' + self.type.name


class FIIType(Base):
    __tablename__ = 'fii_type'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return self.name


class FII(Base):
    __tablename__ = 'fii'
    __table_args__ = {'schema': 'asset'}

    asset_id = Column(Integer, ForeignKey('asset.asset.id'), primary_key=True)
    segment_id = Column(Integer, ForeignKey('asset.fii_segment.id'), nullable=False)

    segment = relationship('FIISegment')
    asset = relationship('Asset', back_populates='fii', lazy='joined')

    def __repr__(self):
        return 'FII: ' + self.asset.ticker
