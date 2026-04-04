"""
Personal Finance repository - handles aggregate queries that go beyond base CRUD.
"""

from collections import defaultdict

from app.infra.db.models.personal_finance import (
    FinanceCategory,
    FinanceExpense,
    FinanceIncome,
    FinanceSubcategory,
)
from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class PersonalFinanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_expenses_by_month(self, user_id: int, year: int, month: int):
        stmt = (
            select(FinanceExpense)
            .where(
                FinanceExpense.user_id == user_id,
                extract('year', FinanceExpense.date) == year,
                extract('month', FinanceExpense.date) == month,
            )
            .options(
                selectinload(FinanceExpense.subcategory).selectinload(
                    FinanceSubcategory.category
                )
            )
            .order_by(FinanceExpense.date.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_expense_with_relations(self, expense_id: int):
        stmt = (
            select(FinanceExpense)
            .where(FinanceExpense.id == expense_id)
            .options(
                selectinload(FinanceExpense.subcategory).selectinload(
                    FinanceSubcategory.category
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_monthly_expense_totals(self, user_id: int, year: int) -> dict[int, float]:
        stmt = (
            select(
                extract('month', FinanceExpense.date).label('month'),
                func.coalesce(func.sum(FinanceExpense.amount), 0).label('total'),
            )
            .where(
                FinanceExpense.user_id == user_id,
                extract('year', FinanceExpense.date) == year,
            )
            .group_by(extract('month', FinanceExpense.date))
        )
        result = await self.session.execute(stmt)
        return {int(row.month): float(row.total) for row in result}

    async def get_monthly_income_totals(self, user_id: int, year: int) -> dict[int, float]:
        stmt = (
            select(
                extract('month', FinanceIncome.date).label('month'),
                func.coalesce(func.sum(FinanceIncome.amount), 0).label('total'),
            )
            .where(
                FinanceIncome.user_id == user_id,
                extract('year', FinanceIncome.date) == year,
            )
            .group_by(extract('month', FinanceIncome.date))
        )
        result = await self.session.execute(stmt)
        return {int(row.month): float(row.total) for row in result}

    async def get_expense_breakdown(self, user_id: int, year: int, month: int):
        """Returns expense breakdown by category and subcategory for a month."""
        expenses = await self.get_expenses_by_month(user_id, year, month)

        by_category: dict[str, float] = defaultdict(float)
        sub_map: dict[str, float] = defaultdict(float)
        sub_cat_map: dict[str, str] = {}

        for exp in expenses:
            cat_name = exp.subcategory.category.name
            sub_name = exp.subcategory.name
            by_category[cat_name] += exp.amount
            sub_map[sub_name] += exp.amount
            sub_cat_map[sub_name] = cat_name

        category_breakdown = [
            {'category': cat, 'total': round(total, 2)}
            for cat, total in sorted(by_category.items(), key=lambda x: -x[1])
        ]

        subcategory_breakdown = [
            {'subcategory': sub, 'category': sub_cat_map[sub], 'total': round(total, 2)}
            for sub, total in sorted(sub_map.items(), key=lambda x: -x[1])
        ]

        return {
            'by_category': category_breakdown,
            'by_subcategory': subcategory_breakdown,
        }

    async def get_subcategories_with_goals(self, user_id: int):
        stmt = (
            select(FinanceSubcategory)
            .join(FinanceCategory, FinanceSubcategory.category_id == FinanceCategory.id)
            .where(
                FinanceCategory.user_id == user_id,
                FinanceSubcategory.goal_amount.is_not(None),
                FinanceSubcategory.goal_amount > 0,
            )
            .options(selectinload(FinanceSubcategory.category))
            .order_by(FinanceCategory.name.asc(), FinanceSubcategory.name.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_categories_with_goals(self, user_id: int):
        stmt = (
            select(FinanceCategory)
            .where(
                FinanceCategory.user_id == user_id,
                FinanceCategory.goal_amount.is_not(None),
                FinanceCategory.goal_amount > 0,
            )
            .options(selectinload(FinanceCategory.subcategories))
            .order_by(FinanceCategory.name.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_monthly_spent_by_subcategory(
        self,
        user_id: int,
        year: int,
        month: int,
    ) -> dict[int, float]:
        stmt = (
            select(
                FinanceExpense.subcategory_id.label('subcategory_id'),
                func.coalesce(func.sum(FinanceExpense.amount), 0).label('total'),
            )
            .where(
                FinanceExpense.user_id == user_id,
                extract('year', FinanceExpense.date) == year,
                extract('month', FinanceExpense.date) == month,
            )
            .group_by(FinanceExpense.subcategory_id)
        )
        result = await self.session.execute(stmt)
        return {int(row.subcategory_id): float(row.total) for row in result}

    async def get_monthly_spent_by_category(
        self,
        user_id: int,
        year: int,
        month: int,
    ) -> dict[int, float]:
        stmt = (
            select(
                FinanceCategory.id.label('category_id'),
                func.coalesce(func.sum(FinanceExpense.amount), 0).label('total'),
            )
            .join(FinanceSubcategory, FinanceExpense.subcategory_id == FinanceSubcategory.id)
            .join(FinanceCategory, FinanceSubcategory.category_id == FinanceCategory.id)
            .where(
                FinanceExpense.user_id == user_id,
                extract('year', FinanceExpense.date) == year,
                extract('month', FinanceExpense.date) == month,
            )
            .group_by(FinanceCategory.id)
        )
        result = await self.session.execute(stmt)
        return {int(row.category_id): float(row.total) for row in result}
