from typing import Dict, List

from app.information.models import InformationItem


def build_information_events(items: List[InformationItem]) -> List[InformationItem]:
    event_groups: Dict[str, List[InformationItem]] = {}

    for item in items:
        key = event_key(item)
        event_groups.setdefault(key, []).append(item)

    events = [merge_group(group) for group in event_groups.values()]

    events.sort(
        key=lambda x: (
            materiality_rank(x.materiality),
            x.confidence,
        ),
        reverse=True,
    )

    return events


def event_key(item: InformationItem) -> str:
    text = f"{item.title} {item.summary}".lower()
    ticker = item.ticker or "MARKET"

    if item.event_type == "Governance":
        if is_executive_change(text):
            return f"{ticker}_governance_executive_change"

        return f"{ticker}_governance"

    if item.event_type == "RegulatoryRisk":
        if "8-k" in text or "material current report" in text:
            return f"{ticker}_governance_executive_change"

        return f"{ticker}_regulatory"

    if item.event_type == "StrategicTransaction":
        return f"{ticker}_strategic_transaction"

    if item.event_type == "InsiderActivity":
        return f"{ticker}_insider_activity"

    if item.event_type == "Earnings":
        return f"{ticker}_earnings"

    if item.event_type == "Macro":
        return "macro"

    if item.event_type == "Geopolitical":
        return "geopolitical"

    if is_executive_change(text):
        return f"{ticker}_governance_executive_change"

    return normalize_title(item.title)


def merge_group(group: List[InformationItem]) -> InformationItem:
    primary = select_primary_item(group)

    sources = sorted({item.source for item in group if item.source})

    domains = sorted({
        domain
        for item in group
        for domain in item.affected_domains
    })

    confidence = min(
        95,
        max(item.confidence for item in group) + (len(group) * 3),
    )

    event_type = determine_group_event_type(group)

    summary = primary.summary

    if len(group) > 1:
        summary = (
            f"{primary.summary} "
            f"Supported by {len(group)} source(s): {', '.join(sources)}."
        )

    return InformationItem(
        title=group_title(group, primary),
        source=", ".join(sources),
        category="Investment Event",
        ticker=primary.ticker,
        summary=summary,
        materiality=highest_materiality(group),
        direction=dominant_direction(group),
        confidence=confidence,
        affected_domains=domains,
        url=primary.url,
        event_type=event_type,
    )


def determine_group_event_type(group: List[InformationItem]) -> str:
    event_types = {item.event_type for item in group}

    priority = [
        "Governance",
        "StrategicTransaction",
        "RegulatoryRisk",
        "InsiderActivity",
        "Earnings",
        "Macro",
        "Geopolitical",
        "General",
    ]

    for event_type in priority:
        if event_type in event_types:
            return event_type

    return "General"


def group_title(group: List[InformationItem], primary: InformationItem) -> str:
    event_type = determine_group_event_type(group)

    if event_type == "Governance":
        return f"{primary.ticker} Executive Leadership Change"

    if event_type == "StrategicTransaction":
        return f"{primary.ticker} Strategic Transaction"

    if event_type == "InsiderActivity":
        return f"{primary.ticker} Insider Activity"

    if event_type == "RegulatoryRisk":
        return f"{primary.ticker} Regulatory Development"

    return primary.title


def is_executive_change(text: str) -> bool:
    executive_terms = [
        "president",
        "ceo",
        "cfo",
        "chief",
        "executive",
    ]

    change_terms = [
        "resigns",
        "resignation",
        "exits",
        "leaves",
        "steps down",
        "retires",
        "departure",
    ]

    return (
        any(term in text for term in executive_terms)
        and any(term in text for term in change_terms)
    )


def select_primary_item(group: List[InformationItem]) -> InformationItem:
    source_priority = {
        "SEC EDGAR": 100,
        "Reuters": 95,
        "Wall Street Journal": 94,
        "Barrons.com": 90,
        "Barron's": 90,
        "American Banker": 88,
        "Milwaukee Journal Sentinel": 85,
        "Payments Dive": 82,
        "Yahoo Finance": 70,
        "Zacks": 65,
        "Simply Wall St.": 60,
        "Stocktwits": 40,
    }

    return max(
        group,
        key=lambda item: (
            materiality_rank(item.materiality),
            source_priority.get(item.source, 50),
            item.confidence,
        ),
    )


def highest_materiality(group: List[InformationItem]) -> str:
    return max(
        group,
        key=lambda item: materiality_rank(item.materiality),
    ).materiality


def dominant_direction(group: List[InformationItem]) -> str:
    bullish = sum(1 for item in group if item.direction == "Bullish")
    bearish = sum(1 for item in group if item.direction == "Bearish")

    if bullish > bearish:
        return "Bullish"

    if bearish > bullish:
        return "Bearish"

    return "Neutral"


def materiality_rank(materiality: str) -> int:
    return {
        "High": 3,
        "Medium": 2,
        "Low": 1,
        "None": 0,
    }.get(materiality, 0)


def normalize_title(title: str) -> str:
    return (
        title.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(":", "")
        .replace(",", "")
        .replace(".", "")
    )