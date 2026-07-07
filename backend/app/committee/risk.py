from app.committee.models import AnalystReview


def risk_review(scored: dict):
    factor_adjustments = scored.get("factor_adjustments", {})
    signals_used = scored.get("signals_used", [])

    execution_risk = factor_adjustments.get("execution_risk", 0)
    regulatory_risk = factor_adjustments.get("regulatory_risk", 0)
    risk_score = int(scored.get("risk_score", 50))

    negative_signal_count = len([
        signal for signal in signals_used
        if signal.get("weighted_factor_adjustment", 0) < 0
    ])

    combined_risk = (
        risk_score
        + abs(execution_risk)
        + abs(regulatory_risk)
        + negative_signal_count
    )

    if combined_risk >= 75:
        stance = "Cautious"
        assessment = "Elevated risk profile"
        material_concern = True
    elif combined_risk >= 55:
        stance = "Neutral"
        assessment = "Moderate risk profile"
        material_concern = False
    else:
        stance = "Constructive"
        assessment = "Manageable risk profile"
        material_concern = False

    positives = []
    concerns = []

    if risk_score < 55:
        positives.append("Base risk score appears manageable.")

    if not signals_used:
        positives.append("No active event signals currently affect the company.")

    if execution_risk >= 0:
        positives.append("No material negative execution-risk adjustment was identified.")

    if regulatory_risk >= 0:
        positives.append("No material negative regulatory-risk adjustment was identified.")

    if execution_risk < 0:
        concerns.append("Execution risk signals are negatively affecting the recommendation.")

    if regulatory_risk < 0:
        concerns.append("Regulatory risk signals are negatively affecting the recommendation.")

    if negative_signal_count > 0:
        concerns.append(f"{negative_signal_count} active negative signal(s) require monitoring.")

    if not concerns:
        concerns.append("No material risk concerns identified by the Risk Officer.")

    confidence = 80

    if combined_risk >= 75:
        confidence = 85
    elif combined_risk >= 55:
        confidence = 75

    return AnalystReview(
        member="Risk Officer",
        role="Event, signal, regulatory, and execution risk review",
        domain="Risk",
        assessment=assessment,
        stance=stance,
        confidence=confidence,
        material_concern=material_concern,
        summary=(
            f"Risk review considered a base risk score of {risk_score}, "
            f"execution risk adjustment of {execution_risk}, regulatory risk adjustment "
            f"of {regulatory_risk}, and {negative_signal_count} negative active signal(s)."
        ),
        positives=positives,
        concerns=concerns,
    )