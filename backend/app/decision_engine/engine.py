from collections import defaultdict

from app.signals.engine import build_signal_engine


MAX_TOTAL_ADJUSTMENT = 6
MAX_SOURCE_ADJUSTMENT = 3


def clamp(value, low, high):
    return max(low, min(high, value))


def raw_signal_impact(signal, ticker: str, sector: str):
    affected_companies = signal.get("affected_companies", [])
    affected_sectors = signal.get("affected_sectors", [])
    direction = signal.get("direction", "neutral")
    score = signal.get("weighted_score", 0)
    title = signal.get("title", "").lower()

    company_match = ticker in affected_companies
    sector_match = sector in affected_sectors if sector else False

    if not company_match and not sector_match:
        return 0, company_match, sector_match, "No company or sector match."

    if direction == "neutral":
        return 0, company_match, sector_match, "Neutral signal."

    if direction == "bullish":
        impact = 3 if company_match else 1
    elif direction == "bearish":
        impact = -3 if company_match else -1
    elif direction == "mixed":
        impact = 1 if company_match else 0
    else:
        impact = 0

    if "public comment" in title or "seeks public comment" in title:
        impact = int(impact / 2)
        reason = "Reduced impact because this is only a public comment/request, not a final rule."
    else:
        reason = "Applied standard company/sector signal impact."

    if score >= 80:
        impact *= 2
        reason += " High-weight signal."
    elif score < 55:
        impact = int(impact / 2)
        reason += " Low-weight signal."

    return impact, company_match, sector_match, reason


def company_signal_adjustment(ticker: str, sector: str = ""):
    ticker = ticker.upper().strip()
    sector = (sector or "").strip()

    signals = build_signal_engine()
    adjustments = []
    source_totals = defaultdict(int)

    total_adjustment = 0

    for signal in signals:
        impact, company_match, sector_match, reason = raw_signal_impact(signal, ticker, sector)

        if impact == 0 and not company_match and not sector_match:
            continue

        source = signal.get("source", "Unknown")
        proposed_source_total = source_totals[source] + impact
        capped_source_total = clamp(
            proposed_source_total,
            -MAX_SOURCE_ADJUSTMENT,
            MAX_SOURCE_ADJUSTMENT,
        )

        source_capped_impact = capped_source_total - source_totals[source]
        source_totals[source] = capped_source_total

        proposed_total = total_adjustment + source_capped_impact
        capped_total = clamp(
            proposed_total,
            -MAX_TOTAL_ADJUSTMENT,
            MAX_TOTAL_ADJUSTMENT,
        )

        final_impact = capped_total - total_adjustment
        total_adjustment = capped_total

        adjustments.append({
            "title": signal.get("title"),
            "source": source,
            "direction": signal.get("direction"),
            "weighted_score": signal.get("weighted_score"),
            "company_match": company_match,
            "sector_match": sector_match,
            "raw_adjustment": impact,
            "final_adjustment": final_impact,
            "reason": reason,
            "summary": signal.get("summary"),
        })

        if abs(total_adjustment) >= MAX_TOTAL_ADJUSTMENT:
            break

    return {
        "ticker": ticker,
        "sector": sector,
        "signal_adjustment": total_adjustment,
        "max_total_adjustment": MAX_TOTAL_ADJUSTMENT,
        "max_source_adjustment": MAX_SOURCE_ADJUSTMENT,
        "signals_used": adjustments,
    }