"""
Personal Finance service - handles expense/income tracking and summaries.
"""

import calendar
from datetime import date

from app.infra.db.models.personal_finance import (
    FinanceCategory,
    FinanceExpense,
    FinanceIncome,
    FinanceSubcategory,
)
from app.infra.db.repositories.base_repository import SQLAlchemyRepository
from app.modules.personal_finance.repositories.personal_finance_repository import (
    PersonalFinanceRepository,
)


class PersonalFinanceService:
    def __init__(self, session):
        self.session = session
        self.repo = SQLAlchemyRepository(session)
        self.finance_repo = PersonalFinanceRepository(session)

    async def list_categories(self, user_id: int):
        return await self.repo.get(
            FinanceCategory,
            by={'user_id': user_id},
            order_by='name',
            relations=['subcategories'],
        )

    async def create_category(self, user_id: int, name: str):
        ids = await self.repo.create(FinanceCategory, {'name': name, 'user_id': user_id})
        await self.session.commit()
        return await self.repo.get(FinanceCategory, id=ids[0])

    async def update_category(self, category_id: int, name: str):
        cat = await self.repo.get(FinanceCategory, id=category_id)
        if not cat:
            raise ValueError('Category not found')
        await self.repo.update(FinanceCategory, {'id': category_id, 'name': name})
        await self.session.commit()
        return await self.repo.get(FinanceCategory, id=category_id)

    async def delete_category(self, category_id: int):
        await self.repo.delete(FinanceCategory, id=category_id)
        await self.session.commit()

    async def create_subcategory(self, name: str, category_id: int):
        ids = await self.repo.create(FinanceSubcategory, {'name': name, 'category_id': category_id})
        await self.session.commit()
        return await self.repo.get(FinanceSubcategory, id=ids[0])

    async def update_subcategory(self, subcategory_id: int, name: str, category_id: int | None = None):
        sub = await self.repo.get(FinanceSubcategory, id=subcategory_id)
        if not sub:
            raise ValueError('Subcategory not found')
        data = {'id': subcategory_id, 'name': name}
        if category_id is not None:
            data['category_id'] = category_id
        await self.repo.update(FinanceSubcategory, data)
        await self.session.commit()
        return await self.repo.get(FinanceSubcategory, id=subcategory_id)

    async def delete_subcategory(self, subcategory_id: int):
        await self.repo.delete(FinanceSubcategory, id=subcategory_id)
        await self.session.commit()

    async def list_expenses(self, user_id: int, year: int, month: int):
        return await self.finance_repo.get_expenses_by_month(user_id, year, month)

    async def create_expense(self, user_id: int, data: dict):
        ids = await self.repo.create(FinanceExpense, {**data, 'user_id': user_id})
        await self.session.flush()
        expense = await self.finance_repo.get_expense_with_relations(ids[0])
        await self.session.commit()
        return expense

    async def update_expense(self, expense_id: int, data: dict):
        expense = await self.repo.get(FinanceExpense, id=expense_id)
        if not expense:
            raise ValueError('Expense not found')
        await self.repo.update(FinanceExpense, {'id': expense_id, **data}, flush=True)
        expense = await self.finance_repo.get_expense_with_relations(expense_id)
        await self.session.commit()
        return expense

    async def delete_expense(self, expense_id: int):
        await self.repo.delete(FinanceExpense, id=expense_id)
        await self.session.commit()

    async def list_incomes(self, user_id: int, year: int, month: int):
        last_day = calendar.monthrange(year, month)[1]
        return await self.repo.get(
            FinanceIncome,
            by={
                'user_id': user_id,
                'date__gte': date(year, month, 1),
                'date__lte': date(year, month, last_day),
            },
            order_by='date desc',
        )

    async def create_income(self, user_id: int, data: dict):
        ids = await self.repo.create(FinanceIncome, {**data, 'user_id': user_id})
        await self.session.commit()
        return await self.repo.get(FinanceIncome, id=ids[0])

    async def update_income(self, income_id: int, data: dict):
        income = await self.repo.get(FinanceIncome, id=income_id)
        if not income:
            raise ValueError('Income not found')
        await self.repo.update(FinanceIncome, {'id': income_id, **data})
        await self.session.commit()
        return await self.repo.get(FinanceIncome, id=income_id)

    async def delete_income(self, income_id: int):
        await self.repo.delete(FinanceIncome, id=income_id)
        await self.session.commit()

    async def yearly_summary(self, user_id: int, year: int):
        expense_map = await self.finance_repo.get_monthly_expense_totals(user_id, year)
        income_map = await self.finance_repo.get_monthly_income_totals(user_id, year)

        return [
            {
                'month': m,
                'total_income': income_map.get(m, 0),
                'total_expense': expense_map.get(m, 0),
            }
            for m in range(1, 13)
        ]

    async def monthly_breakdown(self, user_id: int, year: int, month: int):
        return await self.finance_repo.get_expense_breakdown(user_id, year, month)
