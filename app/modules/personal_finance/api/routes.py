"""
Personal Finance API routes.
Handles expense tracking, income management, categories, and financial summaries.
"""

from datetime import date
from typing import List

from app.infra.db.session import get_session
from app.modules.personal_finance.api.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    ExpenseCreate,
    ExpenseOut,
    ExpenseUpdate,
    IncomeCreate,
    IncomeOut,
    IncomeUpdate,
    MonthlySummary,
    SubcategoryCreate,
    SubcategoryGoalProgress,
    SubcategoryGoalUpdate,
    SubcategoryOut,
    SubcategoryUpdate,
)
from app.modules.personal_finance.service.personal_finance_service import (
    PersonalFinanceService,
)
from app.modules.users.models import User
from app.modules.users.views import current_active_user
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix='/finances',
    tags=['Personal Finance'],
    dependencies=[Depends(current_active_user)],
)


# ── Categories ───────────────────────────────────────────────────

@router.get('/categories', response_model=List[CategoryOut])
async def list_categories(
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    return await service.list_categories(user.id)


@router.post('/categories', response_model=CategoryOut)
async def create_category(
    data: CategoryCreate,
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    cat = await service.create_category(user.id, data.name)
    return CategoryOut(id=cat.id, name=cat.name, subcategories=[])


@router.put('/categories/{category_id}', response_model=CategoryOut)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    try:
        cat = await service.update_category(category_id, data.name)
        return CategoryOut(id=cat.id, name=cat.name, subcategories=[])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/categories/{category_id}')
async def delete_category(category_id: int, session=Depends(get_session)):
    service = PersonalFinanceService(session)
    try:
        await service.delete_category(category_id)
        return {'message': 'OK'}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Subcategories ────────────────────────────────────────────────

@router.post('/subcategories', response_model=SubcategoryOut)
async def create_subcategory(
    data: SubcategoryCreate,
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    sub = await service.create_subcategory(data.name, data.category_id)
    return sub


@router.put('/subcategories/{subcategory_id}', response_model=SubcategoryOut)
async def update_subcategory(
    subcategory_id: int,
    data: SubcategoryUpdate,
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    try:
        sub = await service.update_subcategory(subcategory_id, data.name, data.category_id)
        return sub
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/subcategories/{subcategory_id}')
async def delete_subcategory(subcategory_id: int, session=Depends(get_session)):
    service = PersonalFinanceService(session)
    try:
        await service.delete_subcategory(subcategory_id)
        return {'message': 'OK'}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put('/subcategories/{subcategory_id}/goal', response_model=SubcategoryOut)
async def update_subcategory_goal(
    subcategory_id: int,
    data: SubcategoryGoalUpdate,
    session=Depends(get_session),
):
    if data.goal_amount is not None and data.goal_amount <= 0:
        raise HTTPException(status_code=400, detail='Goal must be greater than zero')
    service = PersonalFinanceService(session)
    try:
        sub = await service.update_subcategory_goal(subcategory_id, data.goal_amount)
        return sub
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Expenses ─────────────────────────────────────────────────────

@router.get('/expenses', response_model=List[ExpenseOut])
async def list_expenses(
    year: int,
    month: int,
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    return await service.list_expenses(user.id, year, month)


@router.post('/expenses', response_model=ExpenseOut)
async def create_expense(
    data: ExpenseCreate,
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    return await service.create_expense(user.id, data.model_dump())


@router.put('/expenses/{expense_id}', response_model=ExpenseOut)
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    try:
        return await service.update_expense(
            expense_id, data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/expenses/{expense_id}')
async def delete_expense(expense_id: int, session=Depends(get_session)):
    service = PersonalFinanceService(session)
    try:
        await service.delete_expense(expense_id)
        return {'message': 'OK'}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Incomes ──────────────────────────────────────────────────────

@router.get('/incomes', response_model=List[IncomeOut])
async def list_incomes(
    year: int,
    month: int,
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    return await service.list_incomes(user.id, year, month)


@router.post('/incomes', response_model=IncomeOut)
async def create_income(
    data: IncomeCreate,
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    return await service.create_income(user.id, data.model_dump())


@router.put('/incomes/{income_id}', response_model=IncomeOut)
async def update_income(
    income_id: int,
    data: IncomeUpdate,
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    try:
        return await service.update_income(
            income_id, data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/incomes/{income_id}')
async def delete_income(income_id: int, session=Depends(get_session)):
    service = PersonalFinanceService(session)
    try:
        await service.delete_income(income_id)
        return {'message': 'OK'}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Summaries ────────────────────────────────────────────────────

@router.get('/summary/yearly', response_model=List[MonthlySummary])
async def yearly_summary(
    year: int,
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    return await service.yearly_summary(user.id, year)


@router.get('/summary/monthly')
async def monthly_breakdown(
    year: int,
    month: int,
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    return await service.monthly_breakdown(user.id, year, month)


@router.get('/summary/monthly-goals', response_model=List[SubcategoryGoalProgress])
async def monthly_goals_progress(
    year: int,
    month: int,
    user: User = Depends(current_active_user),
    session=Depends(get_session),
):
    service = PersonalFinanceService(session)
    return await service.monthly_goals_progress(user.id, year, month)
