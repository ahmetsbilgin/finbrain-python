from __future__ import annotations

import re
import pandas as pd
from urllib.parse import quote
from typing import TYPE_CHECKING, Literal, Dict, Any, List

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


_PType = Literal["daily", "monthly"]
_ALLOWED: set[str] = {"daily", "monthly"}
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class AsyncPredictionsAPI:
    """Async wrapper for price-prediction endpoints."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    async def ticker(
        self,
        symbol: str,
        *,
        prediction_type: _PType = "daily",
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """Single-ticker predictions (async)."""
        _validate(prediction_type)
        path = f"ticker/{symbol.upper()}/predictions/{prediction_type}"
        data: Dict[str, Any] = await self._c._request("GET", path)

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

    async def market(
        self,
        market: str,
        *,
        prediction_type: _PType = "daily",
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Predictions for all tickers in a market (async)."""
        _validate(prediction_type)
        slug = quote(market, safe="")
        path = f"market/{slug}/predictions/{prediction_type}"
        data: List[Dict[str, Any]] = await self._c._request("GET", path)

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


def _validate(value: str) -> None:
    if value not in _ALLOWED:
        raise ValueError("prediction_type must be 'daily' or 'monthly'")
