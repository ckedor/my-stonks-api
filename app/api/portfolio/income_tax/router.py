from fastapi import APIRouter, Depends, Query

from app.infra.db.session import get_session
from app.services.portfolio import portfolio_income_tax_service as service

router = APIRouter(tags=['Imposto de Renda'])

@router.get('/{portfolio_id}/income_tax/assets_and_rights')
async def get_assets_and_rights(
    portfolio_id: int,
    fiscal_year: int = Query(...),
    session = Depends(get_session),
):
    return await service.get_assets_and_rights(session, portfolio_id,  fiscal_year)

@router.get('/{portfolio_id}/income_tax/variable_income/fiis_operations')
async def get_fiis_operations_tax(
    portfolio_id: int,
    fiscal_year: int = Query(...),
    session = Depends(get_session),
):
    return await service.get_fiis_operations_tax(session, portfolio_id,  fiscal_year)

@router.get('/{portfolio_id}/income_tax/variable_income/common_operations')
async def get_common_operations_tax(
    portfolio_id: int,
    fiscal_year: int = Query(...),
    session = Depends(get_session),
):
    return await service.get_common_operations_tax(session, portfolio_id, fiscal_year)

@router.get('/{portfolio_id}/income_tax/darf')
async def get_common_operations_tax(
    portfolio_id: int,
    fiscal_year: int = Query(...),
    session = Depends(get_session),
):
    return await service.get_darf(session, portfolio_id, fiscal_year)
        
    
    
    
    
    
    
    
