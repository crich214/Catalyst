from dataclasses import asdict

from app.live_data import get_live_stock
from app.scoring import score_stock
from app.universe import normalize_ticker
from app.decision_engine.engine import company_signal_adjustment

from app.committee.economist import economist_review
from app.committee.business import business_review
from app.committee.risk import risk_review
from app.committee.portfolio import portfolio_review
from app.committee.chairman import chairman_review

from app.information.engine import build_information_briefing


def apply_decision_context(scored: dict, ticker: str):
    adjustment = company_signal_adjustment(
        ticker=ticker,
        sector=scored.get("sector", ""),
    )

    base_score = scored.get("rich_alpha_score", 0)
    signal_adjustment = adjustment["signal_adjustment"]
    adjusted_score = max(0, min(100, round(base_score + signal_adjustment, 1)))

    scored["base_rich_alpha_score"] = base_score
    scored["signal_adjustment"] = signal_adjustment
    scored["factor_adjustments"] = adjustment["factor_adjustments"]
    scored["adjusted_rich_alpha_score"] = adjusted_score
    scored["signals_used"] = adjustment["signals_used"]
    scored["rich_alpha_score"] = adjusted_score

    return scored


def run_committee(ticker: str):
    normalized = normalize_ticker(ticker.upper().strip())

    stock = get_live_stock(normalized)
    scored = score_stock(stock)
    scored = apply_decision_context(scored, normalized)

    information_briefing = build_information_briefing(
        normalized,
        scored.get("company", normalized),
    )

    analyst_reviews = [
        economist_review(information_briefing),
        business_review(scored, information_briefing),
        risk_review(scored, information_briefing),
        portfolio_review(scored, information_briefing),
    ]

    decision_engine_recommendation = scored.get("recommendation", "WATCH")
    decision_engine_score = (
        scored.get("adjusted_rich_alpha_score")
        or scored.get("rich_alpha_score")
        or 50
    )

    review = chairman_review(
        ticker=normalized,
        company=scored.get("company", normalized),
        decision_engine_recommendation=decision_engine_recommendation,
        decision_engine_score=decision_engine_score,
        analyst_reviews=analyst_reviews,
    )

    return {
        "decision": asdict(review),
        "company_profile": scored,
        "information_briefing": asdict(information_briefing),
    }