import pytest
import pandas as pd
from .conftest import stub_json, wrap_v2


# ── sentiment ──────────────────────────────────────────────────────────
def test_screener_sentiment_ok(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple Inc.", "score": 0.75},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "score": -0.2},
    ])
    stub_json(_activate_responses, "GET", "screener/sentiment", payload, params={"market": "S&P 500"})
    data = client.screener.sentiment(market="S&P 500")
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["symbol"] == "AAPL"
    assert data[0]["score"] == 0.75


def test_screener_sentiment_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple Inc.", "score": 0.75},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "score": -0.2},
    ])
    stub_json(_activate_responses, "GET", "screener/sentiment", payload, params={"market": "S&P 500"})
    df = client.screener.sentiment(market="S&P 500", as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "score"}
    assert df.loc["AAPL", "score"] == 0.75
    assert df.loc["AMZN", "score"] == -0.2


def test_screener_sentiment_requires_market_or_region(client):
    with pytest.raises(ValueError, match="market.*region"):
        client.screener.sentiment(limit=10)


# ── analyst ratings ────────────────────────────────────────────────────
def test_screener_analyst_ratings(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "rating": "Buy"},
        {"symbol": "MSFT", "name": "Microsoft", "rating": "Hold"},
    ])
    stub_json(_activate_responses, "GET", "screener/analyst-ratings", payload, params={"limit": "5"})
    data = client.screener.analyst_ratings(limit=5)
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["rating"] == "Buy"


def test_screener_analyst_ratings_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "rating": "Buy"},
        {"symbol": "MSFT", "name": "Microsoft", "rating": "Hold"},
    ])
    stub_json(_activate_responses, "GET", "screener/analyst-ratings", payload, params={"limit": "5"})
    df = client.screener.analyst_ratings(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "rating"}
    assert df.loc["AAPL", "rating"] == "Buy"
    assert df.loc["MSFT", "rating"] == "Hold"


# ── insider trading ────────────────────────────────────────────────────
def test_screener_insider_trading(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "transactionType": "Sale", "shares": 5000},
    ])
    stub_json(_activate_responses, "GET", "screener/insider-trading", payload, params={"limit": "5"})
    data = client.screener.insider_trading(limit=5)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["transactionType"] == "Sale"


def test_screener_insider_trading_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "transactionType": "Sale", "shares": 5000},
        {"symbol": "TSLA", "name": "Tesla", "transactionType": "Purchase", "shares": 1000},
    ])
    stub_json(_activate_responses, "GET", "screener/insider-trading", payload, params={"limit": "5"})
    df = client.screener.insider_trading(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "transactionType", "shares"}
    assert df.loc["AAPL", "transactionType"] == "Sale"
    assert df.loc["TSLA", "shares"] == 1000


# ── congress house ─────────────────────────────────────────────────────
def test_screener_congress_house(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "politician": "Nancy Pelosi"},
    ])
    stub_json(_activate_responses, "GET", "screener/congress/house", payload, params={"limit": "5"})
    data = client.screener.congress_house(limit=5)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["politician"] == "Nancy Pelosi"


def test_screener_congress_house_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "politician": "Nancy Pelosi"},
        {"symbol": "MSFT", "name": "Microsoft", "politician": "Dan Crenshaw"},
    ])
    stub_json(_activate_responses, "GET", "screener/congress/house", payload, params={"limit": "5"})
    df = client.screener.congress_house(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "politician"}
    assert df.loc["AAPL", "politician"] == "Nancy Pelosi"


# ── congress senate ────────────────────────────────────────────────────
def test_screener_congress_senate(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "politician": "John Boozman"},
    ])
    stub_json(_activate_responses, "GET", "screener/congress/senate", payload, params={"limit": "5"})
    data = client.screener.congress_senate(limit=5)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["politician"] == "John Boozman"


def test_screener_congress_senate_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "politician": "John Boozman"},
        {"symbol": "NVDA", "name": "NVIDIA", "politician": "Tommy Tuberville"},
    ])
    stub_json(_activate_responses, "GET", "screener/congress/senate", payload, params={"limit": "5"})
    df = client.screener.congress_senate(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "politician"}
    assert df.loc["NVDA", "politician"] == "Tommy Tuberville"


# ── news ───────────────────────────────────────────────────────────────
def test_screener_news(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "headline": "Apple announces new product"},
    ])
    stub_json(_activate_responses, "GET", "screener/news", payload, params={"limit": "5"})
    data = client.screener.news(limit=5)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["headline"] == "Apple announces new product"


