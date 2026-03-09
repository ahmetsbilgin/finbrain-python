from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING, Literal, Dict, Any

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


_PType = Literal["daily", "monthly"]
_ALLOWED: set[str] = {"daily", "monthly"}


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
        path = f"predictions/{prediction_type}/{symbol.upper()}"
        data: Dict[str, Any] = await self._c._request("GET", path)

        if as_dataframe:
            rows = data.get("predictions", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data


def _validate(value: str) -> None:
    if value not in _ALLOWED:
        raise ValueError("prediction_type must be 'daily' or 'monthly'")
