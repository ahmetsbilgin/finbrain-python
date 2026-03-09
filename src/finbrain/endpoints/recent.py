from __future__ import annotations
import pandas as pd
from typing import TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from ..client import FinBrainClient


class RecentAPI:
    """
    Recent data endpoints (v2) — latest data across all tracked stocks.
    """

    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client

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
    def _unwrap(data):
        """v2 recent responses wrap rows in ``{"data": [...], "summary": {...}}``."""
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data

    def news(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """
        Get most recent news articles across all tracked stocks.

        Parameters
        ----------
        limit :
            Maximum number of articles (default 100, max 20000).
        market :
            Optional market filter.
        region :
            Optional region filter.
        as_dataframe :
            If *True*, return a pandas DataFrame.

        Returns
        -------
        list[dict] | pandas.DataFrame
        """
        params = self._build_params(limit=limit, market=market, region=region)
        data = self._c._request("GET", "recent/news", params=params or None)
        rows = self._unwrap(data)

        if as_dataframe and isinstance(rows, list):
            return pd.DataFrame(rows)
        return rows

    def analyst_ratings(
        self,
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """
        Get most recent analyst ratings across all tickers.

        Parameters
        ----------
        limit :
            Maximum number of ratings (default 100, max 20000).
        market :
            Optional market filter.
        region :
            Optional region filter.
        as_dataframe :
            If *True*, return a pandas DataFrame.

        Returns
        -------
        list[dict] | pandas.DataFrame
        """
        params = self._build_params(limit=limit, market=market, region=region)
        data = self._c._request("GET", "recent/analyst-ratings", params=params or None)
        rows = self._unwrap(data)

        if as_dataframe and isinstance(rows, list):
            return pd.DataFrame(rows)
        return rows
