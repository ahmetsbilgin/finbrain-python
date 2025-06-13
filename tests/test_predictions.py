# tests/test_predictions.py
import pandas as pd
import pytest
from urllib.parse import quote

from .conftest import stub_json
from finbrain.exceptions import BadRequest

MARKET = "S&P 500"
ENC_MARKET = quote(MARKET, safe="")  # → 'S%26P%20500'
TICKER = "AMZN"


# ─────────── market-level predictions ───────────────────────────────────
def test_market_predictions_raw_ok(client, _activate_responses):
    path = f"market/{ENC_MARKET}/predictions/daily"
    payload = [
        {
            "ticker": "AMZN",
            "name": "Amazon.com Inc.",
            "prediction": {
                "expectedShort": "0.42",
                "expectedMid": "1.10",
                "expectedLong": "2.35",
                "type": "daily",
            },
            "sentimentScore": "0.22",
        },
        {
            "ticker": "MSFT",
            "name": "Microsoft Corp.",
            "prediction": {
                "expectedShort": "-0.12",
                "expectedMid": "0.20",
                "expectedLong": "1.05",
                "type": "daily",
            },
            "sentimentScore": "-0.05",
        },
    ]
    stub_json(_activate_responses, "GET", path, payload)

    data = client.predictions.market(MARKET, prediction_type="daily")
    assert isinstance(data, list)
    assert data[0]["ticker"] == "AMZN"


def test_market_predictions_dataframe_ok(client, _activate_responses):
    path = f"market/{ENC_MARKET}/predictions/daily"
    payload = [
        {
            "ticker": "AMZN",
            "name": "Amazon.com Inc.",
            "prediction": {
                "expectedShort": "0.42",
                "expectedMid": "1.10",
                "expectedLong": "2.35",
                "type": "daily",
            },
            "sentimentScore": "0.22",
        }
    ]
    stub_json(_activate_responses, "GET", path, payload)

    df = client.predictions.market(MARKET, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "ticker"
    assert "expectedShort" in df.columns
    assert df.loc["AMZN", "expectedLong"] == 2.35


# ─────────── single-ticker predictions ──────────────────────────────────
def test_ticker_predictions_raw_ok(client, _activate_responses):
    path = f"ticker/{TICKER}/predictions/daily"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "prediction": {
            "2024-03-19": "155.0,150.0,160.0",
            "2024-03-20": "156.0,151.0,161.0",
            "expectedShort": "0.15",
            "expectedMid": "0.45",
            "expectedLong": "0.80",
            "type": "daily",
            "lastUpdate": "2024-03-18T23:00:00Z",
        },
        "sentimentAnalysis": {"2024-03-19": "0.22"},
    }
    stub_json(_activate_responses, "GET", path, payload)

    data = client.predictions.ticker(TICKER)
    assert data["ticker"] == TICKER
    assert "prediction" in data
    assert "2024-03-19" in data["prediction"]


def test_ticker_predictions_dataframe_ok(client, _activate_responses):
    path = f"ticker/{TICKER}/predictions/daily"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "prediction": {
            "2024-03-19": "155.0,150.0,160.0",
            "2024-03-20": "156.0,151.0,161.0",
            "expectedShort": "0.15",
            "expectedMid": "0.45",
            "expectedLong": "0.80",
            "type": "daily",
        },
    }
    stub_json(_activate_responses, "GET", path, payload)

    df = client.predictions.ticker(TICKER, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert pd.Timestamp("2024-03-19") in df.index
    assert {"main", "lower", "upper"}.issubset(df.columns)


# ─────────── error mapping ──────────────────────────────────────────────
def test_predictions_bad_request(client, _activate_responses):
    path = f"ticker/{TICKER}/predictions/daily"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)

    with pytest.raises(BadRequest):
        client.predictions.ticker(TICKER)
