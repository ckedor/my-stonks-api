from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.infra.db.base import Base


class Exchange(Base):
    __tablename__ = 'exchange'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    
    def __repr__(self):
        return self.code

class AssetClass(Base):
    __tablename__ = 'asset_class'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return self.name


class AssetType(Base):
    __tablename__ = 'asset_type'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    short_name = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    asset_class_id = Column(Integer, ForeignKey('asset.asset_class.id'), nullable=False)

    asset_class = relationship('AssetClass', lazy='joined')

    def __repr__(self):
        return self.short_name + ' - ' + self.name


class Currency(Base):
    __tablename__ = 'currency'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True, nullable=False)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return self.code


class Event(Base):
    __tablename__ = 'event'
    __table_args__ = {'schema': 'asset'}

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('asset.asset.id'), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String(50), nullable=False)
    factor = Column(Float, nullable=False)

    def __repr__(self):
        return self.name


class Asset(Base):
    __tablename__ = 'asset'
    __table_args__ = (
        UniqueConstraint('ticker', 'exchange_id', 'asset_type_id', name='uq_asset_ticker_exchange_type'),
        {'schema': 'asset'}
    )

    id = Column(Integer, primary_key=True)
    ticker = Column(String(30), nullable=True)
    name = Column(String(200), nullable=False)
    asset_type_id = Column(Integer, ForeignKey('asset.asset_type.id'), nullable=False)
    currency_id = Column(Integer, ForeignKey('asset.currency.id'), nullable=False)
    exchange_id = Column(Integer, ForeignKey('asset.exchange.id'), nullable=True)

    currency = relationship('Currency', lazy='joined')
    asset_type = relationship('AssetType', lazy='joined')
    exchange = relationship('Exchange', lazy='joined')

    stock = relationship('Stock', back_populates='asset', uselist=False)
    fii = relationship('FII', back_populates='asset', uselist=False)
    etf = relationship('ETF', back_populates='asset', uselist=False)
    fund = relationship('InvestmentFund', back_populates='asset', uselist=False)
    fixed_income = relationship('FixedIncome', back_populates='asset', uselist=False, cascade='all, delete-orphan')
    treasury_bond = relationship('TreasuryBond', back_populates='asset', uselist=False)

    def __repr__(self):
        return f"{self.ticker} - {self.name}"
