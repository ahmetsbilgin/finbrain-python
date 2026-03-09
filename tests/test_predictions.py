# tests/test_predictions.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── single-ticker predictions ──────────────────────────────────
def test_ticker_predictions_raw_ok(client, _activate_responses):
    path = f"predictions/daily/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "predictions": [
            {"date": "2024-03-19", "mid": 155.0, "lower": 150.0, "upper": 160.0},
            {"date": "2024-03-20", "mid": 156.0, "lower": 151.0, "upper": 161.0},
        ],
        "metadata": {
            "expectedShortTerm": 0.15,
            "expectedMidTerm": 0.45,
            "expectedLongTerm": 0.80,
        },
        "lastUpdated": "2024-03-18T23:00:00Z",
    })
    stub_json(_activate_responses, "GET", path, payload)

    data = client.predictions.ticker(TICKER)
    assert data["symbol"] == TICKER
    assert "predictions" in data
    assert data["predictions"][0]["date"] == "2024-03-19"


def test_ticker_predictions_dataframe_ok(client, _activate_responses):
    path = f"predictions/daily/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "predictions": [
            {"date": "2024-03-19", "mid": 155.0, "lower": 150.0, "upper": 160.0},
            {"date": "2024-03-20", "mid": 156.0, "lower": 151.0, "upper": 161.0},
        ],
        "metadata": {
            "expectedShortTerm": 0.15,
            "expectedMidTerm": 0.45,
            "expectedLongTerm": 0.80,
        },
        "lastUpdated": "2024-03-18T23:00:00Z",
    })
    stub_json(_activate_responses, "GET", path, payload)

    df = client.predictions.ticker(TICKER, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"mid", "lower", "upper"}
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-03-19") in df.index
    assert pd.Timestamp("2024-03-20") in df.index
    assert df.loc["2024-03-19", "mid"] == 155.0
    assert df.loc["2024-03-19", "lower"] == 150.0
    assert df.loc["2024-03-20", "upper"] == 161.0


# ─────────── error mapping ──────────────────────────────────────────────
def test_predictions_bad_request(client, _activate_responses):
    path = f"predictions/daily/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.predictions.ticker(TICKER)
