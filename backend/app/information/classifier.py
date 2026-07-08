def determine_event_type(title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()

    strategic_transaction = [
        "strategic review",
        "explores sale",
        "exploring sale",
        "sale of",
        "sell its",
        "banks are circling",
        "circling",
        "buyer",
        "buyers",
        "acquire",
        "acquiring",
        "acquisition",
        "takeover",
        "merger",
        "divestiture",
        "asset sale",
        "auction",
        "star network",
        "star debit",
        "debit network",
        "payment processing network",
        "card network",
    ]

    earnings = [
        "earnings",
        "guidance",
        "revenue",
        "eps",
        "profit",
        "margin",
        "quarterly results",
        "full-year outlook",
    ]

    regulatory_risk = [
        "sec",
        "investigation",
        "lawsuit",
        "regulation",
        "regulatory",
        "antitrust",
        "probe",
        "settlement",
    ]

    macro = [
        "fed",
        "federal reserve",
        "inflation",
        "interest rate",
        "jobs report",
        "unemployment",
        "cpi",
        "ppi",
        "treasury yields",
    ]

    geopolitical = [
        "war",
        "sanctions",
        "tariff",
        "geopolitical",
        "trade restriction",
        "export controls",
        "military conflict",
    ]

    if any(word in text for word in strategic_transaction):
        return "StrategicTransaction"

    if any(word in text for word in earnings):
        return "Earnings"

    if any(word in text for word in regulatory_risk):
        return "RegulatoryRisk"

    if any(word in text for word in macro):
        return "Macro"

    if any(word in text for word in geopolitical):
        return "Geopolitical"

    return "General"


def determine_materiality(title: str, summary: str) -> str:
    event_type = determine_event_type(title, summary)

    if event_type in [
        "StrategicTransaction",
        "Earnings",
        "RegulatoryRisk",
        "Macro",
        "Geopolitical",
    ]:
        return "High"

    text = f"{title} {summary}".lower()

    if any(word in text for word in [
        "partnership",
        "contract",
        "launch",
        "expansion",
        "upgrade",
        "downgrade",
        "analyst",
    ]):
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
        "rose",
        "higher",
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
        "fell",
        "lower",
    ]

    if any(word in text for word in bullish):
        return "Bullish"

    if any(word in text for word in bearish):
        return "Bearish"

    return "Neutral"