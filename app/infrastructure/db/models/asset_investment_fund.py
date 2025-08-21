from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class InvestmentFund(Base):
    __tablename__ = 'fund'
    __table_args__ = {'schema': 'asset'}

    asset_id = Column(Integer, ForeignKey('asset.asset.id'), primary_key=True)
    legal_id = Column(String(20))
    anbima_code = Column(String(12))
    anbima_code_class = Column(String(12))
    anbima_category = Column(String(100))

    asset = relationship('Asset', back_populates='fund')

    def __repr__(self):
        return 'InvestmentFund: ' + self.asset.ticker
