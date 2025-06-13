# tests/test_analyst_ratings.py
import pandas as pd
import pytest
from urllib.parse import quote

from .conftest import stub_json
from finbrain.exceptions import BadRequest


# ─────────── helpers ────────────────────────────────────────────────────
MARKET = "S&P 500"  # contains space and &
ENC_MARKET = quote(MARKET, safe="")  # → 'S%26P%20500'
TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_analyst_ratings_raw_ok(client, _activate_responses):
    path = f"analystratings/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "analystRatings": [
            {
                "date": "2024-02-02",
                "type": "Reiterated",
                "institution": "Piper Sandler",
                "signal": "Neutral",
                "targetPrice": "$205 → $190",
            }
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    data = client.analyst_ratings.ticker(MARKET, TICKER)
    assert data["ticker"] == TICKER
    assert isinstance(data["analystRatings"], list)
    assert data["analystRatings"][0]["institution"] == "Piper Sandler"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_analyst_ratings_dataframe_ok(client, _activate_responses):
    path = f"analystratings/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "analystRatings": [
            {
                "date": "2024-02-02",
                "type": "Reiterated",
                "institution": "Piper Sandler",
                "signal": "Neutral",
                "targetPrice": "$205 → $190",
            },
            {
                "date": "2024-01-15",
                "type": "Upgrade",
                "institution": "Barclays",
                "signal": "Buy",
                "targetPrice": "$180 → $210",
            },
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    df = client.analyst_ratings.ticker(MARKET, TICKER, as_dataframe=True)

    # basic checks
    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert pd.Timestamp("2024-02-02") in df.index
    assert df.loc["2024-01-15", "institution"] == "Barclays"


# ─────────── error mapping ──────────────────────────────────────────────
def test_analyst_ratings_bad_request(client, _activate_responses):
    path = f"analystratings/{ENC_MARKET}/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"message": "bad params"},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.analyst_ratings.ticker(MARKET, TICKER)
