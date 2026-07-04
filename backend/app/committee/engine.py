from dataclasses import asdict

from app.live_data import get_live_stock
from app.scoring import score_stock
from app.universe import normalize_ticker
from app.decision_engine.engine import company_signal_adjustment

from app.committee.economist import economist_review
from app.committee.business import business_review
from app.committee.risk import risk_review
from app.committee.portfolio import portfolio_review
from app.committee.chairman import chairman_decision


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

    views = [
        economist_review(),
        business_review(scored),
        risk_review(scored),
        portfolio_review(scored),
    ]

    decision = chairman_decision(
        ticker=normalized,
        company=scored.get("company", normalized),
        member_views=views,
    )

    return {
        "decision": asdict(decision),
        "company_profile": scored,
    }