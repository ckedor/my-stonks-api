# app/infra/http/async_http_client.py
"""
Async HTTP client with retry, backoff exponencial, and common utilities.
"""

import asyncio
from typing import Any, Optional

import httpx

from app.config.logger import logger


class AsyncHttpClient:
    """
    Async HTTP client with built-in retry logic and exponential backoff.
    
    Features:
    - Automatic retries with exponential backoff
    - Configurable timeout
    - Token/header injection
    - JSON parsing by default
    - Connection pooling via httpx.AsyncClient
    """
    
    def __init__(
        self,
        base_url: str = "",
        headers: Optional[dict] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        retry_statuses: tuple = (429, 500, 502, 503, 504),
    ):
        self.base_url = base_url.rstrip("/")
        self.default_headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_statuses = retry_statuses
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy initialization of the async client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.default_headers,
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def set_header(self, key: str, value: str) -> None:
        """Add or update a default header."""
        self.default_headers[key] = value

    def set_bearer_token(self, token: str) -> None:
        """Set Bearer token for Authorization header."""
        self.set_header("Authorization", f"Bearer {token}")

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
        parse_json: bool = True,
    ) -> Any:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: URL endpoint (will be joined with base_url)
            params: Query parameters
            json: JSON body data
            data: Form data
            headers: Additional headers for this request
            parse_json: If True, parse response as JSON
            
        Returns:
            Parsed JSON response or raw response text
            
        Raises:
            httpx.HTTPStatusError: If request fails after all retries
        """
        client = await self._get_client()
        url = endpoint if endpoint.startswith("http") else endpoint
        
        request_headers = {**self.default_headers, **(headers or {})}
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    data=data,
                    headers=request_headers,
                )
                
                # Check if we should retry based on status code
                if response.status_code in self.retry_statuses and attempt < self.max_retries:
                    wait_time = self.backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"HTTP {response.status_code} for {url}. "
                        f"Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                if parse_json:
                    return response.json()
                return response.text
                
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self.backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Timeout for {url}. Retrying in {wait_time:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {self.max_retries} retries: {url}")
                    raise
                    
            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx) except rate limiting
                if e.response.status_code < 500 and e.response.status_code != 429:
                    raise
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self.backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"HTTP error {e.response.status_code} for {url}. "
                        f"Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
                    
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error for {url}: {e}")
                raise
        
        if last_exception:
            raise last_exception

    async def get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        parse_json: bool = True,
    ) -> Any:
        """Make a GET request."""
        return await self._request("GET", endpoint, params=params, headers=headers, parse_json=parse_json)

    async def post(
        self,
        endpoint: str,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        parse_json: bool = True,
    ) -> Any:
        """Make a POST request."""
        return await self._request(
            "POST", endpoint, params=params, json=json, data=data, headers=headers, parse_json=parse_json
        )

    async def put(
        self,
        endpoint: str,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        parse_json: bool = True,
    ) -> Any:
        """Make a PUT request."""
        return await self._request(
            "PUT", endpoint, params=params, json=json, data=data, headers=headers, parse_json=parse_json
        )

    async def delete(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        parse_json: bool = True,
    ) -> Any:
        """Make a DELETE request."""
        return await self._request("DELETE", endpoint, params=params, headers=headers, parse_json=parse_json)

    async def __aenter__(self):
        """Context manager entry."""
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
