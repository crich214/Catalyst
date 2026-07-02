from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.live_data import get_live_stock
from app.scoring import score_stock
from app.universe import CORE_UNIVERSE, normalize_ticker
from app.macro import macro_payload
from app.news_events.engine import build_event_report
from app.signals.engine import build_signal_engine
from app.decision_engine.engine import company_signal_adjustment


app = FastAPI(
    title="Catalyst Live Data API",
    version="0.7.0",
    description="Catalyst investment intelligence API."
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
        "version": "0.7.0",
        "live_data": "enabled via yfinance",
        "event_intelligence": "enabled",
        "signal_engine": "enabled",
        "decision_engine": "enabled",
        "core_universe_count": len(CORE_UNIVERSE),
    }


@app.get("/market-regime")
def market_regime():
    return macro_payload()


@app.get("/system-health")
def system_health():
    return {
        "overall_health": 92,
        "feeds": [
            {"name": "Market Data", "status": "Live", "score": 90, "detail": "Yahoo Finance market connector enabled"},
            {"name": "Macro Data", "status": "Live", "score": 85, "detail": "FRED public CSV connector enabled"},
            {"name": "Event Intelligence", "status": "Live", "score": 80, "detail": "Public event feeds enabled"},
            {"name": "Signal Engine", "status": "Live", "score": 75, "detail": "Signals normalized from event intelligence"},
            {"name": "Decision Engine", "status": "Live", "score": 70, "detail": "Signals mapped to company-level adjustments"},
            {"name": "Insider Data", "status": "Placeholder", "score": 35, "detail": "Connector pending"},
            {"name": "Congress Data", "status": "Placeholder", "score": 25, "detail": "Connector pending"},
            {"name": "AI Committee", "status": "Pending", "score": 20, "detail": "Memo engine pending"},
        ],
        "next_priority": "Apply decision engine adjustments directly into opportunity scoring.",
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


@app.get("/signals")
def signals():
    return {
        "signals": build_signal_engine()
    }


@app.get("/decision/{ticker}")
def decision(ticker: str):
    raw = ticker.upper().strip()
    normalized = normalize_ticker(raw)

    try:
        stock = get_live_stock(normalized)
        scored = score_stock(stock)

        adjustment = company_signal_adjustment(
            ticker=normalized,
            sector=scored.get("sector", ""),
        )

        adjusted_score = scored.get("rich_alpha_score", 0) + adjustment["signal_adjustment"]
        adjusted_score = max(0, min(100, round(adjusted_score, 1)))

        return {
            "ticker": normalized,
            "company": scored.get("company"),
            "sector": scored.get("sector"),
            "base_rich_alpha_score": scored.get("rich_alpha_score"),
            "signal_adjustment": adjustment["signal_adjustment"],
            "factor_adjustments": adjustment["factor_adjustments"],
            "adjusted_rich_alpha_score": adjusted_score,
            "signals_used": adjustment["signals_used"],
            "base_recommendation": scored.get("recommendation"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Could not build decision profile for ticker '{raw}': {str(e)}",
        )


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
            "live": len([r for r in valid if r.get("data_status") == "live"]),
            "partial_live": len([r for r in valid if r.get("data_status") == "partial_live"]),
            "fallback": len([r for r in valid if r.get("data_status") == "fallback"]),
        },
    }