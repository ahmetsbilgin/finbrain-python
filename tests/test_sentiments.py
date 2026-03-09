# tests/test_sentiments.py
import pytest
import pandas as pd
from finbrain.exceptions import BadRequest
from .conftest import stub_json, wrap_v2

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_sentiments_raw_ok(client, _activate_responses):
    """Default behaviour returns the original dict."""
    path = f"sentiment/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "data": [
            {"date": "2024-01-02", "score": 0.123},
            {"date": "2024-01-01", "score": -0.045},
        ],
    })

    stub_json(
        _activate_responses,
        "GET",
        path,
        payload,
        params={"startDate": "2024-01-01", "endDate": "2024-01-02"},
    )

    data = client.sentiments.ticker(
        symbol=TICKER,
        date_from="2024-01-01",
        date_to="2024-01-02",
    )

    assert data["symbol"] == "AMZN"
    assert "data" in data
    assert len(data["data"]) == 2


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_sentiments_dataframe_ok(client, _activate_responses):
    """as_dataframe=True returns a DataFrame indexed by date."""
    path = f"sentiment/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "data": [
            {"date": "2024-01-02", "score": 0.123},
            {"date": "2024-01-01", "score": -0.045},
        ],
    })

    stub_json(
        _activate_responses,
        "GET",
        path,
        payload,
        params={"startDate": "2024-01-01", "endDate": "2024-01-02"},
    )

    df = client.sentiments.ticker(
        symbol=TICKER,
        date_from="2024-01-01",
        date_to="2024-01-02",
        as_dataframe=True,
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"sentiment"}
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-02") in df.index
    assert pd.Timestamp("2024-01-01") in df.index
    assert df.loc["2024-01-02", "sentiment"] == 0.123
    assert df.loc["2024-01-01", "sentiment"] == -0.045


# ─────────── error mapping ──────────────────────────────────────────────
def test_sentiments_bad_request(client, _activate_responses):
    path = f"sentiment/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.sentiments.ticker(symbol=TICKER)
