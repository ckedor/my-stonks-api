from fastapi import APIRouter

from app.api.asset.router import router as asset_router
from app.api.brokers.router import router as brokers_router
from app.api.market_data.router import router as market_data_router
from app.api.portfolio.router import router as portfolio_router

router = APIRouter()

router.include_router(asset_router)
router.include_router(market_data_router)
router.include_router(portfolio_router)
router.include_router(brokers_router)

@router.get('/hc', tags=['Health Check'])
async def healthcheck():
    return {'status': 'ok'}
