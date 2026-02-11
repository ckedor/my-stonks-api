from fastapi import APIRouter, Depends

from app.infra.db.session import get_session
from app.modules.portfolio.service.portfolio_rebalancing_service import (
    PortfolioRebalancingService,
)

from .schema import RebalancingResponse, SaveTargetsRequest

router = APIRouter(tags=['Portfolio Rebalancing'])


@router.get('/{portfolio_id}/rebalancing', response_model=RebalancingResponse)
async def get_rebalancing(
    portfolio_id: int,
    session=Depends(get_session),
):
    service = PortfolioRebalancingService(session)
    return await service.get_rebalancing_data(portfolio_id)


@router.put('/{portfolio_id}/rebalancing')
async def save_rebalancing_targets(
    portfolio_id: int,
    payload: SaveTargetsRequest,
    session=Depends(get_session),
):
    service = PortfolioRebalancingService(session)
    await service.save_targets(payload)
    return {'message': 'Targets de rebalanceamento salvos com sucesso.'}
