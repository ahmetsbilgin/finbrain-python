# tests/test_options.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_put_call_raw_ok(client, _activate_responses):
    path = f"put-call-ratio/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "data": [
            {
                "date": "2024-01-15",
                "ratio": 0.85,
                "callVolume": 1200,
                "putVolume": 1020,
                "totalVolume": 2220,
                "price": 155.0,
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.options.put_call(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["data"], list)
    assert data["data"][0]["ratio"] == 0.85


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_put_call_dataframe_ok(client, _activate_responses):
    path = f"put-call-ratio/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "data": [
            {
                "date": "2024-01-15",
                "ratio": 0.85,
                "callVolume": 1200,
                "putVolume": 1020,
                "totalVolume": 2220,
                "price": 155.0,
            },
            {
                "date": "2024-01-14",
                "ratio": 0.90,
                "callVolume": 1100,
                "putVolume": 990,
                "totalVolume": 2090,
                "price": 153.0,
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.options.put_call(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"ratio", "callVolume", "putVolume", "totalVolume", "price"}
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert pd.Timestamp("2024-01-14") in df.index
    assert df.loc["2024-01-15", "ratio"] == 0.85
    assert df.loc["2024-01-14", "putVolume"] == 990
    assert df.loc["2024-01-14", "totalVolume"] == 2090


# ─────────── error mapping ──────────────────────────────────────────────
def test_put_call_bad_request(client, _activate_responses):
    path = f"put-call-ratio/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.options.put_call(symbol=TICKER)
