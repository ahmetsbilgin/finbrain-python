# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/ahmetsbilgin/finbrain-python/compare/v0.1.7...HEAD
[0.1.7]: https://github.com/ahmetsbilgin/finbrain-python/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.5...v0.1.6
[0.1.5]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.4...0.1.5
[0.1.4]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.2...0.1.3
[0.1.2]: https://github.com/ahmetsbilgin/finbrain-python/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/ahmetsbilgin/finbrain-python/releases/tag/0.1.1
