from typing import List

from app.information.company_news import get_company_news
from app.information.earnings import get_earnings_information
from app.information.event_engine import build_information_events
from app.information.geopolitics import get_geopolitical_news
from app.information.macro_news import get_macro_news
from app.information.models import InformationBriefing, InformationItem
from app.information.sec_filings import get_sec_filings


def build_information_briefing(ticker: str, company: str) -> InformationBriefing:
    raw_items: List[InformationItem] = []

    raw_items.extend(get_company_news(ticker))
    raw_items.extend(get_sec_filings(ticker))
    raw_items.extend(get_earnings_information(ticker))
    raw_items.extend(get_macro_news())
    raw_items.extend(get_geopolitical_news())

    events = build_information_events(raw_items)
    overall_materiality = determine_overall_materiality(events)

    return InformationBriefing(
        ticker=ticker,
        company=company,
        items=events,
        overall_materiality=overall_materiality,
        briefing_summary=build_briefing_summary(events, overall_materiality),
    )


def determine_overall_materiality(items: List[InformationItem]) -> str:
    if any(item.materiality == "High" for item in items):
        return "High"

    if any(item.materiality == "Medium" for item in items):
        return "Medium"

    if any(item.materiality == "Low" for item in items):
        return "Low"

    return "None"


def build_briefing_summary(
    items: List[InformationItem],
    overall_materiality: str,
) -> str:
    if not items:
        return "No material outside information identified."

    return (
        f"{len(items)} investment event(s) identified. "
        f"Overall materiality is {overall_materiality}."
    )