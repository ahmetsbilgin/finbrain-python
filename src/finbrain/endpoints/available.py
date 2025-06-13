# src/finbrain/endpoints/available.py
from __future__ import annotations
import pandas as pd
from typing import TYPE_CHECKING, Literal, List, Dict, Any

if TYPE_CHECKING:  # imported only by type-checkers (mypy, pyright…)
    from ..client import FinBrainClient

_PType = Literal["daily", "monthly"]
_ALLOWED: set[str] = {"daily", "monthly"}


class AvailableAPI:
    """
    Wrapper for FinBrain's **/available** endpoints
    -----------------------------------------------

    • ``/available/markets``                → list supported indices
    • ``/available/tickers/<TYPE>``         → list tickers for that *TYPE*

      The docs call the path segment “TYPE”; it might be a market name
      (``sp500`` / ``nasdaq``) or something else. We don't guess—caller passes it.
    """

    # ------------------------------------------------------------
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client  # reference to the parent client

    # ------------------------------------------------------------
    def markets(self) -> List[str]:
        """
        Return every market index string FinBrain supports.

        Example
        -------
        >>> fb.available.markets()
        ['S&P 500', 'NASDAQ', ...]
        """
        data = self._c._request("GET", "available/markets")

        if isinstance(data, List):
            return data

        return data.get("availableMarkets", [])

    # ------------------------------------------------------------
    def tickers(
        self,
        prediction_type: _PType,
        *,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """
        List all tickers for which **FinBrain has predictions** of the given type.

        Parameters
        ----------
        prediction_type :
            Either ``"daily"`` (10-day horizon predictions) or
            ``"monthly"`` (12-month horizon predictions).  Case-insensitive.
        as_dataframe :
            If *True*, return a ``pd.DataFrame``;
            otherwise return the raw list of dicts.

        Returns
        -------
        list[dict] | pandas.DataFrame
            Each row / dict contains at least::

                {
                    "ticker": "AAPL",
                    "name":   "Apple Inc.",
                    "market": "S&P 500"
                }
        """
        prediction_type = prediction_type.lower()
        if prediction_type not in _ALLOWED:
            raise ValueError("prediction_type must be 'daily' or 'monthly'")

        path = f"available/tickers/{prediction_type}"
        data: List[Dict[str, Any]] = self._c._request("GET", path)

        return pd.DataFrame(data) if as_dataframe else data
