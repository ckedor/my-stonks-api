from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infra.db.base import Base


class TreasuryBondType(Base):
    __tablename__ = 'treasury_bond_type'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    treasury_bonds = relationship('TreasuryBond', back_populates='type')

    def __repr__(self):
        return self.name


class TreasuryBond(Base):
    __tablename__ = 'treasury_bond'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('asset.asset.id'), nullable=False)
    maturity_date = Column(Date)
    type_id = Column(Integer, ForeignKey('asset.treasury_bond_type.id'), nullable=False)
    type = relationship('TreasuryBondType', back_populates='treasury_bonds', lazy='joined')

    asset = relationship('Asset', back_populates='treasury_bond')

    def __repr__(self):
        return 'TreasuryBond: ' + self.asset.ticker
