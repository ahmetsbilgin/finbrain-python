"""Tests for plotting module — validation + functional figure construction."""

import pytest
import pandas as pd
import plotly.graph_objects as go
from finbrain.plotting import _PlotNamespace


# ═══════════════════════════════════════════════════════════════════════════
# Helpers & mock data
# ═══════════════════════════════════════════════════════════════════════════

PRICE_DF = pd.DataFrame(
    {"close": [150.0, 151.5, 149.8, 152.0],
     "date": pd.date_range("2024-01-01", periods=4)},
).set_index("date")


def _empty_tx_df():
    """Empty transaction DataFrame with the expected structure."""
    df = pd.DataFrame({"transactionType": []})
    df.index = pd.DatetimeIndex([])
    df.index.name = "date"
    return df


def _tx_df_with_data():
    """Transaction DataFrame with buy/sell entries."""
    df = pd.DataFrame({
        "transactionType": ["Purchase", "Sale"],
        "date": pd.to_datetime(["2024-01-01", "2024-01-03"]),
    }).set_index("date")
    return df


class MockClient:
    """Bare mock — no endpoints wired."""
    pass


class MockAppRatingsClient:
    class app_ratings:
        @staticmethod
        def ticker(*args, **kwargs):
            df = pd.DataFrame({
                "android_ratingsCount": [1000, 1200, 1100],
                "android_score": [4.2, 4.3, 4.1],
                "ios_ratingsCount": [800, 900, 850],
                "ios_score": [4.5, 4.6, 4.4],
                "date": pd.date_range("2024-01-01", periods=3),
            }).set_index("date")
            return df


class MockLinkedInClient:
    class linkedin_data:
        @staticmethod
        def ticker(*args, **kwargs):
            df = pd.DataFrame({
                "employeeCount": [5000, 5100, 5200],
                "followerCount": [100000, 102000, 104000],
                "date": pd.date_range("2024-01-01", periods=3),
            }).set_index("date")
            return df


class MockSentimentsClient:
    class sentiments:
        @staticmethod
        def ticker(*args, **kwargs):
            df = pd.DataFrame({
                "sentiment": [0.15, -0.08, 0.22],
                "date": pd.date_range("2024-01-01", periods=3),
            }).set_index("date")
            return df


class MockOptionsClient:
    class options:
        @staticmethod
        def put_call(*args, **kwargs):
            df = pd.DataFrame({
                "callVolume": [10000, 12000, 11000],
                "putVolume": [8000, 9000, 7500],
                "ratio": [0.8, 0.75, 0.68],
                "date": pd.date_range("2024-01-01", periods=3),
            }).set_index("date")
            return df


class MockPredictionsClient:
    class predictions:
        @staticmethod
        def ticker(*args, **kwargs):
            df = pd.DataFrame({
                "mid": [150.0, 152.0, 154.0],
                "upper": [155.0, 157.0, 159.0],
                "lower": [145.0, 147.0, 149.0],
                "date": pd.date_range("2024-01-01", periods=3),
            }).set_index("date")
            return df


class MockInsiderClient:
    class insider_transactions:
        @staticmethod
        def ticker(*args, **kwargs):
            return _tx_df_with_data()


class MockHouseClient:
    class house_trades:
        @staticmethod
        def ticker(*args, **kwargs):
            return _tx_df_with_data()


class MockSenateClient:
    class senate_trades:
        @staticmethod
        def ticker(*args, **kwargs):
            return _tx_df_with_data()


class MockCorporateLobbyingClient:
    class corporate_lobbying:
        @staticmethod
        def ticker(*args, **kwargs):
            df = pd.DataFrame({
                "income": [50000, 30000],
                "expenses": [75000, 45000],
                "registrantName": ["Firm A", "Firm B"],
                "quarter": ["Q1", "Q2"],
                "date": pd.to_datetime(["2024-03-15", "2024-06-20"]),
            }).set_index("date")
            return df


class MockRedditMentionsClient:
    class reddit_mentions:
        @staticmethod
        def ticker(*args, **kwargs):
            df = pd.DataFrame({
                "subreddit": ["_all", "wallstreetbets", "stocks",
                              "_all", "wallstreetbets", "stocks"],
                "mentions": [120, 85, 12, 95, 60, 10],
                "date": pd.to_datetime([
                    "2024-01-01T08:00:00Z", "2024-01-01T08:00:00Z",
                    "2024-01-01T08:00:00Z", "2024-01-01T12:00:00Z",
                    "2024-01-01T12:00:00Z", "2024-01-01T12:00:00Z",
                ]),
            }).set_index("date")
            return df

        @staticmethod
        def screener(*args, **kwargs):
            return {
                "data": [
                    {"symbol": "TSLA", "name": "Tesla", "date": "2024-01-01T08:00:00Z",
                     "totalMentions": 120, "subreddits": {"wallstreetbets": 85, "stocks": 12}},
                    {"symbol": "AAPL", "name": "Apple", "date": "2024-01-01T08:00:00Z",
                     "totalMentions": 45, "subreddits": {"wallstreetbets": 30, "stocks": 8}},
                    {"symbol": "NVDA", "name": "NVIDIA", "date": "2024-01-01T08:00:00Z",
                     "totalMentions": 80, "subreddits": {"wallstreetbets": 60, "stocks": 5}},
                ],
                "summary": {},
            }


