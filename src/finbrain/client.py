from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional
import requests
from urllib.parse import urljoin

from .plotting import _PlotNamespace
from .exceptions import http_error_to_exception, InvalidResponse
from . import __version__

from .endpoints.available import AvailableAPI
from .endpoints.predictions import PredictionsAPI
from .endpoints.sentiments import SentimentsAPI
from .endpoints.app_ratings import AppRatingsAPI
from .endpoints.analyst_ratings import AnalystRatingsAPI
from .endpoints.house_trades import HouseTradesAPI
from .endpoints.senate_trades import SenateTradesAPI
from .endpoints.insider_transactions import InsiderTransactionsAPI
from .endpoints.linkedin_data import LinkedInDataAPI
from .endpoints.options import OptionsAPI
from .endpoints.news import NewsAPI
from .endpoints.screener import ScreenerAPI
from .endpoints.recent import RecentAPI
from .endpoints.corporate_lobbying import CorporateLobbyingAPI


# Which status codes merit a retry
_RETRYABLE_STATUS = {500}
# How long to wait between retries   (2, 4, 8 … seconds)
_BACKOFF_BASE = 2


class FinBrainClient:
    """
    Thin wrapper around the FinBrain REST API (v2).
    """

    DEFAULT_BASE_URL = "https://api.finbrain.tech/v2/"

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

        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"finbrain-python/{__version__}"
        self.session.headers["Authorization"] = f"Bearer {self.api_key}"

        self.timeout = timeout
        self.retries = retries
        self.last_meta: dict | None = None

        # expose plotting under .plot
        self.plot = _PlotNamespace(self)

        # wire endpoint helpers
        self.available = AvailableAPI(self)
        self.predictions = PredictionsAPI(self)
        self.sentiments = SentimentsAPI(self)
        self.app_ratings = AppRatingsAPI(self)
        self.analyst_ratings = AnalystRatingsAPI(self)
        self.house_trades = HouseTradesAPI(self)
        self.senate_trades = SenateTradesAPI(self)
        self.insider_transactions = InsiderTransactionsAPI(self)
        self.linkedin_data = LinkedInDataAPI(self)
        self.options = OptionsAPI(self)
        self.news = NewsAPI(self)
        self.screener = ScreenerAPI(self)
        self.recent = RecentAPI(self)
        self.corporate_lobbying = CorporateLobbyingAPI(self)

    # ---------- private helpers ----------
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Perform a single HTTP request with Bearer auth and retries.

        The v2 API returns responses in an envelope:
        ``{"success": true, "data": ..., "meta": {...}}``.
        This method auto-unwraps the envelope, returning just ``data``.

        Raises
        ------
        FinBrainError
            Mapped from HTTP status via ``http_error_to_exception``.
        InvalidResponse
            If the body is not valid JSON.
        """
        url = urljoin(self.base_url, path)

        for attempt in range(self.retries + 1):
            try:
                resp = self.session.request(
                    method, url, params=params, timeout=self.timeout
                )
            except requests.RequestException as exc:
                # Network problem → retry if budget allows, else wrap into FinBrainError
                if attempt == self.retries:
                    raise InvalidResponse(f"Network error: {exc}") from exc
                time.sleep(_BACKOFF_BASE**attempt)
                continue

            # ── Happy path ────────────────────────────────────
            if resp.ok:  # 2xx / 3xx
                try:
                    body = resp.json()
                except ValueError as exc:
                    raise InvalidResponse("Response body is not valid JSON") from exc

                # Unwrap v2 envelope
                if isinstance(body, dict) and "success" in body:
                    self.last_meta = body.get("meta")
                    return body.get("data")
                return body

            # ── Error path ───────────────────────────────────
            if resp.status_code in _RETRYABLE_STATUS and attempt < self.retries:
                # 500 – exponential back-off then retry
                time.sleep(_BACKOFF_BASE**attempt)
                continue

            # No more retries → raise the mapped FinBrainError
            raise http_error_to_exception(resp)
