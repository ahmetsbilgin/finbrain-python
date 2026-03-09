import pandas as pd
from .conftest import stub_json, wrap_v2


def test_recent_news_ok(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "headline": "Apple news", "date": "2024-01-15"},
        {"symbol": "AMZN", "headline": "Amazon news", "date": "2024-01-14"},
    ])
    stub_json(_activate_responses, "GET", "recent/news", payload, params={"limit": "10"})
    data = client.recent.news(limit=10)
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["symbol"] == "AAPL"
    assert data[1]["headline"] == "Amazon news"


def test_recent_news_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "headline": "Apple rises", "date": "2024-01-15"},
        {"symbol": "AMZN", "headline": "Amazon grows", "date": "2024-01-14"},
    ])
    stub_json(_activate_responses, "GET", "recent/news", payload, params={"limit": "5"})
    df = client.recent.news(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"symbol", "headline", "date"}
    assert df.iloc[0]["symbol"] == "AAPL"
    assert df.iloc[1]["headline"] == "Amazon grows"


def test_recent_news_with_market(client, _activate_responses):
    payload = wrap_v2([])
    stub_json(_activate_responses, "GET", "recent/news", payload, params={"limit": "5", "market": "S&P 500"})
    data = client.recent.news(limit=5, market="S&P 500")
    assert isinstance(data, list)
    assert len(data) == 0


def test_recent_analyst_ratings_ok(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "institution": "Goldman", "rating": "Buy", "date": "2024-01-15"},
        {"symbol": "MSFT", "institution": "Barclays", "rating": "Hold", "date": "2024-01-14"},
    ])
    stub_json(_activate_responses, "GET", "recent/analyst-ratings", payload, params={"limit": "10"})
    data = client.recent.analyst_ratings(limit=10)
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["symbol"] == "AAPL"
    assert data[0]["institution"] == "Goldman"
    assert data[1]["rating"] == "Hold"


def test_recent_analyst_ratings_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "institution": "Goldman", "rating": "Buy", "date": "2024-01-15"},
        {"symbol": "MSFT", "institution": "Barclays", "rating": "Hold", "date": "2024-01-14"},
    ])
    stub_json(_activate_responses, "GET", "recent/analyst-ratings", payload, params={"limit": "5"})
    df = client.recent.analyst_ratings(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"symbol", "institution", "rating", "date"}
    assert df.iloc[0]["symbol"] == "AAPL"
    assert df.iloc[0]["rating"] == "Buy"
    assert df.iloc[1]["institution"] == "Barclays"
