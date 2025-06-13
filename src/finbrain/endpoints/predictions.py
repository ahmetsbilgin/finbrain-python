from __future__ import annotations

import re
import pandas as pd
from urllib.parse import quote
from typing import TYPE_CHECKING, Literal, Dict, Any, List

if TYPE_CHECKING:
    from ..client import FinBrainClient


# ------------------------------------------------------------------------- #
_PType = Literal["daily", "monthly"]
_ALLOWED: set[str] = {"daily", "monthly"}
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class PredictionsAPI:
    """
    Price-prediction endpoints

    • `/market/<MARKET>/predictions/<TYPE>`
    • `/ticker/<TICKER>/predictions/<TYPE>`

    where **TYPE** ∈ { `daily`, `monthly` }.
    """

    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client

    # ------------------------------------------------------------------ #
    def ticker(
        self,
        symbol: str,
        *,
        prediction_type: _PType = "daily",
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """
        Single-ticker predictions.

        Parameters
        ----------
        symbol :
            Symbol such as ``AAPL`` (case-insensitive).
        prediction_type :
            ``"daily"`` (10-day horizon) or ``"monthly"`` (12-month horizon).
        as_dataframe :
            Return a **DataFrame** (index =`date`, cols =`main, lower, upper`)
            instead of raw JSON.

        Returns
        -------
        dict | pandas.DataFrame
        """
        _validate(prediction_type)
        path = f"ticker/{symbol.upper()}/predictions/{prediction_type}"
        data: Dict[str, Any] = self._c._request("GET", path)

        if as_dataframe:
            pred = data.get("prediction", {})
            rows: list[dict[str, float]] = []
            for k, v in pred.items():
                if _DATE_RE.fullmatch(k):
                    main, low, high = map(float, v.split(","))
                    rows.append({"date": k, "main": main, "lower": low, "upper": high})
            df = pd.DataFrame(rows).set_index(
                pd.to_datetime(pd.Series([r["date"] for r in rows]))
            )
            df.index.name = "date"
            df.drop(columns="date", inplace=True)
            return df

        return data

    # ------------------------------------------------------------------ #
    def market(
        self,
        market: str,
        *,
        prediction_type: _PType = "daily",
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """
        Predictions for **all** tickers in a market.

        Parameters
        ----------
        market :
            Market name **exactly as FinBrain lists it**
            (e.g. ``"S&P 500"``, ``"Germany DAX"``).  Spaces/`&` are OK.
        prediction_type :
            ``"daily"`` or ``"monthly"``.
        as_dataframe :
            If *True* return a DataFrame (index =`ticker`) with
            ``expectedShort``, ``expectedMid``, ``expectedLong``, and optional
            ``sentimentScore``.

        Returns
        -------
        list[dict] | pandas.DataFrame
        """
        _validate(prediction_type)
        slug = quote(market, safe="")
        path = f"market/{slug}/predictions/{prediction_type}"
        data: List[Dict[str, Any]] = self._c._request("GET", path)

        if as_dataframe:
            rows: list[dict[str, Any]] = []
            for rec in data:
                p = rec.get("prediction", {})
                rows.append(
                    {
                        "ticker": rec["ticker"],
                        "expectedShort": float(p["expectedShort"]),
                        "expectedMid": float(p["expectedMid"]),
                        "expectedLong": float(p["expectedLong"]),
                        "sentimentScore": float(rec.get("sentimentScore", "nan")),
                    }
                )
            df = pd.DataFrame(rows).set_index("ticker")
            return df

        return data


# ---------------------------------------------------------------------- #
def _validate(value: str) -> None:
    if value not in _ALLOWED:
        raise ValueError("prediction_type must be 'daily' or 'monthly'")
