# tests/test_sentiments.py
import pytest
import pandas as pd
from urllib.parse import quote
from finbrain.exceptions import BadRequest
from .conftest import stub_json

MARKET = "S&P 500"
ENC_MARKET = quote(MARKET, safe="")
TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_sentiments_raw_ok(client, _activate_responses):
    """Default behaviour returns the original dict."""
    path = f"sentiments/{ENC_MARKET}/AMZN"
    payload = {
        "ticker": "AMZN",
        "name": "Amazon.com Inc.",
        "sentimentAnalysis": {"2024-01-02": "0.123", "2024-01-01": "-0.045"},
    }

    stub_json(
        _activate_responses,
        "GET",
        path,
        payload,
        params={"dateFrom": "2024-01-01", "dateTo": "2024-01-02"},
    )

    data = client.sentiments.ticker(
        market=MARKET,
        symbol=TICKER,
        date_from="2024-01-01",
        date_to="2024-01-02",
    )

    assert data["ticker"] == "AMZN"
    assert "sentimentAnalysis" in data
    assert len(data["sentimentAnalysis"]) == 2


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_sentiments_dataframe_ok(client, _activate_responses):
    """as_dataframe=True returns a DataFrame indexed by date."""

    path = f"sentiments/{ENC_MARKET}/AMZN"

    payload = {
        "ticker": "AMZN",
        "name": "Amazon.com Inc.",
        "sentimentAnalysis": {
            "2024-01-02": "0.123",
            "2024-01-01": "-0.045",
        },
    }

    stub_json(
        _activate_responses,
        "GET",
        path,
        payload,
        params={"days": "2"},
    )

    df = client.sentiments.ticker(
        market=MARKET,
        symbol=TICKER,
        days=2,
        as_dataframe=True,
    )

    # basic shape checks
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["sentiment"]
    assert pd.Timestamp("2024-01-02") in df.index
    # ensure index is datetime
    assert pd.api.types.is_datetime64_any_dtype(df.index)


def test_sentiments_bad_request(client, _activate_responses):
    path = f"sentiments/{ENC_MARKET}/{TICKER}"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)

    with pytest.raises(BadRequest):
        client.sentiments.ticker(MARKET, TICKER)
