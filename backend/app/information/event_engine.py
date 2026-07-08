from typing import Dict, List

from app.information.models import InformationItem


def build_information_events(items: List[InformationItem]) -> List[InformationItem]:
    """
    Consolidate multiple news articles into unique investment events.
    """

    event_groups: Dict[str, List[InformationItem]] = {}

    for item in items:
        key = event_key(item)
        event_groups.setdefault(key, []).append(item)

    events = []

    for _, group in event_groups.items():
        events.append(merge_group(group))

    events.sort(
        key=lambda x: (
            materiality_rank(x.materiality),
            x.confidence,
        ),
        reverse=True,
    )

    return events


def event_key(item: InformationItem) -> str:
    """
    Create a grouping key so multiple articles discussing
    the same event become one Investment Event.
    """

    text = f"{item.title} {item.summary}".lower()

    if item.event_type == "StrategicTransaction":
        return f"{item.ticker}_strategic_transaction"

    if item.event_type == "Earnings":
        return f"{item.ticker}_earnings"

    if item.event_type == "RegulatoryRisk":
        return f"{item.ticker}_regulatory"

    if item.event_type == "Macro":
        return "macro"

    if item.event_type == "Geopolitical":
        return "geopolitical"

    return normalize_title(item.title)


def merge_group(group: List[InformationItem]) -> InformationItem:
    """
    Merge duplicate articles into one event.
    """

    primary = group[0]

    sources = sorted(
        {
            item.source
            for item in group
            if item.source
        }
    )

    domains = sorted(
        {
            domain
            for item in group
            for domain in item.affected_domains
        }
    )

    confidence = min(
        95,
        max(item.confidence for item in group) + (len(group) * 3),
    )

    summary = primary.summary

    if len(group) > 1:
        summary = (
            f"{primary.summary} "
            f"Supported by {len(group)} source(s): "
            f"{', '.join(sources)}."
        )

    return InformationItem(
        title=primary.title,
        source=", ".join(sources),
        category="Investment Event",
        ticker=primary.ticker,
        summary=summary,
        materiality=highest_materiality(group),
        direction=dominant_direction(group),
        confidence=confidence,
        affected_domains=domains,
        url=primary.url,

        # Preserve the classification from the primary article.
        event_type=primary.event_type,
    )


def highest_materiality(group: List[InformationItem]) -> str:
    ranking = {
        "High": 3,
        "Medium": 2,
        "Low": 1,
        "None": 0,
    }

    return max(
        group,
        key=lambda item: ranking.get(item.materiality, 0),
    ).materiality


def dominant_direction(group: List[InformationItem]) -> str:
    bullish = sum(
        1
        for item in group
        if item.direction == "Bullish"
    )

    bearish = sum(
        1
        for item in group
        if item.direction == "Bearish"
    )

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