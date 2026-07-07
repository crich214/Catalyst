def determine_domains(title: str, summary: str):
    text = f"{title} {summary}".lower()

    domains = []

    business = [
        "merger",
        "acquisition",
        "sale",
        "sell",
        "strategic review",
        "debit network",
        "product",
        "launch",
        "contract",
    ]

    risk = [
        "lawsuit",
        "investigation",
        "regulation",
        "sec",
        "cyber",
        "hack",
        "sale",
        "debit network",
    ]

    portfolio = [
        "guidance",
        "earnings",
        "valuation",
        "buyback",
        "dividend",
        "sale",
        "debit network",
    ]

    macro = [
        "fed",
        "inflation",
        "interest rate",
        "tariff",
        "geopolitical",
        "war",
    ]

    if any(word in text for word in business):
        domains.append("Business")

    if any(word in text for word in risk):
        domains.append("Risk")

    if any(word in text for word in portfolio):
        domains.append("Portfolio")

    if any(word in text for word in macro):
        domains.append("Macro")

    if not domains:
        domains = ["Business", "Risk", "Portfolio"]

    return domains