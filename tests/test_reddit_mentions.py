# tests/test_reddit_mentions.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "TSLA"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_reddit_mentions_raw_ok(client, _activate_responses):
    path = f"reddit-mentions/{TICKER}"
    payload = wrap_v2({
        "symbol": "TSLA",
        "name": "Tesla, Inc.",
        "data": [
            {
                "date": "2026-03-17T08:00:00.000Z",
                "subreddit": "_all",
                "mentions": 120,
            },
            {
                "date": "2026-03-17T08:00:00.000Z",
                "subreddit": "wallstreetbets",
                "mentions": 85,
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.reddit_mentions.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 2
    assert data["data"][0]["subreddit"] == "_all"
    assert data["data"][0]["mentions"] == 120


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_reddit_mentions_dataframe_ok(client, _activate_responses):
    path = f"reddit-mentions/{TICKER}"
    payload = wrap_v2({
        "symbol": "TSLA",
        "name": "Tesla, Inc.",
        "data": [
            {
                "date": "2026-03-17T08:00:00.000Z",
                "subreddit": "_all",
                "mentions": 120,
            },
            {
                "date": "2026-03-17T08:00:00.000Z",
                "subreddit": "wallstreetbets",
                "mentions": 85,
            },
            {
                "date": "2026-03-17T12:00:00.000Z",
                "subreddit": "_all",
                "mentions": 95,
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.reddit_mentions.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "subreddit" in df.columns
    assert "mentions" in df.columns
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    # Verify timestamps preserve time component (UTC-aware from ISO Z suffix)
    assert pd.Timestamp("2026-03-17 08:00:00", tz="UTC") in df.index
    assert pd.Timestamp("2026-03-17 12:00:00", tz="UTC") in df.index


# ─────────── error mapping ──────────────────────────────────────────────
def test_reddit_mentions_bad_request(client, _activate_responses):
    path = f"reddit-mentions/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.reddit_mentions.ticker(symbol=TICKER)


# ─────────── screener raw JSON ──────────────────────────────────────────
def test_reddit_mentions_screener_raw_ok(client, _activate_responses):
    path = "screener/reddit-mentions"
    payload = wrap_v2({
        "data": [
            {
                "symbol": "TSLA",
                "name": "Tesla, Inc.",
                "date": "2026-03-17T08:00:00.000Z",
                "totalMentions": 120,
                "subreddits": {"wallstreetbets": 85, "stocks": 12},
            },
        ],
        "summary": {
            "totalEntries": 1,
            "totalTickers": 1,
            "averageMentions": 120,
            "topMentioned": ["TSLA"],
            "subredditNames": ["stocks", "wallstreetbets"],
        },
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.screener.reddit_mentions()
    assert isinstance(data, list)
    assert data[0]["symbol"] == "TSLA"
    assert data[0]["totalMentions"] == 120


# ─────────── screener DataFrame ─────────────────────────────────────────
def test_reddit_mentions_screener_dataframe_ok(client, _activate_responses):
    path = "screener/reddit-mentions"
    payload = wrap_v2({
        "data": [
            {
                "symbol": "TSLA",
                "name": "Tesla, Inc.",
                "date": "2026-03-17T08:00:00.000Z",
                "totalMentions": 120,
                "subreddits": {"wallstreetbets": 85, "stocks": 12},
            },
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "date": "2026-03-17T12:00:00.000Z",
                "totalMentions": 45,
                "subreddits": {"wallstreetbets": 30, "stocks": 8},
            },
        ],
        "summary": {
            "totalEntries": 2,
            "totalTickers": 2,
            "averageMentions": 82.5,
            "topMentioned": ["TSLA", "AAPL"],
            "subredditNames": ["stocks", "wallstreetbets"],
        },
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.screener.reddit_mentions(as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert "totalMentions" in df.columns
