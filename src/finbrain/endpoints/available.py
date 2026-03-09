# src/finbrain/endpoints/available.py
from __future__ import annotations
import pandas as pd
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:  # imported only by type-checkers (mypy, pyright…)
    from ..client import FinBrainClient


class AvailableAPI:
    """
    Wrapper for FinBrain's discovery endpoints
    -------------------------------------------

    • ``/markets``              → list supported markets
    • ``/tickers``              → list tickers (filtered by query params)
    • ``/regions``              → markets grouped by region
    """

    # ------------------------------------------------------------
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client  # reference to the parent client

    # ------------------------------------------------------------
    def markets(
        self,
        *,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """
        Return every market FinBrain supports.

        Each entry contains ``name`` and ``region`` fields.

        Parameters
        ----------
        as_dataframe :
            If *True*, return a ``pd.DataFrame`` instead of a list of dicts.

        Example
        -------
        >>> fb.available.markets()
        [{'name': 'S&P 500', 'region': 'US'}, ...]
        """
        data = self._c._request("GET", "markets")

        if isinstance(data, list):
            rows = data
        else:
            rows = data.get("markets", data.get("availableMarkets", []))

        return pd.DataFrame(rows) if as_dataframe else rows

    # ------------------------------------------------------------
    def tickers(
        self,
        prediction_type: str = "daily",
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """
        List all tickers for which **FinBrain has predictions** of the given type.

        Parameters
        ----------
        prediction_type :
            Either ``"daily"`` or ``"monthly"``.
        limit :
            Maximum number of tickers to return (up to 20000).
        market :
            Filter by market name.
        region :
            Filter by region.
        as_dataframe :
            If *True*, return a ``pd.DataFrame``.

        Returns
        -------
        list[dict] | pandas.DataFrame
        """
        prediction_type = prediction_type.lower()
        if prediction_type not in ("daily", "monthly"):
            raise ValueError("prediction_type must be 'daily' or 'monthly'")

        params: Dict[str, str] = {"type": prediction_type}
        if limit is not None:
            params["limit"] = str(limit)
        if market:
            params["market"] = market
        if region:
            params["region"] = region

        data = self._c._request("GET", "tickers", params=params)

        # v2 API wraps the list in {"tickers": [...]}
        if isinstance(data, dict):
            rows = data.get("tickers", [])
        else:
            rows = data

        return pd.DataFrame(rows) if as_dataframe else rows

    # ------------------------------------------------------------
    def regions(
        self,
        *,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """
        Return markets grouped by region.

        Parameters
        ----------
        as_dataframe :
            If *True*, return a ``pd.DataFrame`` instead of raw JSON.

        Returns
        -------
        list[dict] | pandas.DataFrame
        """
        data = self._c._request("GET", "regions")

        if isinstance(data, list):
            rows = data
        else:
            rows = data.get("regions", [])

        return pd.DataFrame(rows) if as_dataframe else rows
