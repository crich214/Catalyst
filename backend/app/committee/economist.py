from app.committee.models import CommitteeView
from app.macro import macro_payload


def economist_review():
    macro = macro_payload()

    regime = macro.get("regime", "Unknown")
    score = int(macro.get("regime_score", 50))

    if score >= 75:
        stance = "Bullish"
    elif score >= 55:
        stance = "Neutral"
    else:
        stance = "Bearish"

    positives = []
    concerns = []

    if score >= 75:
        positives.append("Macro regime is supportive of risk assets.")
    elif score >= 55:
        positives.append("Macro backdrop is stable.")

    if score < 55:
        concerns.append("Macro conditions remain restrictive.")

    if "higher" in regime.lower():
        concerns.append("Interest rates remain elevated.")

    return CommitteeView(
        member="Chief Economist",
        stance=stance,
        confidence=score,
        score=score,
        summary=f"Current market regime: {regime}",
        positives=positives,
        concerns=concerns,
    )