# app/modules/brokers/api/routes.py
"""
Brokers API routes.
Handles broker listing.
"""

from typing import List

from fastapi import APIRouter, Depends

from app.infra.db.session import get_session
from app.modules.brokers.api.schemas import Broker
from app.modules.brokers.service.brokers_service import BrokersService

router = APIRouter(tags=['Brokers'], prefix='/brokers')


@router.get('/list', response_model=List[Broker])
async def list_brokers(
    session=Depends(get_session),
):
    """List all brokers"""
    service = BrokersService(session)
    return await service.list_brokers()
