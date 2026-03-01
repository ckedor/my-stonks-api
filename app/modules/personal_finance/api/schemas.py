from datetime import date as DateType
from typing import Optional

from pydantic import BaseModel, ConfigDict


# --- Category ---
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class SubcategoryOut(BaseModel):
    id: int
    name: str
    category_id: int
    goal_amount: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryOut(BaseModel):
    id: int
    name: str
    subcategories: list[SubcategoryOut] = []

    model_config = ConfigDict(from_attributes=True)


# --- Subcategory ---
class SubcategoryCreate(BaseModel):
    name: str
    category_id: int


class SubcategoryUpdate(BaseModel):
    name: str
    category_id: Optional[int] = None


# --- Expense ---
class ExpenseCreate(BaseModel):
    amount: float
    date: DateType
    description: Optional[str] = None
    subcategory_id: int


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[DateType] = None
    description: Optional[str] = None
    subcategory_id: Optional[int] = None


class SubcategoryBrief(BaseModel):
    id: int
    name: str
    category_id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryBrief(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class SubcategoryWithCategory(BaseModel):
    id: int
    name: str
    category_id: int
    goal_amount: Optional[float] = None
    category: CategoryBrief

    model_config = ConfigDict(from_attributes=True)


class ExpenseOut(BaseModel):
    id: int
    amount: float
    date: DateType
    description: Optional[str] = None
    subcategory_id: int
    subcategory: SubcategoryWithCategory

    model_config = ConfigDict(from_attributes=True)


# --- Income ---
class IncomeCreate(BaseModel):
    amount: float
    date: DateType
    description: str


class IncomeUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[DateType] = None
    description: Optional[str] = None


class IncomeOut(BaseModel):
    id: int
    amount: float
    date: DateType
    description: str

    model_config = ConfigDict(from_attributes=True)


# --- Summaries ---
class MonthlySummary(BaseModel):
    month: int
    total_income: float
    total_expense: float


class CategoryExpense(BaseModel):
    category: str
    total: float


class SubcategoryExpense(BaseModel):
    subcategory: str
    category: str
    total: float


class SubcategoryGoalUpdate(BaseModel):
    goal_amount: Optional[float] = None


class SubcategoryGoalProgress(BaseModel):
    subcategory_id: int
    subcategory_name: str
    category_id: int
    category_name: str
    goal_amount: float
    spent_amount: float
    remaining_amount: float
    progress_percent: float
    per_day_available: float
    days_remaining: int
    is_over_goal: bool
