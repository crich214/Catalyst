from app.committee.models import AnalystReview


def business_review(scored: dict):
    score = int(
        scored.get("adjusted_rich_alpha_score")
        or scored.get("rich_alpha_score")
        or 50
    )

    company = scored.get("company", "Company")

    positives = []
    concerns = []

    valuation = scored.get("valuation_score", 0)
    conviction = scored.get("conviction_score", 0)
    execution = scored.get("execution_score", 0)
    risk = scored.get("risk_score", 0)

    if valuation >= 70:
        positives.append(
            "Valuation appears attractive relative to intrinsic value."
        )

    if conviction >= 70:
        positives.append(
            "Business quality and conviction remain strong."
        )

    if execution < 60:
        concerns.append(
            "Execution metrics remain below preferred threshold."
        )

    if risk >= 65:
        concerns.append(
            "Underlying business risk has increased."
        )

    # -------- Committee Assessment --------

    if score >= 80:
        stance = "Supportive"
        assessment = "Excellent"
        material_concern = False

    elif score >= 65:
        stance = "Neutral"
        assessment = "Strong"
        material_concern = False

    else:
        stance = "Cautious"
        assessment = "Weakening"
        material_concern = True

    return AnalystReview(
        member="Business Analyst",
        role="Business quality and competitive position",
        domain="Business",

        assessment=assessment,

        stance=stance,

        confidence=max(50, min(95, score)),

        material_concern=material_concern,

        summary=(
            f"{company} maintains a Business Assessment of "
            f"{assessment} with an adjusted Rich Alpha score of {score}."
        ),

        positives=positives,

        concerns=concerns,
    )