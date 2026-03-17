# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2026-03-17

### Added

- **Reddit Mentions Endpoint**: `fb.reddit_mentions.ticker("TSLA")` — fetch per-subreddit mention counts with full timestamps (sampled every 4 hours) (`/reddit-mentions/{SYMBOL}`)
- **Reddit Mentions Screener**: `fb.reddit_mentions.screener()` — cross-ticker Reddit mentions with aggregated totals and per-subreddit breakdowns (`/screener/reddit-mentions`)
- **Reddit Mentions Plotting**: `fb.plot.reddit_mentions()` — stacked bars per subreddit overlaid on a price chart; `fb.plot.reddit_mentions_screener()` — horizontal stacked bar chart of top N most mentioned tickers from the latest screener snapshot
- **Async Reddit Mentions**: Full async support via `AsyncRedditMentionsAPI`
- **Reddit Mentions Tests**: Unit tests (`tests/test_reddit_mentions.py`) covering ticker, screener, DataFrame, and error handling

## [0.2.1] - 2026-03-12

### Added

- **Corporate Lobbying Endpoint**: `fb.corporate_lobbying.ticker("AAPL")` — fetch corporate lobbying filings with income, expenses, registrant details, issue codes, and government entities (`/lobbying/{SYMBOL}`)
- **Corporate Lobbying Plotting**: `fb.plot.corporate_lobbying()` — visualize lobbying spend (income + expenses) as bars on a secondary y-axis overlaid on a price chart, with hover details showing registrant, quarter, income, and expenses
- **Async Corporate Lobbying**: Full async support via `AsyncCorporateLobbyingAPI`
- **Corporate Lobbying Tests**: Unit tests (`tests/test_corporate_lobbying.py`) and integration tests

## [0.2.0] - 2026-03-09

### BREAKING CHANGES

- **v2 API Migration**: SDK now targets FinBrain API v2 (`/v2/` base URL)
- **Authentication**: Switched from `?token=` query parameter to `Authorization: Bearer` header
- **`market` parameter removed**: All per-symbol endpoint methods no longer accept `market` as an argument (v2 API identifies tickers by symbol alone)
  - Affected: `sentiments.ticker()`, `analyst_ratings.ticker()`, `app_ratings.ticker()`, `options.put_call()`, `insider_transactions.ticker()`, `house_trades.ticker()`, `senate_trades.ticker()`, `linkedin_data.ticker()`, and all plotting methods
- **`predictions.market()` removed**: Use `screener.predictions_daily()` or `screener.predictions_monthly()` instead
- **`sentiments.ticker()` `days` parameter removed**: Use `date_from`/`date_to` instead
- **Response envelope**: All v2 responses are wrapped in `{"success": true, "data": ..., "meta": {...}}`. The SDK auto-unwraps this — endpoint methods return just the `data` portion
- **Prediction DataFrame columns**: `main` column renamed to `mid` (matching v2 API)
- **App Ratings DataFrame columns**: Flat columns like `playStoreScore` replaced with nested-then-flattened `ios_score`, `android_score`, `ios_ratingsCount`, `android_ratingsCount`, `android_installCount`
- **Options DataFrame columns**: `callCount`/`putCount` renamed to `callVolume`/`putVolume`
- **LinkedIn DataFrame columns**: `followersCount` renamed to `followerCount`
- **v2 API paths changed**: All endpoint URLs updated (e.g., `/sentiments/{MARKET}/{TICKER}` → `/sentiment/{SYMBOL}`, `/housetrades/` → `/congress/house/`, etc.)
- **Date query parameters**: Internal mapping changed from `dateFrom`/`dateTo` to `startDate`/`endDate` (Python parameter names `date_from`/`date_to` unchanged)
- **Markets response format**: `available.markets()` now returns `[{"name": "S&P 500", "region": "US"}, ...]` instead of `["S&P 500", ...]`

### Added

- **News Endpoint**: `fb.news.ticker("AAPL")` — fetch news articles with sentiment scores (`/news/{SYMBOL}`)
- **Screener Endpoints**: `fb.screener.*` — cross-ticker screening with 11 methods:
  - `sentiment()`, `analyst_ratings()`, `insider_trading()`, `congress_house()`, `congress_senate()`, `news()`, `put_call_ratio()`, `linkedin()`, `app_ratings()`, `predictions_daily()`, `predictions_monthly()`
