"""
Integration tests that hit the real FinBrain v2 API.

Run with:
    pytest -m integration

Requires FINBRAIN_API_KEY to be set in the environment (or .env file).
All tests are skipped automatically when the key is absent.
"""

import os

import pandas as pd
import pytest

from finbrain import FinBrainClient
from finbrain.exceptions import FinBrainError

# ── skip all tests if no API key ──────────────────────────────────────
API_KEY = os.environ.get("FINBRAIN_API_KEY")
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not API_KEY, reason="FINBRAIN_API_KEY not set"),
]

TICKER = "AAPL"
MARKET = "S&P 500"


@pytest.fixture(scope="module")
def fb():
    """Shared client for the entire module (one session)."""
    client = FinBrainClient(api_key=API_KEY)
    yield client
    client.session.close()


# =====================================================================
# Discovery
# =====================================================================
class TestAvailable:
    def test_markets(self, fb):
        data = fb.available.markets()
        assert isinstance(data, list)
        assert len(data) > 0
        # each item should have name & region
        assert "name" in data[0]
        assert "region" in data[0]

    def test_tickers_daily(self, fb):
        df = fb.available.tickers("daily", as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "symbol" in df.columns

    def test_tickers_monthly(self, fb):
        data = fb.available.tickers("monthly")
        assert isinstance(data, list)
        assert len(data) > 0

    def test_regions(self, fb):
        data = fb.available.regions()
        assert isinstance(data, (list, dict))


# =====================================================================
# Predictions
# =====================================================================
class TestPredictions:
    def test_raw(self, fb):
        data = fb.predictions.ticker(TICKER)
        assert isinstance(data, dict)
        assert "predictions" in data
        assert isinstance(data["predictions"], list)
        assert len(data["predictions"]) > 0
        row = data["predictions"][0]
        assert "date" in row
        assert "mid" in row
        assert "lower" in row
        assert "upper" in row

    def test_dataframe(self, fb):
        df = fb.predictions.ticker(TICKER, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert df.index.name == "date"
        assert pd.api.types.is_datetime64_any_dtype(df.index)
        assert {"mid", "lower", "upper"}.issubset(df.columns)
        # values should be numeric
        assert pd.api.types.is_numeric_dtype(df["mid"])

    def test_monthly(self, fb):
        df = fb.predictions.ticker(TICKER, prediction_type="monthly", as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert {"mid", "lower", "upper"}.issubset(df.columns)


# =====================================================================
# Sentiments
# =====================================================================
class TestSentiments:
    def test_raw(self, fb):
        data = fb.sentiments.ticker(TICKER)
        assert isinstance(data, dict)
        assert "data" in data
        rows = data["data"]
        assert isinstance(rows, list)
        if len(rows) > 0:
            assert "date" in rows[0]
            assert "score" in rows[0]

    def test_dataframe(self, fb):
        df = fb.sentiments.ticker(TICKER, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert pd.api.types.is_datetime64_any_dtype(df.index)
            assert "sentiment" in df.columns
            assert pd.api.types.is_numeric_dtype(df["sentiment"])


# =====================================================================
# News
# =====================================================================
class TestNews:
    def test_raw(self, fb):
        data = fb.news.ticker(TICKER, limit=5)
        assert isinstance(data, dict)
        assert "articles" in data
        articles = data["articles"]
        assert isinstance(articles, list)
        if len(articles) > 0:
            assert "headline" in articles[0]
            assert "date" in articles[0]

    def test_dataframe(self, fb):
        df = fb.news.ticker(TICKER, limit=5, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert "headline" in df.columns


# =====================================================================
# Analyst Ratings
# =====================================================================
class TestAnalystRatings:
    def test_raw(self, fb):
        data = fb.analyst_ratings.ticker(TICKER)
        assert isinstance(data, dict)
        assert "ratings" in data
        ratings = data["ratings"]
        assert isinstance(ratings, list)
        if len(ratings) > 0:
            assert "date" in ratings[0]
            assert "institution" in ratings[0]

    def test_dataframe(self, fb):
        df = fb.analyst_ratings.ticker(TICKER, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert pd.api.types.is_datetime64_any_dtype(df.index)
            assert "institution" in df.columns


# =====================================================================
# Options / Put-Call Ratio
# =====================================================================
class TestOptions:
    def test_raw(self, fb):
        data = fb.options.put_call(TICKER)
        assert isinstance(data, dict)
        assert "data" in data
        rows = data["data"]
        assert isinstance(rows, list)
        if len(rows) > 0:
            row = rows[0]
            assert "date" in row
            assert "ratio" in row
            assert "callVolume" in row
            assert "putVolume" in row

    def test_dataframe(self, fb):
        df = fb.options.put_call(TICKER, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert pd.api.types.is_datetime64_any_dtype(df.index)
            assert {"ratio", "callVolume", "putVolume"}.issubset(df.columns)


# =====================================================================
# Insider Transactions
# =====================================================================
class TestInsiderTransactions:
    def test_raw(self, fb):
        data = fb.insider_transactions.ticker(TICKER)
        assert isinstance(data, dict)
        assert "transactions" in data
        txns = data["transactions"]
        assert isinstance(txns, list)
        if len(txns) > 0:
            assert "date" in txns[0]
            assert "insider" in txns[0]
            assert "transactionType" in txns[0]

    def test_dataframe(self, fb):
        df = fb.insider_transactions.ticker(TICKER, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert pd.api.types.is_datetime64_any_dtype(df.index)
            assert "insider" in df.columns
            assert "transactionType" in df.columns


# =====================================================================
# House Trades
# =====================================================================
class TestHouseTrades:
    def test_raw(self, fb):
        data = fb.house_trades.ticker(TICKER)
        assert isinstance(data, dict)
        assert "trades" in data
        trades = data["trades"]
        assert isinstance(trades, list)
        if len(trades) > 0:
            assert "date" in trades[0]
            assert "politician" in trades[0]
            assert "transactionType" in trades[0]

    def test_dataframe(self, fb):
        df = fb.house_trades.ticker(TICKER, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert "politician" in df.columns


# =====================================================================
# Senate Trades
# =====================================================================
class TestSenateTrades:
    def test_raw(self, fb):
        data = fb.senate_trades.ticker(TICKER)
        assert isinstance(data, dict)
        assert "trades" in data
        trades = data["trades"]
        assert isinstance(trades, list)
        if len(trades) > 0:
            assert "date" in trades[0]
            assert "politician" in trades[0]

    def test_dataframe(self, fb):
        df = fb.senate_trades.ticker(TICKER, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert "politician" in df.columns


# =====================================================================
# LinkedIn Data
# =====================================================================
class TestLinkedInData:
    def test_raw(self, fb):
        data = fb.linkedin_data.ticker(TICKER)
        assert isinstance(data, dict)
        assert "data" in data
        rows = data["data"]
        assert isinstance(rows, list)
        if len(rows) > 0:
            assert "date" in rows[0]
            assert "employeeCount" in rows[0]
            assert "followerCount" in rows[0]

    def test_dataframe(self, fb):
        df = fb.linkedin_data.ticker(TICKER, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert pd.api.types.is_datetime64_any_dtype(df.index)
            assert {"employeeCount", "followerCount", "jobCount"}.issubset(df.columns)


# =====================================================================
# App Ratings
# =====================================================================
class TestAppRatings:
    def test_raw(self, fb):
        data = fb.app_ratings.ticker("AMZN")
        assert isinstance(data, dict)
        assert "data" in data
        rows = data["data"]
        assert isinstance(rows, list)
        if len(rows) > 0:
            assert "date" in rows[0]
            assert "ios" in rows[0] or "android" in rows[0]

    def test_dataframe(self, fb):
        df = fb.app_ratings.ticker("AMZN", as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        if len(df) > 0:
            assert df.index.name == "date"
            assert pd.api.types.is_datetime64_any_dtype(df.index)
            # flattened columns
            assert any(c.startswith("ios_") or c.startswith("android_") for c in df.columns)


# =====================================================================
# Screener
# =====================================================================
class TestScreener:
    def test_sentiment(self, fb):
        data = fb.screener.sentiment(market=MARKET)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "symbol" in data[0]

    def test_sentiment_dataframe(self, fb):
        df = fb.screener.sentiment(market=MARKET, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert df.index.name == "symbol"

    def test_predictions_daily(self, fb):
        df = fb.screener.predictions_daily(limit=5, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert df.index.name == "symbol"

    def test_predictions_monthly(self, fb):
        data = fb.screener.predictions_monthly(limit=5)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_insider_trading(self, fb):
        data = fb.screener.insider_trading(limit=5)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "symbol" in data[0]

    def test_analyst_ratings(self, fb):
        data = fb.screener.analyst_ratings(limit=5)
        assert isinstance(data, list)

    def test_congress_house(self, fb):
        data = fb.screener.congress_house(limit=5)
        assert isinstance(data, list)

    def test_congress_senate(self, fb):
        data = fb.screener.congress_senate(limit=5)
        assert isinstance(data, list)

    def test_news(self, fb):
        data = fb.screener.news(limit=5)
        assert isinstance(data, list)

    def test_put_call_ratio(self, fb):
        data = fb.screener.put_call_ratio(limit=5)
        assert isinstance(data, list)

    def test_linkedin(self, fb):
        data = fb.screener.linkedin(market=MARKET)
        assert isinstance(data, list)

    def test_app_ratings(self, fb):
        data = fb.screener.app_ratings(market=MARKET)
        assert isinstance(data, list)


# =====================================================================
# Recent
# =====================================================================
class TestRecent:
    def test_news(self, fb):
        data = fb.recent.news(limit=5)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "symbol" in data[0]

    def test_news_dataframe(self, fb):
        df = fb.recent.news(limit=5, as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "symbol" in df.columns

    def test_analyst_ratings(self, fb):
        data = fb.recent.analyst_ratings(limit=5)
        assert isinstance(data, list)
        assert len(data) > 0


# =====================================================================
# Envelope / Meta
# =====================================================================
class TestEnvelope:
    def test_last_meta_populated(self, fb):
        """After any successful call, client.last_meta should be set."""
        fb.available.markets()
        assert fb.last_meta is not None
        assert "timestamp" in fb.last_meta

    def test_invalid_ticker_raises(self, fb):
        """Requesting a nonsense ticker should raise a FinBrainError."""
        with pytest.raises(FinBrainError):
            fb.predictions.ticker("ZZZZZZNOTREAL999")
