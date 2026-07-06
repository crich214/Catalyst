from app.committee.models import AnalystReview


def risk_review(scored: dict):
    factor_adjustments = scored.get("factor_adjustments", {})
    signals_used = scored.get("signals_used", [])

    execution_risk = factor_adjustments.get("execution_risk", 0)
    regulatory_risk = factor_adjustments.get("regulatory_risk", 0)
    risk_score = int(scored.get("risk_score", 50))

    negative_signal_count = len([
        s for s in signals_used
        if s.get("weighted_factor_adjustment", 0) < 0
    ])

    combined_risk = risk_score + abs(execution_risk) + abs(regulatory_risk) + negative_signal_count

    if combined_risk >= 75:
        stance = "Cautious"
    elif combined_risk >= 55:
        stance = "Neutral"
    else:
        stance = "Constructive"

    positives = []
    concerns = []

    if risk_score < 55:
        positives.append("Base risk score is manageable.")

    if not signals_used:
        positives.append("No active event signals currently affect the company.")

    if execution_risk < 0:
        concerns.append("Execution risk signals are negative.")

    if regulatory_risk < 0:
        concerns.append("Regulatory risk signals are negative.")

    if negative_signal_count > 0:
        concerns.append(f"{negative_signal_count} active negative signal(s) require monitoring.")

    return AnalystReview(
        member="Risk Officer",
        role="Event, signal, regulatory, and execution risk review",
        stance=stance,
        confidence=max(50, min(95, combined_risk)),
        summary=f"Risk review considered base risk score of {risk_score} and active signal factors.",
        positives=positives,
        concerns=concerns,
    )