# ═══════════════════════════════════════════════════════════════════════════
# Validation tests (existing — kept intact)
# ═══════════════════════════════════════════════════════════════════════════

def test_options_plot_invalid_kind():
    """Test that options() raises ValueError for unknown kind."""
    plot = _PlotNamespace(MockClient())

    with pytest.raises(ValueError, match="Unknown kind 'invalid'"):
        plot.options("AAPL", kind="invalid")


def test_options_plot_valid_kind_requires_real_client():
    """Test that valid kind='put_call' requires a real client with data."""
    plot = _PlotNamespace(MockClient())

    # This should pass the kind check but fail when trying to call client methods
    with pytest.raises(AttributeError):
        plot.options("AAPL", kind="put_call")


def test_insider_transactions_empty_price_data():
    """Test that insider_transactions() raises ValueError for empty price_data."""
    plot = _PlotNamespace(MockClient())
    empty_df = pd.DataFrame()

    with pytest.raises(ValueError, match="price_data cannot be empty"):
        plot.insider_transactions("AAPL", price_data=empty_df)


def test_insider_transactions_missing_price_column():
    """Test that insider_transactions() raises ValueError when price column is missing."""
    plot = _PlotNamespace(MockClient())
    # DataFrame with wrong columns
    bad_df = pd.DataFrame({"volume": [100, 200], "high": [150, 151]})

    with pytest.raises(ValueError, match="price_data must contain a price column"):
        plot.insider_transactions("AAPL", price_data=bad_df)


def test_house_trades_empty_price_data():
    """Test that house_trades() raises ValueError for empty price_data."""
    plot = _PlotNamespace(MockClient())
    empty_df = pd.DataFrame()

    with pytest.raises(ValueError, match="price_data cannot be empty"):
        plot.house_trades("AAPL", price_data=empty_df)


def test_house_trades_missing_price_column():
    """Test that house_trades() raises ValueError when price column is missing."""
    plot = _PlotNamespace(MockClient())
    # DataFrame with wrong columns
    bad_df = pd.DataFrame({"volume": [100, 200], "high": [150, 151]})

    with pytest.raises(ValueError, match="price_data must contain a price column"):
        plot.house_trades("NVDA", price_data=bad_df)


def test_insider_transactions_accepts_various_price_columns():
    """Test that insider_transactions() accepts different price column names."""

    class MockClientWithData:
        class insider_transactions:
            @staticmethod
            def ticker(*args, **kwargs):
                return _empty_tx_df()

    plot = _PlotNamespace(MockClientWithData())

    for col in ["close", "Close", "price"]:
        price_df = pd.DataFrame(
            {col: [150, 151, 152], "date": pd.date_range("2024-01-01", periods=3)}
        ).set_index("date")
        fig = plot.insider_transactions("AAPL", price_data=price_df, show=False)
        assert fig is not None


def test_house_trades_accepts_various_price_columns():
    """Test that house_trades() accepts different price column names."""

    class MockClientWithData:
        class house_trades:
            @staticmethod
            def ticker(*args, **kwargs):
                return _empty_tx_df()

    plot = _PlotNamespace(MockClientWithData())

    price_df = pd.DataFrame(
        {"close": [150, 151, 152], "date": pd.date_range("2024-01-01", periods=3)}
    ).set_index("date")
    fig = plot.house_trades("NVDA", price_data=price_df, show=False)
    assert fig is not None


# ═══════════════════════════════════════════════════════════════════════════
# Functional tests — figure construction
# ═══════════════════════════════════════════════════════════════════════════

# ── app_ratings ────────────────────────────────────────────────────────────

