# tests/test_analyst_ratings.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_analyst_ratings_raw_ok(client, _activate_responses):
    path = f"analyst-ratings/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "ratings": [
            {
                "date": "2024-01-15",
                "institution": "Goldman Sachs",
                "action": "upgrade",
                "rating": "Buy",
                "targetPrice": 200.0,
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.analyst_ratings.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["ratings"], list)
    assert data["ratings"][0]["institution"] == "Goldman Sachs"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_analyst_ratings_dataframe_ok(client, _activate_responses):
    path = f"analyst-ratings/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "ratings": [
            {
                "date": "2024-01-15",
                "institution": "Goldman Sachs",
                "action": "upgrade",
                "rating": "Buy",
                "targetPrice": 200.0,
            },
            {
                "date": "2024-01-10",
                "institution": "Barclays",
                "action": "reiterate",
                "rating": "Neutral",
                "targetPrice": 180.0,
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.analyst_ratings.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"institution", "action", "rating", "targetPrice"}
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert pd.Timestamp("2024-01-10") in df.index
    assert df.loc["2024-01-10", "institution"] == "Barclays"
    assert df.loc["2024-01-15", "rating"] == "Buy"
    assert df.loc["2024-01-15", "targetPrice"] == 200.0


# ─────────── error mapping ──────────────────────────────────────────────
def test_analyst_ratings_bad_request(client, _activate_responses):
    path = f"analyst-ratings/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.analyst_ratings.ticker(symbol=TICKER)
