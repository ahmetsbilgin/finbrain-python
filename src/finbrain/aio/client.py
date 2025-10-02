from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, Optional
import httpx
from urllib.parse import urljoin

from ..exceptions import http_error_to_exception, InvalidResponse
from .. import __version__

from .endpoints.available import AsyncAvailableAPI
from .endpoints.predictions import AsyncPredictionsAPI
from .endpoints.sentiments import AsyncSentimentsAPI
from .endpoints.app_ratings import AsyncAppRatingsAPI
from .endpoints.analyst_ratings import AsyncAnalystRatingsAPI
from .endpoints.house_trades import AsyncHouseTradesAPI
from .endpoints.insider_transactions import AsyncInsiderTransactionsAPI
from .endpoints.linkedin_data import AsyncLinkedInDataAPI
from .endpoints.options import AsyncOptionsAPI


# Which status codes merit a retry
_RETRYABLE_STATUS = {500}
# How long to wait between retries   (2, 4, 8 … seconds)
_BACKOFF_BASE = 2


class AsyncFinBrainClient:
    """
    Async wrapper around the FinBrain REST API using httpx.

    Example
    -------
    >>> import asyncio
    >>> from finbrain.aio import AsyncFinBrainClient
    >>>
    >>> async def main():
    ...     async with AsyncFinBrainClient(api_key="YOUR_KEY") as client:
    ...         markets = await client.available.markets()
    ...         print(markets)
    >>>
    >>> asyncio.run(main())
    """

    DEFAULT_BASE_URL = "https://api.finbrain.tech/v1/"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str | None = None,
        timeout: float = 10,
        retries: int = 3,
    ):
        self.api_key = api_key or os.getenv("FINBRAIN_API_KEY")
        if not self.api_key:
            raise ValueError("FinBrain API key missing")
        self.base_url = base_url or self.DEFAULT_BASE_URL

        self._client: Optional[httpx.AsyncClient] = None
        self.timeout = timeout
        self.retries = retries

        # wire endpoint helpers
        self.available = AsyncAvailableAPI(self)
        self.predictions = AsyncPredictionsAPI(self)
        self.sentiments = AsyncSentimentsAPI(self)
        self.app_ratings = AsyncAppRatingsAPI(self)
        self.analyst_ratings = AsyncAnalystRatingsAPI(self)
        self.house_trades = AsyncHouseTradesAPI(self)
        self.insider_transactions = AsyncInsiderTransactionsAPI(self)
        self.linkedin_data = AsyncLinkedInDataAPI(self)
        self.options = AsyncOptionsAPI(self)

    async def __aenter__(self) -> "AsyncFinBrainClient":
        """Context manager entry."""
        self._client = httpx.AsyncClient(
            headers={"User-Agent": f"finbrain-python/{__version__}"},
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def close(self) -> None:
        """Explicitly close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    # ---------- private helpers ----------
    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Perform a single HTTP request with auth token and retries.

        Raises
        ------
        FinBrainError
            Mapped from HTTP status via ``http_error_to_exception``.
        InvalidResponse
            If the body is not valid JSON.
        RuntimeError
            If the client is not initialized (use context manager or create client).
        """
        if self._client is None:
            raise RuntimeError(
                "AsyncFinBrainClient not initialized. Use 'async with' context manager."
            )

        params = params.copy() if params else {}
        params["token"] = self.api_key  # FinBrain authentication
        url = urljoin(self.base_url, path)

        for attempt in range(self.retries + 1):
            try:
                resp = await self._client.request(method, url, params=params)
            except httpx.RequestError as exc:
                # Network problem → retry if budget allows, else wrap into FinBrainError
                if attempt == self.retries:
                    raise InvalidResponse(f"Network error: {exc}") from exc
                await asyncio.sleep(_BACKOFF_BASE**attempt)
                continue

            # ── Happy path ────────────────────────────────────
            if resp.is_success:  # 2xx / 3xx
                try:
                    return resp.json()
                except ValueError as exc:
                    raise InvalidResponse("Response body is not valid JSON") from exc

            # ── Error path ───────────────────────────────────
            if resp.status_code in _RETRYABLE_STATUS and attempt < self.retries:
                # 500 – exponential back-off then retry
                await asyncio.sleep(_BACKOFF_BASE**attempt)
                continue

            # No more retries → raise the mapped FinBrainError
            # Convert httpx.Response to requests-like interface for error handler
            raise _httpx_error_to_exception(resp)


def _httpx_error_to_exception(resp: httpx.Response):
    """
    Convert httpx.Response to the exception format expected by http_error_to_exception.

    Creates a minimal requests-like interface for compatibility.
    """
    # Create a minimal requests-like response object
    class _RequestsLikeResponse:
        def __init__(self, httpx_resp: httpx.Response):
            self.status_code = httpx_resp.status_code
            self.reason = httpx_resp.reason_phrase
            self.text = httpx_resp.text

        def json(self):
            import json

            return json.loads(self.text)

    return http_error_to_exception(_RequestsLikeResponse(resp))
