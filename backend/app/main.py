from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.committee.engine import run_committee
from app.decision_engine.engine import company_signal_adjustment
from app.information.engine import build_information_briefing
from app.journal.engine import latest_decisions, record_decision
from app.live_data import get_live_stock
from app.macro import macro_payload
from app.news_events.engine import build_event_report
from app.performance.engine import build_performance_report
from app.portfolio.engine import (
    PILOT_CAPITAL,
    build_pilot_portfolio,
    load_pilot_portfolio,
)
from app.scoring import recommendation_from_metrics, score_stock
from app.signals.engine import build_signal_engine
from app.universe import CORE_UNIVERSE, normalize_ticker


app = FastAPI(
    title="Catalyst Live Data API",
    version="1.0.0",
    description="Catalyst investment intelligence API.",
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
        "version": "1.0.0",
        "live_data": "enabled via yfinance",
        "event_intelligence": "enabled",
        "signal_engine": "enabled",
        "decision_engine": "enabled",
        "ai_committee": "enabled",
        "information_engine": "enabled",
        "portfolio_engine": "enabled",
        "decision_journal": "enabled",
        "performance_engine": "enabled",
        "core_universe_count": len(CORE_UNIVERSE),
    }


@app.get("/market-regime")
def market_regime():
    return macro_payload()


@app.get("/system-health")
def system_health():
    return {
        "overall_health": 99,
        "feeds": [
            {
                "name": "Market Data",
                "status": "Live",
                "score": 90,
                "detail": "Yahoo Finance market connector enabled",
            },
            {
                "name": "Macro Data",
                "status": "Live",
                "score": 85,
                "detail": "FRED public CSV connector enabled",
            },
            {
                "name": "Event Intelligence",
                "status": "Live",
                "score": 80,
                "detail": "Public event feeds enabled",
            },
            {
                "name": "Signal Engine",
                "status": "Live",
                "score": 80,
                "detail": "Signals normalized from event intelligence",
            },
            {
                "name": "Decision Engine",
                "status": "Live",
                "score": 85,
                "detail": "Signals mapped to adjusted recommendations",
            },
            {
                "name": "AI Committee",
                "status": "Live",
                "score": 75,
                "detail": "Investment committee review enabled",
            },
            {
                "name": "Information Engine",
                "status": "Live",
                "score": 75,
                "detail": "Structured investment events enabled",
            },
            {
                "name": "Portfolio Engine",
                "status": "Live",
                "score": 80,
                "detail": "Persistent pilot portfolio enabled",
            },
            {
                "name": "Decision Journal",
                "status": "Live",
                "score": 80,
                "detail": "Investment decisions persisted locally",
            },
            {
                "name": "Performance Engine",
                "status": "Live",
                "score": 80,
                "detail": "Pilot performance and benchmark tracking enabled",
            },
        ],
        "next_priority": "Complete dashboard integration and begin pilot testing.",
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
        "events": build_event_report(),
    }


@app.get("/signals")
def signals():
    return {
        "signals": build_signal_engine(),
    }


@app.get("/information/{ticker}")
def information_briefing(ticker: str):
    raw = ticker.upper().strip()
    normalized = normalize_ticker(raw)

    try:
        stock = get_live_stock(normalized)
        company = stock.get("company", normalized)

        briefing = build_information_briefing(
            normalized,
            company,
        )

        return asdict(briefing)

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Could not build information briefing for ticker "
                f"'{raw}': {str(exc)}"
            ),
        )


def apply_decision_engine(
    scored: dict,
    ticker: str,
) -> dict:
    adjustment = company_signal_adjustment(
        ticker=ticker,
        sector=scored.get("sector", ""),
    )

    base_score = float(
        scored.get("rich_alpha_score", 0)
    )

    signal_adjustment = float(
        adjustment.get("signal_adjustment", 0)
    )

    adjusted_score = max(
        0,
        min(
            100,
            round(
                base_score + signal_adjustment,
                1,
            ),
        ),
    )

    scored["base_rich_alpha_score"] = base_score
    scored["signal_adjustment"] = signal_adjustment

    scored["factor_adjustments"] = adjustment.get(
        "factor_adjustments",
        {},
    )

    scored["adjusted_rich_alpha_score"] = adjusted_score

    scored["signals_used"] = adjustment.get(
        "signals_used",
        [],
    )

    scored["rich_alpha_score"] = adjusted_score

    scored["recommendation"] = recommendation_from_metrics(
        category=scored.get("category", ""),
        risk=float(
            scored.get("risk_score", 50)
        ),
        rich_alpha=adjusted_score,
        conviction=float(
            scored.get("conviction_score", 0)
        ),
    )

    return scored


def build_live_opportunity_results() -> list[dict]:
    results = []

    for ticker in CORE_UNIVERSE:
        try:
            stock = get_live_stock(ticker)

            scored = score_stock(stock)

            scored = apply_decision_engine(
                scored,
                ticker,
            )

            results.append(scored)

        except Exception as exc:
            results.append(
                {
                    "ticker": ticker,
                    "error": str(exc),
                    "data_status": "unavailable",
                }
            )

    return results


def valid_opportunities(
    results: list[dict],
) -> list[dict]:
    valid = [
        result
        for result in results
        if "rich_alpha_score" in result
    ]

    valid.sort(
        key=lambda item: item.get(
            "adjusted_rich_alpha_score",
            item.get("rich_alpha_score", 0),
        ),
        reverse=True,
    )

    return valid


