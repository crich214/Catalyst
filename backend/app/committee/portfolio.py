from app.committee.models import CommitteeView


def portfolio_review(scored: dict):
    margin_of_safety = scored.get("accumulation_plan", {}).get("estimated_margin_of_safety_pct", 0) or 0
    max_position = scored.get("accumulation_plan", {}).get("max_position", "N/A")
    recommendation = scored.get("recommendation", "WATCH")

    if margin_of_safety >= 25:
        stance = "Bullish"
        score = 85
    elif margin_of_safety >= 15:
        stance = "Neutral"
        score = 70
    else:
        stance = "Cautious"
        score = 55

    positives = []
    concerns = []

    if margin_of_safety >= 15:
        positives.append("Margin of safety is acceptable for gradual accumulation.")

    if margin_of_safety < 15:
        concerns.append("Margin of safety is limited at the current price.")

    return CommitteeView(
        member="Portfolio Manager",
        stance=stance,
        confidence=score,
        score=score,
        summary=f"Portfolio view: {recommendation}. Suggested max position: {max_position}.",
        positives=positives,
        concerns=concerns,
    )