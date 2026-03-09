import pytest
import pandas as pd
from .conftest import stub_json, wrap_v2

TICKER = "AMZN"

def test_news_raw_ok(client, _activate_responses):
    """Default returns dict with articles."""
    path = f"news/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "articles": [
            {"date": "2024-01-15", "headline": "Amazon beats Q4 estimates", "source": "Reuters", "url": "https://example.com/1", "sentiment": 0.85},
            {"date": "2024-01-14", "headline": "Amazon layoffs continue", "source": "Bloomberg", "url": "https://example.com/2", "sentiment": -0.3},
        ]
    })
    stub_json(_activate_responses, "GET", path, payload)
    data = client.news.ticker(TICKER)
    assert data["symbol"] == "AMZN"
    assert len(data["articles"]) == 2
    assert data["articles"][0]["headline"] == "Amazon beats Q4 estimates"

def test_news_dataframe_ok(client, _activate_responses):
    """as_dataframe=True returns DataFrame indexed by date."""
    path = f"news/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "articles": [
            {"date": "2024-01-15", "headline": "Test", "source": "Reuters", "url": "https://example.com/1", "sentiment": 0.5},
        ]
    })
    stub_json(_activate_responses, "GET", path, payload)
    df = client.news.ticker(TICKER, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert set(df.columns) == {"headline", "source", "url", "sentiment"}
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert df.loc["2024-01-15", "headline"] == "Test"
    assert df.loc["2024-01-15", "sentiment"] == 0.5
    assert df.loc["2024-01-15", "source"] == "Reuters"

def test_news_with_dates(client, _activate_responses):
    """Date params are sent as startDate/endDate."""
    path = f"news/{TICKER}"
    payload = wrap_v2({"symbol": "AMZN", "name": "Amazon.com Inc.", "articles": []})
    stub_json(_activate_responses, "GET", path, payload, params={"startDate": "2024-01-01", "endDate": "2024-01-31"})
    data = client.news.ticker(TICKER, date_from="2024-01-01", date_to="2024-01-31")
    assert data["symbol"] == "AMZN"

def test_news_with_limit(client, _activate_responses):
    """Limit parameter is passed through."""
    path = f"news/{TICKER}"
    payload = wrap_v2({"symbol": "AMZN", "name": "Amazon.com Inc.", "articles": []})
    stub_json(_activate_responses, "GET", path, payload, params={"limit": "10"})
    data = client.news.ticker(TICKER, limit=10)
    assert data["symbol"] == "AMZN"

def test_news_bad_request(client, _activate_responses):
    path = f"news/{TICKER}"
    stub_json(_activate_responses, "GET", path, {"success": False, "error": {"code": "NOT_FOUND", "message": "Ticker not found"}}, status=404)
    with pytest.raises(Exception):
        client.news.ticker(TICKER)
