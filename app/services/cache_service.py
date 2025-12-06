from app.infra.redis.redis_service import RedisService
from app.services.portfolio import portfolio_position_service


class CacheService:
    def __init__(self):
        self.redis = RedisService()
        self.ttl = 60 * 60 * 4

    async def set_patrimony_evolution_cache(self, patrimony_evolution, portfolio_id: str) -> None:
        patrimony_evolution_json_str = patrimony_evolution.to_json(
            orient='records',
            date_format='iso',
            double_precision=10,
        )
        await self.redis.set_json(
            f'patrimony_evolution:{portfolio_id}',
            patrimony_evolution_json_str,
            expire_seconds=self.ttl,
        )

    async def get_patrimony_evolution_cache(self, portfolio_id: str) -> dict:
        cache = await self.redis.get_json(f'patrimony_evolution:{portfolio_id}')
        return cache

    async def set_market_indexes_history(self, indexes_history):
        await self.redis.set_json(
            'indexes_history',
            indexes_history,
            expire_seconds=self.ttl,
        )

    async def get_market_indexes_history(self) -> dict:
        cache = await self.redis.get_json('indexes_history')
        return cache

    async def set_portfolio_returns(self, portfolio_returns, portfolio_id: str) -> None:
        
        #serialized = PortfolioReturnsResponse(**portfolio_returns).model_dump(mode='json')
        
        await self.redis.set_json(
            f'portfolio_returns:{portfolio_id}',
            portfolio_returns,
            expire_seconds=self.ttl,
        )

    async def get_portfolio_returns(self, portfolio_id: str) -> dict:
        cache = await self.redis.get_json(f'portfolio_returns:{portfolio_id}')
        return cache
    
    async def get_usd_brl_history(self) -> dict:
        cache = await self.redis.get_json('usd_brl_history')
        return cache
    
    async def set_usd_brl_history(self, usd_brl_history) -> None:
        await self.redis.set_json(
            'usd_brl_history',
            usd_brl_history,
            expire_seconds=self.ttl,
        )