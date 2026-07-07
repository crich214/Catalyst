def determine_materiality(title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()

    company_specific_high = [
        "merger",
        "acquisition",
        "strategic review",
        "explores sale",
        "sale of",
        "sell its",
        "spinoff",
        "spin-off",
        "bankruptcy",
        "investigation",
        "lawsuit",
        "guidance",
        "earnings miss",
        "ceo resigns",
        "cfo resigns",
    ]

    company_specific_medium = [
        "partnership",
        "contract",
        "launch",
        "expansion",
        "upgrade",
        "downgrade",
        "analyst",
    ]

    low_signal = [
        "sector update",
        "market update",
        "stocks edge",
        "stocks mixed",
        "midday stories",
        "morning brief",
    ]

    if any(word in text for word in low_signal):
        return "Low"

    if any(word in text for word in company_specific_high):
        return "High"

    if any(word in text for word in company_specific_medium):
        return "Medium"

    return "Low"


def determine_direction(title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()

    bullish = [
        "beats",
        "beat",
        "raises",
        "growth",
        "upgrade",
        "partnership",
        "contract",
        "acquisition",
        "rises",
    ]

    bearish = [
        "miss",
        "misses",
        "downgrade",
        "lawsuit",
        "investigation",
        "cuts",
        "weak",
        "bankruptcy",
        "falls",
    ]

    if any(word in text for word in bullish):
        return "Bullish"

    if any(word in text for word in bearish):
        return "Bearish"

    return "Neutral"