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
        positives.append("Valuation supports gradual accumulation.")
    else:
        concerns.append("Limited margin of safety reduces allocation appeal.")

    if recommendation in ["BUY", "ACCUMULATE"]:
        stance = "Supportive"
        assessment = "Capital allocation supported"
    elif recommendation == "WATCH":
        stance = "Neutral"
        assessment = "Watchlist position preferred"
    else:
        stance = "Defensive"
        assessment = "Capital preservation preferred"

    if conviction >= 75:
        positives.append("Decision Engine conviction supports portfolio consideration.")
    elif conviction < 60:
        concerns.append("Overall conviction remains moderate.")

    if max_position not in [None, "N/A", ""]:
        positives.append(f"Suggested maximum position size is {max_position}.")
    else:
        concerns.append("No clear maximum position size was provided.")

    material_concern = (
        margin < 10
        or conviction < 60
        or recommendation in ["SELL", "AVOID"]
    )

    if not concerns:
        concerns.append("No material portfolio-construction concerns identified.")

    return AnalystReview(
        member="Portfolio Manager",
        role="Portfolio construction and capital allocation",
        domain="Portfolio",
        assessment=assessment,
        stance=stance,
        confidence=max(50, min(95, conviction)),
        material_concern=material_concern,
        summary=(
            f"Portfolio review considered the Decision Engine recommendation of "
            f"{recommendation}, conviction score of {conviction}, estimated margin "
            f"of safety of {margin}%, and suggested maximum position of {max_position}."
        ),
        positives=positives,
        concerns=concerns,
    )