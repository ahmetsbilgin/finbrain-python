# FinBrain Python SDK&nbsp;<!-- omit in toc -->

[![PyPI version](https://img.shields.io/pypi/v/finbrain-python.svg)](https://pypi.org/project/finbrain-python/)
[![CI](https://github.com/finbrain-tech/finbrain-python/actions/workflows/ci.yml/badge.svg)](https://github.com/finbrain-tech/finbrain-python/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

**Official Python client** for the [FinBrain API](https://docs.finbrain.tech).  
Fetch deep-learning price predictions, sentiment scores, insider trades, LinkedIn metrics, options data and more — with a single import.

*Python ≥ 3.9  •  requests  •  asyncio optional.*

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
```
pip install finbrain
```
Create a client and fetch data:
```
from finbrain import FinBrainClient

fb = FinBrainClient(api_key="YOUR_KEY")

print(fb.available.markets())
print(fb.predictions.ticker("AAPL")["prediction"]["expectedShort"])
```

### Async

```
import asyncio, os
from finbrain.aio import FinBrainAsyncClient async
def  main():
	async  with FinBrainAsyncClient(api_key=os.getenv("FINBRAIN_API_KEY")) as fb:
        data = await fb.sentiments.ticker("sp500", "AMZN")
        print(list(data["sentimentAnalysis"].items())[:3])

asyncio.run(main())` 
```

### CLI

```
export FINBRAIN_API_KEY=your_key
finbrain markets
finbrain predict AAPL --type daily
``` 

----------

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

----------

## 🛠️ Error-handling

```
from finbrain.exceptions import BadRequest
try:
    fb.predictions.ticker("MSFT", prediction_type="weekly")
except BadRequest as exc:
	print("Invalid parameters:", exc)` 
```

| HTTP status | Exception class          | Meaning                               |
|-------------|--------------------------|---------------------------------------|
| 400         | `BadRequest`             | The request is invalid or malformed   |
| 401         | `AuthenticationError`    | API key missing or incorrect          |
| 403         | `PermissionDenied`       | Authenticated, but not authorised     |
| 404         | `NotFound`               | Resource or endpoint not found        |
| 405         | `MethodNotAllowed`       | HTTP method not supported on endpoint |
| 500         | `ServerError`            | FinBrain internal error               |

----------

## 🔄 Versioning & release

-   Semantic Versioning (`MAJOR.MINOR.PATCH`)
    
-   Version auto-generated from Git tags (setuptools-scm)

`git tag -a v0.2.0 -m "Add options.put_call endpoint" git push --tags # GitHub Actions builds & uploads to PyPI` 

----------

## 🧑‍💻 Development



```
git clone https://github.com/finbrain-tech/finbrain-python cd finbrain-python
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]

ruff check . # lint / format pytest -q # unit tests (mocked) 
```

### Live integration test

Set `FINBRAIN_LIVE_KEY`, then run:

```
pytest -m integration
```
----------

## 🤝 Contributing

1.  Fork → create a feature branch
    
2.  Add tests & run `ruff --fix`
    
3.  Ensure `pytest` & CI pass
    
4.  Open a PR — thanks!
    

----------

## 🔒 Security

Please report vulnerabilities to **info@finbrain.tech**.  
We respond within 48 hours.

----------

## 📜 License

MIT — see [LICENSE](LICENSE).

----------

© 2025 FinBrain Technologies — Built with ❤️ for the quant community.