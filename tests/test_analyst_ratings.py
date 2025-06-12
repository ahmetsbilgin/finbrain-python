# tests/test_analyst_ratings.py
from .conftest import stub_json


def test_analyst_ratings_ok(client, _activate_responses):
    path = "analystratings/sp500/AMZN"
    stub_json(
        _activate_responses, "GET", path, {"ticker": "AMZN", "analystRatings": []}
    )
    data = client.analyst_ratings.ticker("sp500", "AMZN")
    assert data["analystRatings"] == []
