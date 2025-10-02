# FinBrain Python SDK&nbsp;<!-- omit in toc -->

[![PyPI version](https://img.shields.io/pypi/v/finbrain-python.svg)](https://pypi.org/project/finbrain-python/)
[![CI](https://github.com/ahmetsbilgin/finbrain-python/actions/workflows/ci.yml/badge.svg)](https://github.com/ahmetsbilgin/finbrain-python/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

**Official Python client** for the [FinBrain API](https://docs.finbrain.tech).  
Fetch deep-learning price predictions, sentiment scores, insider trades, LinkedIn metrics, options data and more — with a single import.

*Python ≥ 3.9  •  requests, pandas, numpy & plotly  •  asyncio optional.*

---

## ✨ Features

- One-line auth (`FinBrainClient(api_key="…")`)
- Complete endpoint coverage (predictions, sentiments, options, insider, etc.)
- Transparent retries & custom error hierarchy (`FinBrainError`)
- Async parity with `finbrain.aio` (`httpx`)
- CLI (`finbrain markets`, `finbrain predict AAPL`)
- Auto-version from Git tags (setuptools-scm)
- MIT-licensed, fully unit-tested

---

## 🚀 Quick start

Install the SDK:

```bash
pip install finbrain-python
```

Create a client and fetch data:

```python
from finbrain import FinBrainClient

fb = FinBrainClient(api_key="YOUR_KEY")        # create once, reuse below

# ---------- availability ----------
fb.available.markets()                         # list markets
fb.available.tickers("daily", as_dataframe=True)

# ---------- app ratings ----------
fb.app_ratings.ticker("S&P 500", "AMZN",
                      date_from="2025-01-01",
                      date_to="2025-06-30",
                      as_dataframe=True)

# ---------- analyst ratings ----------
fb.analyst_ratings.ticker("S&P 500", "AMZN",
                          date_from="2025-01-01",
                          date_to="2025-06-30",
                          as_dataframe=True)

# ---------- house trades ----------
fb.house_trades.ticker("S&P 500", "AMZN",
                       date_from="2025-01-01",
                       date_to="2025-06-30",
                       as_dataframe=True)

# ---------- insider transactions ----------
fb.insider_transactions.ticker("S&P 500", "AMZN", as_dataframe=True)

# ---------- LinkedIn metrics ----------
fb.linkedin_data.ticker("S&P 500", "AMZN",
                        date_from="2025-01-01",
                        date_to="2025-06-30",
                        as_dataframe=True)

# ---------- options put/call ----------
fb.options.put_call("S&P 500", "AMZN",
                    date_from="2025-01-01",
                    date_to="2025-06-30",
                    as_dataframe=True)

# ---------- price predictions ----------
fb.predictions.market("S&P 500", as_dataframe=True)   # all tickers in market
fb.predictions.ticker("AMZN", as_dataframe=True)      # single ticker

# ---------- news sentiment ----------
fb.sentiments.ticker("S&P 500", "AMZN",
                     date_from="2025-01-01",
                     date_to="2025-06-30",
                     as_dataframe=True)
```

## ⚡ Async Usage

For async/await support, install with the `async` extra:

```bash
pip install finbrain-python[async]
```

Then use `AsyncFinBrainClient` with `httpx`:

```python
import asyncio
from finbrain.aio import AsyncFinBrainClient

async def main():
    async with AsyncFinBrainClient(api_key="YOUR_KEY") as fb:
        # All methods are async and return the same data structures
        markets = await fb.available.markets()

        # Fetch predictions
        predictions = await fb.predictions.ticker("AMZN", as_dataframe=True)

        # Fetch sentiment data
        sentiment = await fb.sentiments.ticker(
            "S&P 500", "AMZN",
            date_from="2025-01-01",
            date_to="2025-06-30",
            as_dataframe=True
        )

        # All other endpoints work the same way
        app_ratings = await fb.app_ratings.ticker("S&P 500", "AMZN", as_dataframe=True)
        analyst_ratings = await fb.analyst_ratings.ticker("S&P 500", "AMZN", as_dataframe=True)

asyncio.run(main())
```

**Note**: The async client uses `httpx.AsyncClient` and must be used with `async with` context manager for proper resource cleanup.

## 📈 Plotting

Plot helpers in a nutshell

- `show` – defaults to True, so the chart appears immediately.

- `as_json=True` – skips display and returns the figure as a Plotly-JSON string, ready to embed elsewhere.

```python
# ---------- App Ratings Chart - Apple App Store or Google Play Store ----------
fb.plot.app_ratings("S&P 500", "AMZN",
                    store="app",                # "play" for Google Play Store
                    date_from="2025-01-01",
                    date_to="2025-06-30")

# ---------- LinkedIn Metrics Chart ----------
fb.plot.linkedin("S&P 500", "AMZN",
                 date_from="2025-01-01",
                 date_to="2025-06-30")

# ---------- Put-Call Ratio Chart ----------
fb.plot.options("S&P 500", "AMZN",
                kind="put_call",
                date_from="2025-01-01",
                date_to="2025-06-30")

# ---------- Predictions Chart ----------
fb.plot.predictions("AMZN")         # prediction_type="monthly" for monthly predictions

# ---------- Sentiments Chart ----------
fb.plot.sentiments("S&P 500", "AMZN",
                   date_from="2025-01-01",
                   date_to="2025-06-30")

# ---------- Insider Transactions & House Trades (requires user price data) ----------
# These plots overlay transaction markers on a price chart.
# Since FinBrain doesn't provide historical prices, you must provide your own:

import pandas as pd

# Example: Load your price data from any legal source
# (broker API, licensed data provider, CSV file, etc.)
price_df = pd.DataFrame({
    "close": [150.25, 151.30, 149.80],  # Your price data
    "date": pd.date_range("2025-01-01", periods=3)
}).set_index("date")

# Plot insider transactions on your price chart
fb.plot.insider_transactions("S&P 500", "AAPL", price_data=price_df)

# Plot House member trades on your price chart
fb.plot.house_trades("S&P 500", "NVDA",
                     price_data=price_df,
                     date_from="2025-01-01",
                     date_to="2025-06-30")
```

**Price Data Requirements:**

- DataFrame with DatetimeIndex
- Must contain a price column: `close`, `Close`, `price`, `Price`, `adj_close`, or `Adj Close`
- Obtain from legal sources: broker API, Bloomberg, Alpha Vantage, FMP, etc.

## 🔑 Authentication

To call the API you need an **API key**, obtained by purchasing a **FinBrain API subscription**.  
*(The Terminal-only subscription does **not** include an API key.)*

1. Subscribe at <https://www.finbrain.tech> → FinBrain API.
2. Copy the key from your dashboard.
3. Pass it once when you create the client:

```python
from finbrain import FinBrainClient
fb = FinBrainClient(api_key="YOUR_KEY")
```

---

## 📚 Supported endpoints

| Category             | Method                                   | Path                                                 |
|----------------------|------------------------------------------|------------------------------------------------------|
| Availability         | `client.available.markets()`             | `/available/markets`                                 |
|                      | `client.available.tickers()`             | `/available/tickers/{TYPE}`                          |
| Predictions          | `client.predictions.ticker()`            | `/ticker/{TICKER}/predictions/{daily\|monthly}`      |
|                      | `client.predictions.market()`            | `/market/{MARKET}/predictions/{daily\|monthly}`      |
| Sentiments           | `client.sentiments.ticker()`             | `/sentiments/{MARKET}/{TICKER}`                      |
| App ratings          | `client.app_ratings.ticker()`            | `/appratings/{MARKET}/{TICKER}`                      |
| Analyst ratings      | `client.analyst_ratings.ticker()`        | `/analystratings/{MARKET}/{TICKER}`                  |
| House trades         | `client.house_trades.ticker()`           | `/housetrades/{MARKET}/{TICKER}`                     |
| Insider transactions | `client.insider_transactions.ticker()`   | `/insidertransactions/{MARKET}/{TICKER}`             |
| LinkedIn             | `client.linkedin_data.ticker()`          | `/linkedindata/{MARKET}/{TICKER}`                    |
| Options – Put/Call   | `client.options.put_call()`              | `/putcalldata/{MARKET}/{TICKER}`                     |

---

## 🛠️ Error-handling

```python
from finbrain.exceptions import BadRequest
try:
    fb.predictions.ticker("MSFT", prediction_type="weekly")
except BadRequest as exc:
    print("Invalid parameters:", exc)
```

| HTTP status | Exception class          | Meaning                               |
|-------------|--------------------------|---------------------------------------|
| 400         | `BadRequest`             | The request is invalid or malformed   |
| 401         | `AuthenticationError`    | API key missing or incorrect          |
| 403         | `PermissionDenied`       | Authenticated, but not authorised     |
| 404         | `NotFound`               | Resource or endpoint not found        |
| 405         | `MethodNotAllowed`       | HTTP method not supported on endpoint |
| 500         | `ServerError`            | FinBrain internal error               |

---

## 🔄 Versioning & release

- Semantic Versioning (`MAJOR.MINOR.PATCH`)

- Version auto-generated from Git tags (setuptools-scm)

```bash
git tag -a v0.2.0 -m "Add options.chain endpoint"
git push --tags # GitHub Actions builds & uploads to PyPI
```

---

## 🧑‍💻 Development

```bash
git clone https://github.com/finbrain-tech/finbrain-python
cd finbrain-python
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]

ruff check . # lint / format
pytest -q # unit tests (mocked) 
```

### Live integration test(currently under development)

Set `FINBRAIN_LIVE_KEY`, then run:

```bash
pytest -m integration
```

---

## 🤝 Contributing

1. Fork → create a feature branch

2. Add tests & run `ruff --fix`

3. Ensure `pytest` & CI pass

4. Open a PR — thanks!

---

## 🔒 Security

Please report vulnerabilities to **<info@finbrain.tech>**.  
We respond within 48 hours.

---

## 📜 License

MIT — see [LICENSE](LICENSE).

---

© 2025 FinBrain Technologies — Built with ❤️ for the quant community.
