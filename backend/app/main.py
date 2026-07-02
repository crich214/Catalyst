from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.live_data import get_live_stock
from app.scoring import score_stock
from app.universe import CORE_UNIVERSE, normalize_ticker
from app.macro import macro_payload
from app.news_events.engine import build_event_report

app = FastAPI(
    title="Catalyst Live Data API",
    version="0.6.0",
    description="Catalyst Step 6: FRED macro engine + decision dashboard."
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.6.0",
        "live_data": "enabled via yfinance",
        "data_integrity": "enabled",
        "core_universe_count": len(CORE_UNIVERSE),
    }


@app.get("/market-regime")
def market_regime():
    return macro_payload()


@app.get("/system-health")
def system_health():
    return {
        "overall_health": 88,
        "feeds": [
            {
                "name": "Market Data",
                "status": "Live",
                "score": 90,
                "detail": "yfinance connector enabled",
            },
            {
                "name": "Ticker Alias Map",
                "status": "Live",
                "score": 100,
                "detail": "Alias normalization enabled",
            },
            {
                "name": "Fallback Profiles",
                "status": "Live",
                "score": 85,
                "detail": "Fallback layer enabled for core names",
            },
            {
                "name": "Insider Data",
                "status": "Placeholder",
                "score": 35,
                "detail": "FMP/OpenInsider connector pending",
            },
            {
                "name": "Congress Data",
                "status": "Placeholder",
                "score": 25,
                "detail": "Quiver/FMP connector pending",
            },
            {
                "name": "Macro Data",
                "status": "Live",
                "score": 85,
                "detail": "FRED public CSV connector enabled",
            },
            {
                "name": "AI Committee",
                "status": "Pending",
                "score": 20,
                "detail": "OpenAI memo engine pending",
            },
        ],
        "next_priority": "Connect insider and congressional trading data; macro data is now powered by FRED when available.",
    }


@app.get("/universe")
def universe():
    return {
        "count": len(CORE_UNIVERSE),
        "tickers": CORE_UNIVERSE,
    }


@app.get("/events")
def events():
    return {
        "events": build_event_report()
    }


@app.get("/live/{ticker}")
def live_ticker(ticker: str):
    raw = ticker.upper().strip()
    normalized = normalize_ticker(raw)

    if raw == "APPL":
        raise HTTPException(
            status_code=400,
            detail="Ticker not found. Did you mean AAPL for Apple?",
        )

    try:
        stock = get_live_stock(normalized)
        result = score_stock(stock)

        if raw != normalized:
            result["alias_used"] = raw
            result["normalized_ticker"] = normalized

        return result

    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Could not load live data for ticker '{raw}'. Check the symbol and try again.",
        )


@app.get("/opportunities/live")
def live_opportunities():
    results = []

    for ticker in CORE_UNIVERSE:
        try:
            stock = get_live_stock(ticker)
            results.append(score_stock(stock))
        except Exception as e:
            results.append(
                {
                    "ticker": ticker,
                    "error": str(e),
                    "data_status": "unavailable",
                }
            )

    valid = [r for r in results if "rich_alpha_score" in r]
    invalid = [r for r in results if "rich_alpha_score" not in r]

    valid.sort(key=lambda x: x["rich_alpha_score"], reverse=True)

    return {
        "ranked_opportunities": valid,
        "errors": invalid,
        "summary": {
            "total": len(results),
            "valid": len(valid),
            "errors": len(invalid),
            "live": len(
                [r for r in valid if r.get("data_status") == "live"]
            ),
            "partial_live": len(
                [r for r in valid if r.get("data_status") == "partial_live"]
            ),
            "fallback": len(
                [r for r in valid if r.get("data_status") == "fallback"]
            ),
        },
    }