@app.get("/decision/{ticker}")
def decision(ticker: str):
    raw = ticker.upper().strip()
    normalized = normalize_ticker(raw)

    try:
        stock = get_live_stock(normalized)

        scored = score_stock(stock)

        return apply_decision_engine(
            scored,
            normalized,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Could not build decision profile for ticker "
                f"'{raw}': {str(exc)}"
            ),
        )


@app.get("/committee/{ticker}")
def committee(ticker: str):
    raw = ticker.upper().strip()

    try:
        return run_committee(raw)

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Could not run committee review for ticker "
                f"'{raw}': {str(exc)}"
            ),
        )


@app.get("/live/{ticker}")
def live_ticker(ticker: str):
    raw = ticker.upper().strip()
    normalized = normalize_ticker(raw)

    if raw == "APPL":
        raise HTTPException(
            status_code=400,
            detail=(
                "Ticker not found. "
                "Did you mean AAPL for Apple?"
            ),
        )

    try:
        stock = get_live_stock(normalized)

        result = score_stock(stock)

        result = apply_decision_engine(
            result,
            normalized,
        )

        if raw != normalized:
            result["alias_used"] = raw
            result["normalized_ticker"] = normalized

        return result

    except Exception:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Could not load live data for ticker "
                f"'{raw}'. Check the symbol and try again."
            ),
        )


@app.get("/opportunities/live")
def live_opportunities():
    results = build_live_opportunity_results()
    valid = valid_opportunities(results)

    invalid = [
        result
        for result in results
        if "rich_alpha_score" not in result
    ]

    recommendation_counts = {}

    for item in valid:
        recommendation = item.get(
            "recommendation",
            "UNKNOWN",
        )

        recommendation_counts[recommendation] = (
            recommendation_counts.get(
                recommendation,
                0,
            )
            + 1
        )

    actionable = [
        item
        for item in valid
        if item.get("recommendation")
        in {
            "BUY",
            "ACCUMULATE",
            "SPECULATIVE STARTER",
        }
    ]

    return {
        "ranked_opportunities": valid,
        "actionable_opportunities": actionable,
        "errors": invalid,
        "summary": {
            "total": len(results),
            "valid": len(valid),
            "errors": len(invalid),
            "live": len(
                [
                    item
                    for item in valid
                    if item.get("data_status") == "live"
                ]
            ),
            "partial_live": len(
                [
                    item
                    for item in valid
                    if item.get("data_status")
                    == "partial_live"
                ]
            ),
            "fallback": len(
                [
                    item
                    for item in valid
                    if item.get("data_status")
                    == "fallback"
                ]
            ),
            "actionable": len(actionable),
            "recommendation_counts": recommendation_counts,
        },
    }


@app.get("/portfolio/pilot")
def pilot_portfolio():
    saved_portfolio = load_pilot_portfolio()

    if saved_portfolio:
        return saved_portfolio

    results = build_live_opportunity_results()
    valid = valid_opportunities(results)

    return build_pilot_portfolio(
        opportunities=valid,
        capital=PILOT_CAPITAL,
    )


@app.get("/performance/pilot")
def pilot_performance():
    portfolio = load_pilot_portfolio()

    if not portfolio:
        results = build_live_opportunity_results()
        valid = valid_opportunities(results)

        portfolio = build_pilot_portfolio(
            opportunities=valid,
            capital=PILOT_CAPITAL,
        )

    return build_performance_report(portfolio)


@app.get("/journal")
def journal(limit: int = 50):
    entries = latest_decisions(
        limit=max(1, min(limit, 500))
    )

    return {
        "entries": entries,
        "count": len(entries),
    }


@app.post("/journal/{ticker}")
def journal_ticker(ticker: str):
    raw = ticker.upper().strip()
    normalized = normalize_ticker(raw)

    try:
        committee_result = run_committee(normalized)

        decision_data = committee_result.get(
            "decision",
            {},
        )

        profile = committee_result.get(
            "company_profile",
            {},
        )

        reasons = []

        for review in decision_data.get(
            "analyst_reviews",
            [],
        ):
            reasons.extend(
                review.get("positives", [])
            )

            reasons.extend(
                review.get("concerns", [])
            )

        entry = record_decision(
            ticker=normalized,
            company=profile.get(
                "company",
                normalized,
            ),
            recommendation=decision_data.get(
                "final_recommendation",
                profile.get(
                    "recommendation",
                    "WATCH",
                ),
            ),
            rich_alpha_score=float(
                profile.get(
                    "adjusted_rich_alpha_score"
                )
                or profile.get(
                    "rich_alpha_score"
                )
                or 0
            ),
            conviction_score=float(
                profile.get(
                    "conviction_score",
                    0,
                )
            ),
            risk_score=float(
                profile.get(
                    "risk_score",
                    50,
                )
            ),
            price=float(
                profile.get(
                    "price",
                    0,
                )
            ),
            committee_action=decision_data.get(
                "committee_action",
                "",
            ),
            chairman_summary=decision_data.get(
                "chairman_summary",
                "",
            ),
            reasons=reasons,
        )

        return {
            "status": "recorded",
            "entry": entry,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Could not record decision for ticker "
                f"'{raw}': {str(exc)}"
            ),
        )