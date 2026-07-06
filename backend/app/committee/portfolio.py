from app.committee.models import AnalystReview


def portfolio_review(scored: dict):
    recommendation = scored.get("recommendation", "WATCH")
    conviction = int(scored.get("conviction_score", 50))

    accumulation = scored.get("accumulation_plan", {})
    max_position = accumulation.get("max_position", "N/A")
    margin = accumulation.get("estimated_margin_of_safety_pct", 0)

    positives = []
    concerns = []

    if margin >= 20:
        positives.append("Margin of safety supports accumulation.")

    elif margin >= 10:
        positives.append("Valuation allows gradual accumulation.")

    else:
        concerns.append("Limited margin of safety.")

    if recommendation in ["BUY", "ACCUMULATE"]:
        stance = "Supportive"

    elif recommendation == "WATCH":
        stance = "Neutral"

    else:
        stance = "Defensive"

    if conviction < 60:
        concerns.append("Overall conviction remains moderate.")

    return AnalystReview(
        member="Portfolio Manager",
        role="Portfolio construction and capital allocation",
        stance=stance,
        confidence=max(50, min(95, conviction)),
        summary=(
            f"Decision Engine recommends {recommendation}. "
            f"Suggested maximum position is {max_position}."
        ),
        positives=positives,
        concerns=concerns,
    )