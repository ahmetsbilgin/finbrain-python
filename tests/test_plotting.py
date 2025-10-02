"""Tests for plotting module error handling."""

import pytest
import pandas as pd
from finbrain.plotting import _PlotNamespace


class MockClient:
    """Mock client for testing plotting namespace."""

    pass


def test_options_plot_invalid_kind():
    """Test that options() raises ValueError for unknown kind."""
    plot = _PlotNamespace(MockClient())

    with pytest.raises(ValueError, match="Unknown kind 'invalid'"):
        plot.options("S&P 500", "AAPL", kind="invalid")


def test_options_plot_valid_kind_requires_real_client():
    """Test that valid kind='put_call' requires a real client with data."""
    plot = _PlotNamespace(MockClient())

    # This should pass the kind check but fail when trying to call client methods
    with pytest.raises(AttributeError):
        plot.options("S&P 500", "AAPL", kind="put_call")


def test_insider_transactions_empty_price_data():
    """Test that insider_transactions() raises ValueError for empty price_data."""
    plot = _PlotNamespace(MockClient())
    empty_df = pd.DataFrame()

    with pytest.raises(ValueError, match="price_data cannot be empty"):
        plot.insider_transactions("S&P 500", "AAPL", price_data=empty_df)


def test_insider_transactions_missing_price_column():
    """Test that insider_transactions() raises ValueError when price column is missing."""
    plot = _PlotNamespace(MockClient())
    # DataFrame with wrong columns
    bad_df = pd.DataFrame({"volume": [100, 200], "high": [150, 151]})

    with pytest.raises(ValueError, match="price_data must contain a price column"):
        plot.insider_transactions("S&P 500", "AAPL", price_data=bad_df)


def test_house_trades_empty_price_data():
    """Test that house_trades() raises ValueError for empty price_data."""
    plot = _PlotNamespace(MockClient())
    empty_df = pd.DataFrame()

    with pytest.raises(ValueError, match="price_data cannot be empty"):
        plot.house_trades("S&P 500", "AAPL", price_data=empty_df)


def test_house_trades_missing_price_column():
    """Test that house_trades() raises ValueError when price column is missing."""
    plot = _PlotNamespace(MockClient())
    # DataFrame with wrong columns
    bad_df = pd.DataFrame({"volume": [100, 200], "high": [150, 151]})

    with pytest.raises(ValueError, match="price_data must contain a price column"):
        plot.house_trades("S&P 500", "NVDA", price_data=bad_df)


def test_insider_transactions_accepts_various_price_columns():
    """Test that insider_transactions() accepts different price column names."""

    class MockClientWithData:
        """Mock client that returns empty transaction data."""

        class insider_transactions:
            @staticmethod
            def ticker(*args, **kwargs):
                # Return empty DataFrame with expected structure (insider uses 'transaction')
                df = pd.DataFrame({"transaction": []})
                df.index = pd.DatetimeIndex([])
                df.index.name = "date"
                return df

    plot = _PlotNamespace(MockClientWithData())

    # Test with 'close' column
    price_df = pd.DataFrame(
        {"close": [150, 151, 152], "date": pd.date_range("2024-01-01", periods=3)}
    ).set_index("date")

    fig = plot.insider_transactions("S&P 500", "AAPL", price_data=price_df, show=False)
    assert fig is not None

    # Test with 'Close' column (capitalized)
    price_df2 = pd.DataFrame(
        {"Close": [150, 151, 152], "date": pd.date_range("2024-01-01", periods=3)}
    ).set_index("date")

    fig2 = plot.insider_transactions(
        "S&P 500", "AAPL", price_data=price_df2, show=False
    )
    assert fig2 is not None

    # Test with 'price' column
    price_df3 = pd.DataFrame(
        {"price": [150, 151, 152], "date": pd.date_range("2024-01-01", periods=3)}
    ).set_index("date")

    fig3 = plot.insider_transactions(
        "S&P 500", "AAPL", price_data=price_df3, show=False
    )
    assert fig3 is not None


def test_house_trades_accepts_various_price_columns():
    """Test that house_trades() accepts different price column names."""

    class MockClientWithData:
        """Mock client that returns empty transaction data."""

        class house_trades:
            @staticmethod
            def ticker(*args, **kwargs):
                # Return empty DataFrame with expected structure (house uses 'type')
                df = pd.DataFrame({"type": []})
                df.index = pd.DatetimeIndex([])
                df.index.name = "date"
                return df

    plot = _PlotNamespace(MockClientWithData())

    # Test with 'close' column
    price_df = pd.DataFrame(
        {"close": [150, 151, 152], "date": pd.date_range("2024-01-01", periods=3)}
    ).set_index("date")

    fig = plot.house_trades("S&P 500", "NVDA", price_data=price_df, show=False)
    assert fig is not None
