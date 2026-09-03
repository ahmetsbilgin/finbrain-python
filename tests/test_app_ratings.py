# tests/test_app_ratings.py
import pytest
import pandas as pd
from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_app_ratings_raw(client, _activate_responses):
    """Endpoint returns the original JSON shape."""
    path = f"app-ratings/{TICKER}"
    payload = wrap_v2(
        {
            "symbol": "AMZN",
            "name": "Amazon.com Inc.",
            "data": [
                {
                    "date": "2024-01-15",
                    "ios": {"score": 4.07, "ratingsCount": 88533},
                    "android": {
                        "score": 3.75,
                        "ratingsCount": 567996,
                        "installCount": None,
                    },
                }
            ],
        }
    )

    stub_json(_activate_responses, "GET", path, payload)

    data = client.app_ratings.ticker(symbol=TICKER)
    assert data["symbol"] == "AMZN"
    assert isinstance(data["data"], list)


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_app_ratings_dataframe(client, _activate_responses):
    """Endpoint returns a DataFrame with `date` as the index."""
    path = f"app-ratings/{TICKER}"
    payload = wrap_v2(
        {
            "symbol": "AMZN",
            "name": "Amazon.com Inc.",
            "data": [
                {
                    "date": "2024-01-15",
                    "ios": {"score": 4.07, "ratingsCount": 88533},
                    "android": {
                        "score": 3.75,
                        "ratingsCount": 567996,
                        "installCount": None,
                    },
                }
            ],
        }
    )

    stub_json(_activate_responses, "GET", path, payload)

    df = client.app_ratings.ticker(symbol=TICKER, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert set(df.columns) == {
        "ios_score",
        "ios_ratingsCount",
        "android_score",
        "android_ratingsCount",
        "android_installCount",
    }
    assert df.loc["2024-01-15", "ios_score"] == 4.07
    assert df.loc["2024-01-15", "android_ratingsCount"] == 567996


# ─────────── error mapping ──────────────────────────────────────────────
def test_app_ratings_bad_request(client, _activate_responses):
    path = f"app-ratings/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )
    with pytest.raises(BadRequest):
        client.app_ratings.ticker(symbol=TICKER)


# ─────────── per-app (granular) branch ──────────────────────────────────
def _per_app_payload():
    """A two-app iOS company plus one pre-per-app observation."""
    return wrap_v2(
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "data": [
                {
                    "date": "2026-09-01",
                    "ios": {"score": 4.89, "ratingsCount": 8_803_317},
                    "android": {
                        "score": 4.58,
                        "ratingsCount": 748_106,
                        "installCount": 201_947_094,
                    },
                }
            ],
            "apps": [
                {
                    "platform": "ios",
                    "appId": "284882215",
                    "appName": "Shazam",
                    "observations": [
                        {
                            "date": "2026-09-01",
                            "score": 4.89,
                            "ratingsCount": 8_803_317,
                            "installCount": None,
                        },
                        {
                            "date": "2026-08-01",
                            "score": 4.88,
                            "ratingsCount": 8_700_000,
                            "installCount": None,
                        },
                    ],
                },
                {
                    "platform": "ios",
                    "appId": "1108187390",
                    "appName": "Apple Music",
                    "observations": [
                        {
                            "date": "2026-09-01",
                            "score": 4.86,
                            "ratingsCount": 3_074_796,
                            "installCount": None,
                        }
                    ],
                },
                {
                    # Pre-per-app observation: platform known, app not.
                    "platform": "android",
                    "appId": None,
                    "appName": None,
                    "observations": [
                        {
                            "date": "2024-01-05",
                            "score": 4.1,
                            "ratingsCount": 500,
                            "installCount": 10_000,
                        }
                    ],
                },
            ],
        }
    )


def test_app_ratings_per_app_dataframe(client, _activate_responses):
    """per_app=True yields one row per app per observation, not a blend."""
    path = "app-ratings/AAPL"
    stub_json(_activate_responses, "GET", path, _per_app_payload())

    df = client.app_ratings.ticker("AAPL", as_dataframe=True, per_app=True)

    assert isinstance(df, pd.DataFrame)
    # 2 Shazam + 1 Apple Music + 1 legacy android
    assert len(df) == 4
    assert set(df.columns) >= {
        "date",
        "platform",
        "app_id",
        "app_name",
        "score",
        "ratings_count",
        "install_count",
    }
    # A date repeats across apps, so it must NOT be the index
    assert df.index.name != "date"
    assert (df["date"] == "2026-09-01").sum() == 2


def test_app_ratings_per_app_keeps_unidentified_observations(
    client, _activate_responses
):
    """A row predating per-app keying is kept with app_id None, not dropped."""
    stub_json(_activate_responses, "GET", "app-ratings/AAPL", _per_app_payload())

    df = client.app_ratings.ticker("AAPL", as_dataframe=True, per_app=True)
    legacy = df[df["app_id"].isna()]

    assert len(legacy) == 1
    assert legacy.iloc[0]["platform"] == "android"
    # platform is known even when the app is not
    assert legacy.iloc[0]["install_count"] == 10_000


def test_app_ratings_blended_view_is_unchanged(client, _activate_responses):
    """Default stays the per-date blended frame, so existing callers are safe."""
    stub_json(_activate_responses, "GET", "app-ratings/AAPL", _per_app_payload())

    df = client.app_ratings.ticker("AAPL", as_dataframe=True)

    assert df.index.name == "date"
    assert "ios_score" in df.columns
    assert "app_id" not in df.columns


def test_app_ratings_per_app_empty_when_api_predates_apps(client, _activate_responses):
    """An older API sends no apps[]; ask for per_app and get an empty frame."""
    payload = wrap_v2(
        {
            "symbol": "AMZN",
            "name": "Amazon.com Inc.",
            "data": [
                {
                    "date": "2024-01-15",
                    "ios": {"score": 4.07, "ratingsCount": 88533},
                    "android": None,
                }
            ],
        }
    )
    stub_json(_activate_responses, "GET", "app-ratings/AMZN", payload)

    df = client.app_ratings.ticker("AMZN", as_dataframe=True, per_app=True)
    assert isinstance(df, pd.DataFrame)
    assert df.empty
