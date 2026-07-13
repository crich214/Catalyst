from typing import List

from app.information.domain_router import determine_domains
from app.information.models import InformationItem
from app.macro import macro_payload


def get_macro_news() -> List[InformationItem]:
    """
    Build macroeconomic investment events from Catalyst's live Macro Engine.
    """

    items: List[InformationItem] = []

    try:
        macro = macro_payload()
    except Exception:
        return items

    regime = macro.get("regime", "Unknown")
    score = macro.get("regime_score", 50)
    risk_level = macro.get("risk_level", "Moderate")

    favored = macro.get("favored_themes", [])
    cautious = macro.get("cautious_themes", [])

    items.append(
        InformationItem(
            title=f"Market Regime: {regime}",
            source="Catalyst Macro Engine",
            category="Macro",
            ticker=None,
            summary=(
                f"Current market regime is {regime} with a regime score "
                f"of {score} and an overall risk level of {risk_level}."
            ),
            materiality="High",
            direction="Neutral",
            confidence=95,
            affected_domains=determine_domains("Macro"),
            url=None,
            event_type="Macro",
        )
    )

    if favored:
        items.append(
            InformationItem(
                title="Favored Investment Themes",
                source="Catalyst Macro Engine",
                category="Macro",
                ticker=None,
                summary="Current favored themes: " + ", ".join(favored) + ".",
                materiality="Medium",
                direction="Bullish",
                confidence=90,
                affected_domains=determine_domains("Macro"),
                url=None,
                event_type="Macro",
            )
        )

    if cautious:
        items.append(
            InformationItem(
                title="Areas Requiring Caution",
                source="Catalyst Macro Engine",
                category="Macro",
                ticker=None,
                summary="Current cautious themes: " + ", ".join(cautious) + ".",
                materiality="Medium",
                direction="Bearish",
                confidence=90,
                affected_domains=determine_domains("Macro"),
                url=None,
                event_type="Macro",
            )
        )

    return items