def test_screener_news_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "headline": "Apple news"},
        {"symbol": "AMZN", "name": "Amazon", "headline": "Amazon news"},
    ])
    stub_json(_activate_responses, "GET", "screener/news", payload, params={"limit": "5"})
    df = client.screener.news(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "headline"}
    assert df.loc["AAPL", "headline"] == "Apple news"


# ── put-call ratio ─────────────────────────────────────────────────────
def test_screener_put_call_ratio(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "ratio": 0.85},
    ])
    stub_json(_activate_responses, "GET", "screener/put-call-ratio", payload, params={"limit": "5"})
    data = client.screener.put_call_ratio(limit=5)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["ratio"] == 0.85


def test_screener_put_call_ratio_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "ratio": 0.85},
        {"symbol": "AMZN", "name": "Amazon", "ratio": 1.2},
    ])
    stub_json(_activate_responses, "GET", "screener/put-call-ratio", payload, params={"limit": "5"})
    df = client.screener.put_call_ratio(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "ratio"}
    assert df.loc["AAPL", "ratio"] == 0.85
    assert df.loc["AMZN", "ratio"] == 1.2


# ── linkedin ───────────────────────────────────────────────────────────
def test_screener_linkedin_requires_market_or_region(client):
    with pytest.raises(ValueError, match="market.*region"):
        client.screener.linkedin(limit=10)


def test_screener_linkedin_ok(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "employeeCount": 150000},
    ])
    stub_json(_activate_responses, "GET", "screener/linkedin", payload, params={"market": "S&P 500"})
    data = client.screener.linkedin(market="S&P 500")
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["employeeCount"] == 150000


def test_screener_linkedin_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "employeeCount": 150000},
        {"symbol": "MSFT", "name": "Microsoft", "employeeCount": 220000},
    ])
    stub_json(_activate_responses, "GET", "screener/linkedin", payload, params={"market": "S&P 500"})
    df = client.screener.linkedin(market="S&P 500", as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "employeeCount"}
    assert df.loc["MSFT", "employeeCount"] == 220000


# ── app ratings ────────────────────────────────────────────────────────
def test_screener_app_ratings_requires_market_or_region(client):
    with pytest.raises(ValueError, match="market.*region"):
        client.screener.app_ratings(limit=10)


def test_screener_app_ratings_ok(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "ios_score": 4.5},
    ])
    stub_json(_activate_responses, "GET", "screener/app-ratings", payload, params={"region": "US"})
    data = client.screener.app_ratings(region="US")
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["ios_score"] == 4.5


def test_screener_app_ratings_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "ios_score": 4.5},
        {"symbol": "AMZN", "name": "Amazon", "ios_score": 3.8},
    ])
    stub_json(_activate_responses, "GET", "screener/app-ratings", payload, params={"region": "US"})
    df = client.screener.app_ratings(region="US", as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "ios_score"}
    assert df.loc["AAPL", "ios_score"] == 4.5
    assert df.loc["AMZN", "ios_score"] == 3.8


# ── predictions daily ─────────────────────────────────────────────────
def test_screener_predictions_daily(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "expectedShortTerm": 0.5},
    ])
    stub_json(_activate_responses, "GET", "screener/predictions/daily", payload, params={"limit": "5"})
    data = client.screener.predictions_daily(limit=5)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["expectedShortTerm"] == 0.5


def test_screener_predictions_daily_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "expectedShortTerm": 0.5},
        {"symbol": "MSFT", "name": "Microsoft", "expectedShortTerm": 0.3},
    ])
    stub_json(_activate_responses, "GET", "screener/predictions/daily", payload, params={"limit": "5"})
    df = client.screener.predictions_daily(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "expectedShortTerm"}
    assert df.loc["AAPL", "expectedShortTerm"] == 0.5
    assert df.loc["MSFT", "expectedShortTerm"] == 0.3


# ── predictions monthly ───────────────────────────────────────────────
def test_screener_predictions_monthly(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "expectedLongTerm": 1.5},
    ])
    stub_json(_activate_responses, "GET", "screener/predictions/monthly", payload, params={"limit": "5"})
    data = client.screener.predictions_monthly(limit=5)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["expectedLongTerm"] == 1.5


def test_screener_predictions_monthly_dataframe(client, _activate_responses):
    payload = wrap_v2([
        {"symbol": "AAPL", "name": "Apple", "expectedLongTerm": 1.5},
        {"symbol": "TSLA", "name": "Tesla", "expectedLongTerm": 2.1},
    ])
    stub_json(_activate_responses, "GET", "screener/predictions/monthly", payload, params={"limit": "5"})
    df = client.screener.predictions_monthly(limit=5, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert set(df.columns) == {"name", "expectedLongTerm"}
    assert df.loc["AAPL", "expectedLongTerm"] == 1.5
    assert df.loc["TSLA", "expectedLongTerm"] == 2.1
