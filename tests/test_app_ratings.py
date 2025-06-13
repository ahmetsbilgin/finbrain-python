# tests/test_app_ratings.py
import pytest
import pandas as pd
from urllib.parse import quote
from .conftest import stub_json
from finbrain.exceptions import BadRequest

MARKET = "S&P 500"  # human-readable name with space
ENC_MARKET = quote(MARKET, safe="")  # → 'S%26P%20500'
TICKER = "AMZN"


def test_app_ratings_raw(client, _activate_responses):
    """Endpoint returns the original JSON shape."""
    path = f"appratings/{ENC_MARKET}/{TICKER}"
    payload = {"ticker": "AMZN", "appRatings": []}

    stub_json(_activate_responses, "GET", path, payload)

    data = client.app_ratings.ticker(MARKET, TICKER)
    assert data["ticker"] == "AMZN"
    assert isinstance(data["appRatings"], list)


def test_app_ratings_dataframe(client, _activate_responses):
    """Endpoint returns a DataFrame with `date` as the index."""
    path = f"appratings/{ENC_MARKET}/{TICKER}"
    ratings = [
        {
            "date": "2024-02-02",
            "playStoreScore": 3.75,
            "playStoreRatingsCount": 567996,
            "appStoreScore": 4.07,
            "appStoreRatingsCount": 88533,
            "playStoreInstallCount": None,
        }
    ]
    payload = {"ticker": "AMZN", "name": "Amazon.com Inc.", "appRatings": ratings}

    stub_json(_activate_responses, "GET", path, payload)

    df = client.app_ratings.ticker(MARKET, TICKER, as_dataframe=True)
    # basic shape checks
    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert "playStoreScore" in df.columns
    assert df["playStoreScore"].dtype.kind in "fi"  # float or int
    # the single mocked row should appear at the expected date
    assert pd.Timestamp("2024-02-02") in df.index


def test_app_ratings_bad_request(client, _activate_responses):
    path = f"appratings/{ENC_MARKET}/{TICKER}"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)
    with pytest.raises(BadRequest):
        client.app_ratings.ticker(MARKET, TICKER)
