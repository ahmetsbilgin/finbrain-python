from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Dict, Any

if TYPE_CHECKING:  # imported only by type-checkers
    from ..client import FinBrainClient


_PType = Literal["daily", "monthly"]  # helper type alias
_ALLOWED_TYPES: set[str] = {"daily", "monthly"}


class PredictionsAPI:
    """
    FinBrain price-prediction endpoints.

    • ``/market/<MARKET_NAME>/predictions/<TYPE>``
    • ``/ticker/<TICKER>/predictions/<TYPE>``

    where **TYPE** ∈ { ``daily``, ``monthly`` }.
    """

    # ------------------------------------------------------------------ #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client  # reference to the main client

    # ------------------------------------------------------------------ #
    def ticker(
        self,
        ticker: str,
        *,
        prediction_type: _PType = "daily",
    ) -> Dict[str, Any]:
        """
        Predictions for a **single ticker**.

        Parameters
        ----------
        ticker :
            Symbol such as ``AAPL``.  Case-insensitive (converted to upper-case).
        prediction_type :
            ``"daily"`` (10-day horizon) or ``"monthly"`` (12-month horizon).

        Returns
        -------
        dict
            Raw JSON exactly as FinBrain returns.
        """
        _validate_type(prediction_type)
        path = f"ticker/{ticker.upper()}/predictions/{prediction_type}"
        return self._c._request("GET", path)

    # ------------------------------------------------------------------ #
    def market(
        self,
        market: str,
        *,
        prediction_type: _PType = "daily",
    ) -> Dict[str, Any]:
        """
        Predictions for **all tickers** in a market segment.

        Parameters
        ----------
        market :
            Path segment such as ``sp500`` or ``nasdaq``.
        prediction_type :
            ``"daily"`` (10-day horizon) or ``"monthly"`` (12-month horizon).

        Returns
        -------
        list[dict]
            Each element contains ``ticker``, ``name``, ``prediction`` and
            optionally ``sentimentScore`` (see docs).
        """
        _validate_type(prediction_type)
        path = f"market/{market}/predictions/{prediction_type}"
        return self._c._request("GET", path)


# ---------------------------------------------------------------------- #
# helper                                                                 #
# ---------------------------------------------------------------------- #
def _validate_type(value: str) -> None:
    if value not in _ALLOWED_TYPES:
        raise ValueError(
            f"prediction_type must be 'daily' or 'monthly' (got '{value}')"
        )
