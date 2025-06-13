# tests/test_options.py
import pandas as pd
import pytest
from urllib.parse import quote

from .conftest import stub_json
from finbrain.exceptions import BadRequest

MARKET = "S&P 500"
ENC_MARKET = quote(MARKET, safe="")  # → 'S%26P%20500'
TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_put_call_raw_ok(client, _activate_responses):
    path = f"putcalldata/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "putCallData": [
            {
                "date": "2024-03-19",
                "ratio": 0.4,
                "callCount": 788319,
                "putCount": 315327,
            }
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    data = client.options.put_call(MARKET, TICKER)
    assert data["ticker"] == TICKER
    assert isinstance(data["putCallData"], list)
    assert data["putCallData"][0]["ratio"] == 0.4


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_put_call_dataframe_ok(client, _activate_responses):
    path = f"putcalldata/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "putCallData": [
            {
                "date": "2024-03-19",
                "ratio": 0.4,
                "callCount": 788319,
                "putCount": 315327,
            },
            {
                "date": "2024-03-18",
                "ratio": 0.42,
                "callCount": 800000,
                "putCount": 335000,
            },
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    df = client.options.put_call(MARKET, TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert pd.Timestamp("2024-03-19") in df.index
    assert df.loc["2024-03-18", "putCount"] == 335000


# ─────────── error mapping ──────────────────────────────────────────────
def test_put_call_bad_request(client, _activate_responses):
    path = f"putcalldata/{ENC_MARKET}/{TICKER}"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)

    with pytest.raises(BadRequest):
        client.options.put_call(MARKET, TICKER)
