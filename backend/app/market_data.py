from datetime import datetime, timezone
import yfinance as yf

MARKET_SERIES = {
    "ten_year": {
        "symbol": "^TNX",
        "name": "10-Year Treasury",
        "unit": "%",
        "divisor": 1,
    },
    "vix": {
        "symbol": "^VIX",
        "name": "VIX",
        "unit": "Index",
        "divisor": 1,
    },
}


def get_market_quote(key):
    meta = MARKET_SERIES[key]

    ticker = yf.Ticker(meta["symbol"])
    history = ticker.history(period="5d")

    if history.empty:
        raise ValueError(f"No data returned for {meta['symbol']}")

    latest = history.iloc[-1]

    return {
        "value": round(float(latest["Close"]) / meta["divisor"], 3),
        "date": str(history.index[-1].date()),
        "status": "market_live",
        "source": "Yahoo Finance",
        "series_id": meta["symbol"],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "name": meta["name"],
        "unit": meta["unit"],
    }


def get_market_rates():
    results = {}

    for key in MARKET_SERIES:
        try:
            results[key] = get_market_quote(key)
        except Exception as e:
            results[key] = {
                "status": "market_unavailable",
                "error": str(e),
            }

    return results