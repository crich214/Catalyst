from collections import defaultdict

from app.signals.engine import build_signal_engine


MAX_TOTAL_ADJUSTMENT = 6
MAX_SOURCE_ADJUSTMENT = 3


FACTOR_WEIGHTS = {
    "regulatory_risk": 0.30,
    "financing_conditions": 0.25,
    "demand_outlook": 0.20,
    "execution_risk": 0.25,
}


def clamp(value, low, high):
    return max(low, min(high, value))


def classify_signal_factor(signal):
    title = signal.get("title", "").lower()
    summary = signal.get("summary", "").lower()
    text = f"{title} {summary}"

    if any(word in text for word in ["sec", "cftc", "regulatory", "rule", "enforcement", "fraud", "charges"]):
        return "regulatory_risk"

    if any(word in text for word in ["rate", "fed", "inflation", "fomc", "treasury", "yield"]):
        return "financing_conditions"

    if any(word in text for word in ["ipo", "market statistics", "demand", "growth", "innovation", "etf"]):
        return "demand_outlook"

    if any(word in text for word in ["earthquake", "hurricane", "storm", "supply chain", "pipeline", "refinery"]):
        return "execution_risk"

    return "execution_risk"


def raw_factor_impact(signal, ticker: str, sector: str):
    affected_companies = signal.get("affected_companies", [])
    affected_sectors = signal.get("affected_sectors", [])
    direction = signal.get("direction", "neutral")
    score = signal.get("weighted_score", 0)
    title = signal.get("title", "").lower()

    company_match = ticker in affected_companies
    sector_match = sector in affected_sectors if sector else False

    if not company_match and not sector_match:
        return None

    factor = classify_signal_factor(signal)

    if direction == "neutral":
        raw = 0
        reason = "Neutral signal; no factor change."
    elif direction == "bullish":
        raw = 3 if company_match else 1
        reason = "Bullish signal matched company/sector."
    elif direction == "bearish":
        raw = -3 if company_match else -1
        reason = "Bearish signal matched company/sector."
    elif direction == "mixed":
        raw = 1 if company_match else 0
        reason = "Mixed signal; only company-specific matches receive a small adjustment."
    else:
        raw = 0
        reason = "Unknown signal direction."

    if "public comment" in title or "seeks public comment" in title:
        raw = int(raw / 2)
        reason += " Reduced because this is a public comment/request, not a final rule."

    if score >= 80:
        raw *= 2
        reason += " Increased because signal weight is high."
    elif score < 55:
        raw = int(raw / 2)
        reason += " Reduced because signal weight is low."

    weighted = round(raw * FACTOR_WEIGHTS.get(factor, 0.2), 2)

    return {
        "factor": factor,
        "raw": raw,
        "weighted": weighted,
        "company_match": company_match,
        "sector_match": sector_match,
        "reason": reason,
    }


def company_signal_adjustment(ticker: str, sector: str = ""):
    ticker = ticker.upper().strip()
    sector = (sector or "").strip()

    signals = build_signal_engine()

    factor_adjustments = {
        "regulatory_risk": 0,
        "financing_conditions": 0,
        "demand_outlook": 0,
        "execution_risk": 0,
    }

    explanations = []
    source_totals = defaultdict(float)

    for signal in signals:
        impact = raw_factor_impact(signal, ticker, sector)

        if impact is None:
            continue

        source = signal.get("source", "Unknown")
        proposed_source_total = source_totals[source] + impact["weighted"]

        capped_source_total = clamp(
            proposed_source_total,
            -MAX_SOURCE_ADJUSTMENT,
            MAX_SOURCE_ADJUSTMENT,
        )

        final_weighted = capped_source_total - source_totals[source]
        source_totals[source] = capped_source_total

        factor = impact["factor"]
        factor_adjustments[factor] += final_weighted

        explanations.append({
            "title": signal.get("title"),
            "source": source,
            "direction": signal.get("direction"),
            "weighted_score": signal.get("weighted_score"),
            "factor": factor,
            "company_match": impact["company_match"],
            "sector_match": impact["sector_match"],
            "raw_adjustment": impact["raw"],
            "weighted_factor_adjustment": final_weighted,
            "reason": impact["reason"],
            "summary": signal.get("summary"),
        })

    total_adjustment = round(sum(factor_adjustments.values()), 2)
    total_adjustment = clamp(total_adjustment, -MAX_TOTAL_ADJUSTMENT, MAX_TOTAL_ADJUSTMENT)

    return {
        "ticker": ticker,
        "sector": sector,
        "signal_adjustment": total_adjustment,
        "factor_adjustments": factor_adjustments,
        "max_total_adjustment": MAX_TOTAL_ADJUSTMENT,
        "max_source_adjustment": MAX_SOURCE_ADJUSTMENT,
        "signals_used": explanations,
    }