from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING, Literal, Dict, Any, List

if TYPE_CHECKING:
    from ..client import FinBrainClient


# ------------------------------------------------------------------------- #
_PType = Literal["daily", "monthly"]
_ALLOWED: set[str] = {"daily", "monthly"}


class PredictionsAPI:
    """
    Price-prediction endpoint

    • ``/predictions/<TYPE>/<TICKER>``

    where **TYPE** is ``daily`` or ``monthly``.
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
            Return a **DataFrame** (index = ``date``, cols = ``mid, lower, upper``)
            instead of raw JSON.

        Returns
        -------
        dict | pandas.DataFrame
        """
        _validate(prediction_type)
        path = f"predictions/{prediction_type}/{symbol.upper()}"
        data: Dict[str, Any] = self._c._request("GET", path)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("predictions", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data


# ---------------------------------------------------------------------- #
def _validate(value: str) -> None:
    if value not in _ALLOWED:
        raise ValueError("prediction_type must be 'daily' or 'monthly'")
