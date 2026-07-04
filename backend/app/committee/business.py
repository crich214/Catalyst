from app.committee.models import CommitteeView


def business_review(scored: dict):
    score = int(scored.get("base_rich_alpha_score") or scored.get("rich_alpha_score") or 50)
    company = scored.get("company", "Company")

    if score >= 80:
        stance = "Bullish"
    elif score >= 65:
        stance = "Neutral"
    else:
        stance = "Cautious"

    positives = []
    concerns = []

    if scored.get("valuation_score", 0) >= 70:
        positives.append("Valuation appears attractive relative to Catalyst estimates.")

    if scored.get("conviction_score", 0) >= 70:
        positives.append("Conviction score supports the thesis.")

    if scored.get("execution_score", 0) < 60:
        concerns.append("Execution score is below preferred threshold.")

    if scored.get("risk_score", 0) >= 65:
        concerns.append("Risk score is elevated.")

    return CommitteeView(
        member="Business Analyst",
        stance=stance,
        confidence=score,
        score=score,
        summary=f"{company} has a base business score of {score}.",
        positives=positives,
        concerns=concerns,
    )