# tests/test_app_ratings.py
from .conftest import stub_json


def test_app_ratings_ok(client, _activate_responses):
    path = "appratings/sp500/AMZN"
    stub_json(_activate_responses, "GET", path, {"ticker": "AMZN", "appRatings": []})
    assert "appRatings" in client.app_ratings.ticker("sp500", "AMZN")
