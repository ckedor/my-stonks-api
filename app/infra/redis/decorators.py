def cached(ttl=60):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached_result = await self.redis.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = await func(self, *args, **kwargs)
            await self.redis.set(cache_key, result, ex=ttl)
            return result
        return wrapper
    return decorator
    