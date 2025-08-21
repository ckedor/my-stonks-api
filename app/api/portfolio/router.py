from fastapi import APIRouter, Depends

from app.users.views import current_active_user

from .category.router import router as category_router
from .dividend.router import router as dividend_router
from .income_tax.router import router as income_tax_router
from .portfolio.router import router as portfolio_router
from .position.router import router as position_router
from .position_consolidator.router import router as position_consolidator_router
from .transaction.router import router as transaction_router
from .user_configuration.router import router as user_configuration_router

router = APIRouter(prefix='/portfolio', dependencies=[Depends(current_active_user)])

router.include_router(portfolio_router)
router.include_router(dividend_router)
router.include_router(category_router)
router.include_router(transaction_router)
router.include_router(position_router)
router.include_router(position_consolidator_router)
router.include_router(income_tax_router)
router.include_router(user_configuration_router)

__all__ = ['router']
