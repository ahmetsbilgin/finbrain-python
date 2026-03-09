from __future__ import annotations
import pandas as pd
from typing import TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


class AsyncScreenerAPI:
    """Async screener endpoints (v2) — cross-ticker screening."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    # ── helpers ────────────────────────────────────────────────

    @staticmethod
    def _build_params(
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
    ) -> Dict[str, str]:
        params: Dict[str, str] = {}
        if limit is not None:
            params["limit"] = str(limit)
        if market:
            params["market"] = market
        if region:
            params["region"] = region
        return params

    @staticmethod
    def _require_market_or_region(market: str | None, region: str | None) -> None:
        if not market and not region:
            raise ValueError(
                "Either 'market' or 'region' must be provided for this screener endpoint."
            )

    @staticmethod
    def _to_df(data: Any) -> pd.DataFrame:
        if isinstance(data, list):
            df = pd.DataFrame(data)
            if not df.empty and "symbol" in df.columns:
                df.set_index("symbol", inplace=True)
            return df
        return pd.DataFrame()

    @staticmethod
    def _unwrap(data: Any) -> Any:
        """v2 screener responses wrap rows in ``{"data": [...], "summary": {...}}``."""
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data

    async def _get(self, path: str, params: Dict[str, str], as_dataframe: bool) -> Any:
        data = await self._c._request("GET", path, params=params or None)
        rows = self._unwrap(data)
        return self._to_df(rows) if as_dataframe else rows

    # ── sentiment ─────────────────────────────────────────────

    async def sentiment(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen sentiment across tickers. Requires ``market`` or ``region``."""
        self._require_market_or_region(market, region)
        params = self._build_params(limit=limit, market=market, region=region)
        return await self._get("screener/sentiment", params, as_dataframe)

    # ── analyst ratings ───────────────────────────────────────

    async def analyst_ratings(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen analyst ratings across tickers."""
        params = self._build_params(limit=limit, market=market, region=region)
        return await self._get("screener/analyst-ratings", params, as_dataframe)

    # ── insider trading ───────────────────────────────────────

    async def insider_trading(
        self,
        *,
        limit: int | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen insider trades across all tickers."""
        params = self._build_params(limit=limit)
        return await self._get("screener/insider-trading", params, as_dataframe)

    # ── congress house ────────────────────────────────────────

    async def congress_house(
        self,
        *,
        limit: int | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen House trades across all tickers."""
        params = self._build_params(limit=limit)
        return await self._get("screener/congress/house", params, as_dataframe)

    # ── congress senate ───────────────────────────────────────

    async def congress_senate(
        self,
        *,
        limit: int | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen Senate trades across all tickers."""
        params = self._build_params(limit=limit)
        return await self._get("screener/congress/senate", params, as_dataframe)

    # ── news ──────────────────────────────────────────────────

    async def news(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen news across tickers."""
        params = self._build_params(limit=limit, market=market, region=region)
        return await self._get("screener/news", params, as_dataframe)

    # ── put-call ratio ────────────────────────────────────────

    async def put_call_ratio(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen put/call ratio across tickers."""
        params = self._build_params(limit=limit, market=market, region=region)
        return await self._get("screener/put-call-ratio", params, as_dataframe)

    # ── linkedin ──────────────────────────────────────────────

    async def linkedin(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen LinkedIn data. Requires ``market`` or ``region``."""
        self._require_market_or_region(market, region)
        params = self._build_params(limit=limit, market=market, region=region)
        return await self._get("screener/linkedin", params, as_dataframe)

    # ── app ratings ───────────────────────────────────────────

    async def app_ratings(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen app ratings. Requires ``market`` or ``region``."""
        self._require_market_or_region(market, region)
        params = self._build_params(limit=limit, market=market, region=region)
        return await self._get("screener/app-ratings", params, as_dataframe)

    # ── predictions daily ─────────────────────────────────────

    async def predictions_daily(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen daily (10-day) predictions across tickers."""
        params = self._build_params(limit=limit, market=market, region=region)
        return await self._get("screener/predictions/daily", params, as_dataframe)

    # ── predictions monthly ───────────────────────────────────

    async def predictions_monthly(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Screen monthly (12-month) predictions across tickers."""
        params = self._build_params(limit=limit, market=market, region=region)
        return await self._get("screener/predictions/monthly", params, as_dataframe)
