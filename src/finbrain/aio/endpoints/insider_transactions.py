from __future__ import annotations
import pandas as pd
from urllib.parse import quote
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


class AsyncInsiderTransactionsAPI:
    """Async wrapper for /insidertransactions endpoints."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    async def ticker(
        self,
        market: str,
        symbol: str,
        *,
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """Insider transactions for symbol in market (async)."""
        market_slug = quote(market, safe="")
        path = f"insidertransactions/{market_slug}/{symbol.upper()}"
        data: Dict[str, Any] = await self._c._request("GET", path)

        if as_dataframe:
            rows = data.get("insiderTransactions", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                _fmt = "%b %d '%y"
                dt = pd.to_datetime(df["date"], format=_fmt, errors="coerce")
                if dt.isna().any():
                    dt = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)
                df["date"] = dt
                df.set_index("date", inplace=True)
            return df

        return data
