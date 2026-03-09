# tests/test_app_ratings.py
import pytest
import pandas as pd
from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_app_ratings_raw(client, _activate_responses):
    """Endpoint returns the original JSON shape."""
    path = f"app-ratings/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "data": [
            {
                "date": "2024-01-15",
                "ios": {"score": 4.07, "ratingsCount": 88533},
                "android": {
                    "score": 3.75,
                    "ratingsCount": 567996,
                    "installCount": None,
                },
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.app_ratings.ticker(symbol=TICKER)
    assert data["symbol"] == "AMZN"
    assert isinstance(data["data"], list)


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_app_ratings_dataframe(client, _activate_responses):
    """Endpoint returns a DataFrame with `date` as the index."""
    path = f"app-ratings/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "data": [
            {
                "date": "2024-01-15",
                "ios": {"score": 4.07, "ratingsCount": 88533},
                "android": {
                    "score": 3.75,
                    "ratingsCount": 567996,
                    "installCount": None,
                },
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.app_ratings.ticker(symbol=TICKER, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert set(df.columns) == {"ios_score", "ios_ratingsCount", "android_score", "android_ratingsCount", "android_installCount"}
    assert df.loc["2024-01-15", "ios_score"] == 4.07
    assert df.loc["2024-01-15", "android_ratingsCount"] == 567996


# ─────────── error mapping ──────────────────────────────────────────────
def test_app_ratings_bad_request(client, _activate_responses):
    path = f"app-ratings/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )
    with pytest.raises(BadRequest):
        client.app_ratings.ticker(symbol=TICKER)
