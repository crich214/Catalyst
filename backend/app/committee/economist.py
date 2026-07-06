from app.committee.models import AnalystReview
from app.macro import macro_payload


def economist_review():
    macro = macro_payload()

    regime = macro.get("regime", "Unknown")
    score = int(macro.get("regime_score", 50))

    if score >= 75:
        stance = "Supportive"
        assessment = "Favorable"
        material_concern = False
    elif score >= 55:
        stance = "Neutral"
        assessment = "Balanced"
        material_concern = False
    else:
        stance = "Restrictive"
        assessment = "Restrictive"
        material_concern = True

    positives = []
    concerns = []

    if score >= 75:
        positives.append("Macro regime is supportive of risk assets.")
    elif score >= 55:
        positives.append("Macro backdrop is balanced but not strongly supportive.")

    if score < 55:
        concerns.append("Macro conditions remain restrictive.")

    if "watchful" in regime.lower():
        concerns.append("Market regime requires patience and selectivity.")

    return AnalystReview(
        member="Chief Economist",
        role="Macro and market regime review",
        domain="Macro",
        assessment=assessment,
        stance=stance,
        confidence=max(50, min(95, score)),
        material_concern=material_concern,
        summary=f"Current market regime is {regime} with a macro score of {score}.",
        positives=positives,
        concerns=concerns,
    )