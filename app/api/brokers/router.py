from typing import List

from fastapi import APIRouter, Depends

from app.infrastructure.db.session import get_session
from app.services.brokers import brokers_service as service

from .schemas import Broker

router = APIRouter(tags=['Brokers'], prefix='/brokers')


@router.get('/list', response_model=List[Broker])
async def list_brokers(
    session = Depends(get_session),
):
    return await service.list_brokers(session)
