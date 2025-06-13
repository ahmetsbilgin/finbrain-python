# tests/test_app_ratings.py
import pandas as pd

from .conftest import stub_json


def test_app_ratings_raw(client, _activate_responses):
    """Endpoint returns the original JSON shape."""
    path = "appratings/sp500/AMZN"
    payload = {"ticker": "AMZN", "appRatings": []}

    stub_json(_activate_responses, "GET", path, payload)

    data = client.app_ratings.ticker("sp500", "AMZN")
    assert data["ticker"] == "AMZN"
    assert isinstance(data["appRatings"], list)


def test_app_ratings_dataframe(client, _activate_responses):
    """Endpoint returns a DataFrame with `date` as the index."""
    path = "appratings/sp500/AMZN"
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

    df = client.app_ratings.ticker("sp500", "AMZN", as_dataframe=True)

    # basic shape checks
    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert "playStoreScore" in df.columns
    # the single mocked row should appear at the expected date
    assert pd.Timestamp("2024-02-02") in df.index
