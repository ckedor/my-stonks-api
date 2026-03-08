from app.infra.db.base import Base
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class FinanceCategory(Base):
    __tablename__ = 'category'
    __table_args__ = {'schema': 'personal_finance'}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    goal_amount = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey('public.user.id'), nullable=False)

    subcategories = relationship(
        'FinanceSubcategory', back_populates='category', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'FinanceCategory({self.name})'


class FinanceSubcategory(Base):
    __tablename__ = 'subcategory'
    __table_args__ = {'schema': 'personal_finance'}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    goal_amount = Column(Float, nullable=True)
    category_id = Column(
        Integer, ForeignKey('personal_finance.category.id', ondelete='CASCADE'), nullable=False
    )

    category = relationship('FinanceCategory', back_populates='subcategories')
    expenses = relationship('FinanceExpense', back_populates='subcategory')

    def __repr__(self):
        return f'FinanceSubcategory({self.name})'


class FinanceExpense(Base):
    __tablename__ = 'expense'
    __table_args__ = {'schema': 'personal_finance'}

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String(200), nullable=True)
    subcategory_id = Column(
        Integer, ForeignKey('personal_finance.subcategory.id'), nullable=False
    )
    user_id = Column(Integer, ForeignKey('public.user.id'), nullable=False)

    subcategory = relationship('FinanceSubcategory', back_populates='expenses', lazy='joined')

    def __repr__(self):
        return f'FinanceExpense({self.amount} on {self.date})'


class FinanceIncome(Base):
    __tablename__ = 'income'
    __table_args__ = {'schema': 'personal_finance'}

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('public.user.id'), nullable=False)

    def __repr__(self):
        return f'FinanceIncome({self.description}: {self.amount})'
