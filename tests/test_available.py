# tests/test_available.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest


# ─────────── markets ────────────────────────────────────────────────────
def test_markets_ok(client, _activate_responses):
    stub_json(
        _activate_responses,
        "GET",
        "markets",
        wrap_v2([{"name": "S&P 500", "region": "US"}, {"name": "NASDAQ", "region": "US"}]),
    )
    data = client.available.markets()
    assert isinstance(data, list)
    assert data[0]["name"] == "S&P 500"


def test_markets_bad_request(client, _activate_responses):
    stub_json(
        _activate_responses,
        "GET",
        "markets",
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )
    with pytest.raises(BadRequest):
        client.available.markets()


# ─────────── tickers ────────────────────────────────────────────────────
def test_tickers_list_ok(client, _activate_responses):
    path = "tickers"
    payload = wrap_v2({
        "tickers": [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
        ]
    })
    stub_json(_activate_responses, "GET", path, payload, params={"type": "daily"})

    data = client.available.tickers("daily")
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["symbol"] == "AAPL"


def test_tickers_dataframe_ok(client, _activate_responses):
    path = "tickers"
    payload = wrap_v2({
        "tickers": [
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
        ]
    })
    stub_json(_activate_responses, "GET", path, payload, params={"type": "daily"})

    df = client.available.tickers("daily", as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.loc[0, "symbol"] == "AMZN"


def test_tickers_invalid_type(client):
    with pytest.raises(ValueError):
        client.available.tickers("weekly")
