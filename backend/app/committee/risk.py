from app.committee.models import CommitteeView


def risk_review(scored: dict):
    factor_adjustments = scored.get("factor_adjustments", {})
    signals_used = scored.get("signals_used", [])

    execution_risk = factor_adjustments.get("execution_risk", 0)
    regulatory_risk = factor_adjustments.get("regulatory_risk", 0)
    risk_score = int(scored.get("risk_score", 50))

    combined_risk = risk_score + abs(execution_risk) + abs(regulatory_risk)

    if combined_risk >= 75:
        stance = "Cautious"
    elif combined_risk >= 55:
        stance = "Neutral"
    else:
        stance = "Constructive"

    concerns = []
    positives = []

    if execution_risk < 0:
        concerns.append("Execution risk signals are negative.")

    if regulatory_risk < 0:
        concerns.append("Regulatory risk signals are negative.")

    if not signals_used:
        positives.append("No active event signals currently affect the company.")

    if risk_score < 55:
        positives.append("Base risk score is manageable.")

    return CommitteeView(
        member="Risk Officer",
        stance=stance,
        confidence=min(95, max(50, combined_risk)),
        score=max(0, min(100, 100 - combined_risk)),
        summary=f"Risk review considered base risk score of {risk_score} and active signal factors.",
        positives=positives,
        concerns=concerns,
    )