# tests/test_available.py
import pandas as pd
import pytest

from .conftest import stub_json
from finbrain.exceptions import BadRequest


# ─────────── markets ────────────────────────────────────────────────────
def test_markets_ok(client, _activate_responses):
    stub_json(
        _activate_responses,
        "GET",
        "available/markets",
        {"availableMarkets": ["S&P 500", "NASDAQ"]},
    )
    assert client.available.markets() == ["S&P 500", "NASDAQ"]


def test_markets_bad_request(client, _activate_responses):
    stub_json(
        _activate_responses,
        "GET",
        "available/markets",
        {"message": "oops"},
        status=400,
    )
    with pytest.raises(BadRequest):
        client.available.markets()


# ─────────── tickers ────────────────────────────────────────────────────
def test_tickers_list_ok(client, _activate_responses):
    path = "available/tickers/daily"
    payload = [
        {"ticker": "AAPL", "name": "Apple Inc.", "market": "S&P 500"},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "market": "S&P 500"},
    ]
    stub_json(_activate_responses, "GET", path, payload)

    data = client.available.tickers("daily")
    assert isinstance(data, list)
    assert data[0]["ticker"] == "AAPL"


def test_tickers_dataframe_ok(client, _activate_responses):
    path = "available/tickers/monthly"
    payload = [
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "market": "NASDAQ"},
    ]
    stub_json(_activate_responses, "GET", path, payload)

    df = client.available.tickers("monthly", as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert df.loc[0, "ticker"] == "AMZN"


def test_tickers_invalid_type(client):
    with pytest.raises(ValueError):
        client.available.tickers("weekly")
