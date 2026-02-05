# app/infra/integrations/tesouro_client.py
import asyncio
import gzip
import time
from datetime import date
from io import StringIO

import pandas as pd
from redis.asyncio import Redis

from app.config.logger import logger
from app.config.settings import settings
from app.infra.http import AsyncHttpClient


class TesouroClient:
    
    _cached_df: pd.DataFrame | None = None
    _cache_date: date | None = None
    _cache_lock: asyncio.Lock | None = None

    REDIS_KEY_PREFIX = 'tesouro:csv:gzip'
    REDIS_TTL_SECONDS = 86400  # 24 horas

    def __init__(self):
        self.http = AsyncHttpClient(
            timeout=60.0,
            max_retries=3,
            backoff_factor=1.0,
        )
        self._redis: Redis | None = None

    async def _get_redis(self) -> Redis:
        if self._redis is None:
            # decode_responses=False para permitir dados binários (gzip)
            self._redis = Redis.from_url(settings.REDIS_URL, decode_responses=False)
        return self._redis

    @classmethod
    def _get_lock(cls) -> asyncio.Lock:
        if cls._cache_lock is None:
            cls._cache_lock = asyncio.Lock()
        return cls._cache_lock

    def _get_redis_key(self) -> str:
        """Chave do Redis com a data de hoje."""
        return f'{self.REDIS_KEY_PREFIX}:{date.today().isoformat()}'

    async def get_taxas_precos_tesouro(self):
        today = date.today()

        if TesouroClient._cached_df is not None and TesouroClient._cache_date == today:
            logger.info('[TIMING] Tesouro CSV from memory cache')
            return TesouroClient._cached_df

        async with self._get_lock():
            if TesouroClient._cached_df is not None and TesouroClient._cache_date == today:
                logger.info('[TIMING] Tesouro CSV from memory cache (after lock)')
                return TesouroClient._cached_df

            try:
                redis = await self._get_redis()
                redis_key = self._get_redis_key()

                start = time.perf_counter()
                cached_gzip = await redis.get(redis_key)

                if cached_gzip:
                    csv_content = gzip.decompress(cached_gzip).decode('utf-8')
                    logger.info(
                        f'[TIMING] Tesouro CSV from Redis (gzip): {time.perf_counter() - start:.2f}s '
                        f'({len(cached_gzip)/1024/1024:.1f}MB compressed)'
                    )
                    result = await self._parse_csv(csv_content)
                    TesouroClient._cached_df = result
                    TesouroClient._cache_date = today
                    return result

                taxas_precos_history_url = 'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv'

                start_download = time.perf_counter()
                response = await self.http.get(taxas_precos_history_url, parse_json=False)
                download_time = time.perf_counter() - start_download
                logger.info(
                    f'[TIMING] Tesouro CSV download: {download_time:.2f}s ({len(response)/1024/1024:.1f}MB)'
                )

                compressed = gzip.compress(response.encode('utf-8'), compresslevel=6)
                await redis.set(redis_key, compressed, ex=self.REDIS_TTL_SECONDS)
                logger.info(
                    f'[TIMING] Tesouro CSV saved to Redis (gzip): {len(compressed)/1024/1024:.1f}MB'
                )

                result = await self._parse_csv(response)
                TesouroClient._cached_df = result
                TesouroClient._cache_date = today

                return result
            except Exception as e:
                logger.error(f'Error fetching Tesouro CSV: {e}')
                return None

    async def _parse_csv(self, csv_content: str) -> pd.DataFrame:
        """Parse CSV em thread separada para não bloquear o event loop."""
        def parse():
            data = pd.read_csv(StringIO(csv_content), sep=';', decimal=',')
            data['Data Base'] = pd.to_datetime(data['Data Base'], format='%d/%m/%Y', dayfirst=True)
            data['Data Vencimento'] = pd.to_datetime(
                data['Data Vencimento'], format='%d/%m/%Y', dayfirst=True
            )
            return data

        start_parse = time.perf_counter()
        result = await asyncio.to_thread(parse)
        parse_time = time.perf_counter() - start_parse
        logger.info(f'[TIMING] Tesouro CSV parsing: {parse_time:.2f}s')
        return result

    async def get_precos_tesouro(self, tipo_titulo, vencimento):
        taxas_precos_df = await self.get_taxas_precos_tesouro()
        df = taxas_precos_df[taxas_precos_df['Tipo Titulo'] == tipo_titulo]
        df = df[df['Data Vencimento'] == pd.to_datetime(vencimento)]
        df = df.sort_values(by='Data Base').rename(
            columns={
                'Taxa Compra Manha': 'fee',
                'PU Venda Manha': 'price',
                'Data Base': 'date',
            }
        )
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', dayfirst=True)
        df = df.set_index('date').asfreq('D')
        df['close'] = df['price'].ffill().copy()
        df = df.reset_index()
        df['currency'] = 'BRL'
        return df[['date', 'close', 'currency']]

    async def get_quotes(
        self,
        treasury_type,
        treasury_maturity_date,
        start_date=None,
        end_date=None,
    ):
        history_df = await self.get_precos_tesouro(treasury_type, treasury_maturity_date)

        if start_date:
            history_df = history_df[history_df['date'] >= pd.to_datetime(start_date).normalize()]
        if end_date:
            history_df = history_df[history_df['date'] <= pd.to_datetime(end_date).normalize()]

        return {
            'currency': 'BRL',
            'quotes': history_df[['date', 'close']],
        }

    async def close(self):
        """Close the HTTP client."""
        await self.http.close()