def test_app_ratings_plot_android():
    plot = _PlotNamespace(MockAppRatingsClient())
    fig = plot.app_ratings("AMZN", store="play", show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # bar + line
    assert fig.data[0].type == "bar"
    assert fig.data[1].type == "scatter"
    assert "Android" in fig.layout.title.text


def test_app_ratings_plot_ios():
    plot = _PlotNamespace(MockAppRatingsClient())
    fig = plot.app_ratings("AMZN", store="app", show=False)

    assert isinstance(fig, go.Figure)
    assert "iOS" in fig.layout.title.text


def test_app_ratings_plot_invalid_store():
    plot = _PlotNamespace(MockAppRatingsClient())
    with pytest.raises(ValueError, match="store must be 'play' or 'app'"):
        plot.app_ratings("AMZN", store="invalid", show=False)


def test_app_ratings_plot_as_json():
    plot = _PlotNamespace(MockAppRatingsClient())
    result = plot.app_ratings("AMZN", store="play", show=False, as_json=True)
    assert isinstance(result, str)


# ── linkedin ───────────────────────────────────────────────────────────────

def test_linkedin_plot():
    plot = _PlotNamespace(MockLinkedInClient())
    fig = plot.linkedin("AMZN", show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # bar (employees) + line (followers)
    assert fig.data[0].type == "bar"
    assert fig.data[1].type == "scatter"
    assert "LinkedIn" in fig.layout.title.text


def test_linkedin_plot_as_json():
    plot = _PlotNamespace(MockLinkedInClient())
    result = plot.linkedin("AMZN", show=False, as_json=True)
    assert isinstance(result, str)


# ── sentiments ─────────────────────────────────────────────────────────────

def test_sentiments_plot():
    plot = _PlotNamespace(MockSentimentsClient())
    fig = plot.sentiments("AMZN", show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1  # single bar trace
    assert fig.data[0].type == "bar"
    assert "Sentiment" in fig.layout.title.text


def test_sentiments_plot_as_json():
    plot = _PlotNamespace(MockSentimentsClient())
    result = plot.sentiments("AMZN", show=False, as_json=True)
    assert isinstance(result, str)


# ── options ────────────────────────────────────────────────────────────────

def test_options_plot_put_call():
    plot = _PlotNamespace(MockOptionsClient())
    fig = plot.options("AMZN", kind="put_call", show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 3  # calls bar + puts bar + ratio line
    assert fig.data[0].type == "bar"   # calls
    assert fig.data[1].type == "bar"   # puts
    assert fig.data[2].type == "scatter"  # ratio
    assert "Options" in fig.layout.title.text


def test_options_plot_as_json():
    plot = _PlotNamespace(MockOptionsClient())
    result = plot.options("AMZN", kind="put_call", show=False, as_json=True)
    assert isinstance(result, str)


# ── predictions ────────────────────────────────────────────────────────────

def test_predictions_plot():
    plot = _PlotNamespace(MockPredictionsClient())
    fig = plot.predictions("AMZN", show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 3  # mid line + upper CI + lower CI (fill)
    assert "Prediction" in fig.layout.title.text


def test_predictions_plot_as_json():
    plot = _PlotNamespace(MockPredictionsClient())
    result = plot.predictions("AMZN", show=False, as_json=True)
    assert isinstance(result, str)


# ── insider_transactions ──────────────────────────────────────────────────

def test_insider_transactions_plot_with_data():
    plot = _PlotNamespace(MockInsiderClient())
    fig = plot.insider_transactions("AAPL", price_data=PRICE_DF, show=False)

    assert isinstance(fig, go.Figure)
    # At least price line + buy/sell markers
    assert len(fig.data) >= 1
    assert "Insider" in fig.layout.title.text


# ── house_trades ──────────────────────────────────────────────────────────

def test_house_trades_plot_with_data():
    plot = _PlotNamespace(MockHouseClient())
    fig = plot.house_trades("NVDA", price_data=PRICE_DF, show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert "House" in fig.layout.title.text


# ── senate_trades ─────────────────────────────────────────────────────────

def test_senate_trades_plot_with_data():
    plot = _PlotNamespace(MockSenateClient())
    fig = plot.senate_trades("META", price_data=PRICE_DF, show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert "Senate" in fig.layout.title.text


def test_senate_trades_empty_price_data():
    plot = _PlotNamespace(MockClient())
    with pytest.raises(ValueError, match="price_data cannot be empty"):
        plot.senate_trades("META", price_data=pd.DataFrame())


def test_senate_trades_missing_price_column():
    plot = _PlotNamespace(MockClient())
    bad_df = pd.DataFrame({"volume": [100, 200]})
    with pytest.raises(ValueError, match="price_data must contain a price column"):
        plot.senate_trades("META", price_data=bad_df)


# ── corporate_lobbying ────────────────────────────────────────────────────

def test_corporate_lobbying_plot():
    plot = _PlotNamespace(MockCorporateLobbyingClient())
    fig = plot.corporate_lobbying("AAPL", price_data=PRICE_DF, show=False)

    assert isinstance(fig, go.Figure)
    # price line + lobbying bars
    assert len(fig.data) >= 2
    assert "Lobbying" in fig.layout.title.text


def test_corporate_lobbying_empty_price_data():
    plot = _PlotNamespace(MockClient())
    with pytest.raises(ValueError, match="price_data cannot be empty"):
        plot.corporate_lobbying("AAPL", price_data=pd.DataFrame())


def test_corporate_lobbying_missing_price_column():
    plot = _PlotNamespace(MockClient())
    bad_df = pd.DataFrame({"volume": [100, 200]})
    with pytest.raises(ValueError, match="price_data must contain a price column"):
        plot.corporate_lobbying("AAPL", price_data=bad_df)


# ── reddit_mentions ───────────────────────────────────────────────────────

def test_reddit_mentions_plot():
    plot = _PlotNamespace(MockRedditMentionsClient())
    fig = plot.reddit_mentions("TSLA", price_data=PRICE_DF, show=False)

    assert isinstance(fig, go.Figure)
    # price line + one bar trace per subreddit (excluding _all)
    assert len(fig.data) >= 3  # price + stocks + wallstreetbets
    assert fig.data[0].type == "scatter"  # price line
    assert fig.data[1].type == "bar"
    assert "Reddit Mentions" in fig.layout.title.text
    assert fig.layout.barmode == "stack"


def test_reddit_mentions_empty_price_data():
    plot = _PlotNamespace(MockClient())
    with pytest.raises(ValueError, match="price_data cannot be empty"):
        plot.reddit_mentions("TSLA", price_data=pd.DataFrame())


def test_reddit_mentions_missing_price_column():
    plot = _PlotNamespace(MockClient())
    bad_df = pd.DataFrame({"volume": [100, 200]})
    with pytest.raises(ValueError, match="price_data must contain a price column"):
        plot.reddit_mentions("TSLA", price_data=bad_df)


def test_reddit_mentions_as_json():
    plot = _PlotNamespace(MockRedditMentionsClient())
    result = plot.reddit_mentions("TSLA", price_data=PRICE_DF, show=False, as_json=True)
    assert isinstance(result, str)


# ── reddit_mentions_screener ──────────────────────────────────────────────

def test_reddit_mentions_screener_plot():
    plot = _PlotNamespace(MockRedditMentionsClient())
    fig = plot.reddit_mentions_screener(show=False)

    assert isinstance(fig, go.Figure)
    # 2 subreddits → 2 bar traces (stocks, wallstreetbets)
    assert len(fig.data) == 2
    assert fig.data[0].type == "bar"
    assert fig.data[0].orientation == "h"
    assert fig.layout.barmode == "stack"
    assert "Top 3" in fig.layout.title.text
    # Verify ordering: highest-mentioned (TSLA) at top → last in y array
    symbols = list(fig.data[0].y)
    assert symbols[-1] == "TSLA"
    assert symbols[0] == "AAPL"  # lowest mentions


def test_reddit_mentions_screener_top_n():
    plot = _PlotNamespace(MockRedditMentionsClient())
    fig = plot.reddit_mentions_screener(top_n=2, show=False)

    assert isinstance(fig, go.Figure)
    # Only top 2 tickers
    symbols = list(fig.data[0].y)
    assert len(symbols) == 2
    assert "TSLA" in symbols
    assert "NVDA" in symbols
    assert "AAPL" not in symbols


def test_reddit_mentions_screener_empty_data():
    class EmptyScreenerClient:
        class reddit_mentions:
            @staticmethod
            def screener(*args, **kwargs):
                return {"data": [], "summary": {}}

    plot = _PlotNamespace(EmptyScreenerClient())
    with pytest.raises(ValueError, match="No screener data returned"):
        plot.reddit_mentions_screener(show=False)


def test_reddit_mentions_screener_as_json():
    plot = _PlotNamespace(MockRedditMentionsClient())
    result = plot.reddit_mentions_screener(show=False, as_json=True)
    assert isinstance(result, str)


def test_reddit_mentions_screener_latest_snapshot():
    """Verify that only the latest snapshot per ticker is used."""

    class MultiSnapshotClient:
        class reddit_mentions:
            @staticmethod
            def screener(*args, **kwargs):
                return {
                    "data": [
                        {"symbol": "TSLA", "date": "2024-01-01T04:00:00Z",
                         "totalMentions": 50, "subreddits": {"wsb": 30}},
                        {"symbol": "TSLA", "date": "2024-01-01T08:00:00Z",
                         "totalMentions": 120, "subreddits": {"wsb": 85}},
                    ],
                    "summary": {},
                }

    plot = _PlotNamespace(MultiSnapshotClient())
    fig = plot.reddit_mentions_screener(show=False)

    # Should use the 08:00 snapshot (120 mentions), not 04:00 (50)
    assert fig.data[0].x == (85,)  # wsb=85 from the latest snapshot
