# src/finbrain/endpoints/available.py
from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:  # imported only by type-checkers (mypy, pyright…)
    from ..client import FinBrainClient


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
        return data.get("availableMarkets", [])

    # ------------------------------------------------------------
    def tickers(self, type_: str) -> List[Dict[str, str]]:
        """
        Return all tickers for the supplied *TYPE* exactly as
        documented by FinBrain.

        Parameters
        ----------
        type_ :
            Path segment after ``/available/tickers/`` - whatever the
            FinBrain docs list (e.g. ``sp500``, ``nasdaq``, ``dax`` …).

        Returns
        -------
        list[dict]
            Each element looks like::

                {
                    "ticker": "AAPL",
                    "name":   "Apple Inc.",
                    "market": "S&P 500"
                }
        """
        path = f"available/tickers/{type_}"
        return self._c._request("GET", path)
