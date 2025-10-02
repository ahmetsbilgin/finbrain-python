"""Tests for plotting module error handling."""

import pytest
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