- **Recent Data Endpoints**: `fb.recent.news()`, `fb.recent.analyst_ratings()` — latest data across all tracked stocks
- **Regions Endpoint**: `fb.available.regions()` — markets grouped by region
- **`limit` parameter**: Added to all per-symbol endpoints and screener/recent endpoints
- **`RateLimitError` exception**: New exception for HTTP 429 responses
- **`error_code` and `error_details` attributes**: Added to `FinBrainError` for v2 structured error responses
- **`client.last_meta`**: Stores the `meta` object from the last API response (contains `timestamp`)
- **Async parity**: All new endpoints have full async counterparts
- **Envelope tests**: `tests/test_envelope.py` dedicated tests for v2 response handling
- **79 unit tests**: Comprehensive test coverage for all v2 endpoints

### Changed

- **Base URL**: `https://api.finbrain.tech/v1/` → `https://api.finbrain.tech/v2/`
- **Error message extraction**: Updated to handle v2 error format `{"error": {"code": "...", "message": "..."}}`
- **Insider transactions date parsing**: Simplified from custom `"%b %d '%y"` format to standard ISO dates
- **All plotting methods**: Updated for v2 column names and removed `market` parameter

## [0.1.8] - 2025-12-27

### Added

- **Senate Trades Endpoint**: `fb.senate_trades.ticker()` - Fetch U.S. Senator trading activity (`/senatetrades/{MARKET}/{TICKER}`)
- **Senate Trades Plotting**: `fb.plot.senate_trades()` - Visualize Senator trades on price charts
- **Async Senate Trades**: Full async support via `AsyncSenateTradesAPI`
- **Python 3.14 Support**: Added to CI test matrix (now testing 3.9-3.14)
- **Senate Trades Tests**: `tests/test_senate_trades.py`

## [0.1.7] - 2025-10-02

### Added

- **Insider Transactions Plotting**: `fb.plot.insider_transactions()` - Overlay insider buy/sell markers on user-provided price charts
- **House Trades Plotting**: `fb.plot.house_trades()` - Visualize U.S. House member trades on price charts
- **Transaction Plotting Example**: `examples/transactions_plotting_example.py` demonstrating integration with various price data sources
- **Plotting Tests**: Extended `tests/test_plotting.py` with 8 new test cases for transaction plotting

### Changed

- **Price Data Flexibility**: Plotting methods now auto-detect multiple price column formats (`close`, `Close`, `price`, `Price`, `adj_close`, `Adj Close`)
- **MultiIndex Support**: Transaction plotting methods now handle yfinance's MultiIndex column format (from `yf.download()`)
- **Timezone Handling**: Automatic timezone normalization to handle timezone-aware price data (e.g., from yfinance)

### Fixed

- **Column Detection**: Fixed `KeyError` when house trades API returns `type` column instead of `transaction`
- **yfinance Compatibility**: Fixed price line not displaying when using `yf.download()` due to MultiIndex columns

## [0.1.6] - 2025-10-02

### Added

- **Async Support**: Full async/await implementation using `httpx`
  - `AsyncFinBrainClient` with context manager support
  - All 9 endpoints have async equivalents
  - Install with: `pip install finbrain-python[async]`
  - Example: `examples/async_example.py`
- **Python 3.13 Support**: Added to CI test matrix (now testing 3.9, 3.10, 3.11, 3.12, 3.13)
- **Async utilities module**: `src/finbrain/aio/endpoints/_utils.py`
- **Sync utilities module**: `src/finbrain/endpoints/_utils.py`
- **Plotting tests**: `tests/test_plotting.py`
- **Async client tests**: `tests/test_async_client.py`
- **Release guide**: `RELEASE.md` with tag conventions

### Changed

- **Tag Convention**: Now using `v` prefix (e.g., `v0.1.6` instead of `0.1.6`)
- **GitHub Actions**: Updated to trigger on `v[0-9]*` tags
- **Code Deduplication**: Consolidated 12 duplicate `_to_datestr()` helpers into 2 utility modules
- **README**: Added async usage section with examples

### Fixed

- **Plotting Error Handling**: `options()` method now raises clear `ValueError` for invalid `kind` parameter instead of `NameError`

### Dependencies

- Added `httpx>=0.24` as optional dependency for async support
- Added `pytest-asyncio` as dev dependency

## [0.1.5] - 2024-09-18

Previous releases...

## [0.1.4] - 2024-06-25

Previous releases...

## [0.1.3] - 2024-06-13

Previous releases...

## [0.1.2] - 2024-06-13

Previous releases...

## [0.1.1] - 2024-06-13

Previous releases...

[0.2.1]: https://github.com/ahmetsbilgin/finbrain-python/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/ahmetsbilgin/finbrain-python/compare/v0.1.8...v0.2.0
[0.1.8]: https://github.com/ahmetsbilgin/finbrain-python/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/ahmetsbilgin/finbrain-python/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.5...v0.1.6
[0.1.5]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.4...0.1.5
[0.1.4]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.2...0.1.3
[0.1.2]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/ahmetsbilgin/finbrain-python/releases/tag/0.1.1
