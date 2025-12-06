from fastapi import APIRouter, Depends

from app.infra.db.session import get_session
from app.services.portfolio import (
    portfolio_user_configuration as user_configuration_service,
)

from .schemas import UserConfigurationUpdateRequest

router = APIRouter(tags=['Configuração do Usuário'])

@router.get('/{portfolio_id}/user_configurations')
async def get_user_configurations(
    portfolio_id: int,
    session = Depends(get_session)
):
    return await user_configuration_service.get_user_configurations(session, portfolio_id)

@router.put('/{portfolio_id}/user_configuration')
async def update_user_configuration(
    portfolio_id: int,
    user_configuration_request: UserConfigurationUpdateRequest,
    session = Depends(get_session)
):
    return await user_configuration_service.update_user_configuration(session, portfolio_id, user_configuration_request)