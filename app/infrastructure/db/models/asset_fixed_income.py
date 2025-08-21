from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class FixedIncome(Base):
    __tablename__ = 'fixed_income'
    __table_args__ = {'schema': 'asset'}

    asset_id = Column(Integer, ForeignKey('asset.asset.id'), primary_key=True)
    maturity_date = Column(Date)
    fee = Column(Numeric(8, 5))
    index_id = Column(Integer, ForeignKey('market_data.index.id'))
    fixed_income_type_id = Column(Integer, ForeignKey('asset.fixed_income_type.id'))

    asset = relationship('Asset', back_populates='fixed_income')
    fixed_income_type = relationship('FixedIncomeType', back_populates='fixed_incomes')
    index = relationship('Index', lazy='joined')

    def __repr__(self):
        return 'FixedIncome: ' + self.asset.ticker


class FixedIncomeType(Base):
    __tablename__ = 'fixed_income_type'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))

    fixed_incomes = relationship('FixedIncome', back_populates='fixed_income_type')

    def __repr__(self):
        return self.name
