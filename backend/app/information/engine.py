from typing import List

from app.information.company_news import get_company_news
from app.information.earnings import get_earnings_information
from app.information.geopolitics import get_geopolitical_news
from app.information.macro_news import get_macro_news
from app.information.models import InformationBriefing, InformationItem
from app.information.sec_filings import get_sec_filings


def build_information_briefing(ticker: str, company: str) -> InformationBriefing:
    """
    Build a structured information briefing for the Investment Committee.

    v1 gathers information from:
      - Company news
      - SEC filings
      - Earnings information
      - Macro developments
      - Geopolitical developments

    Each source returns normalized InformationItem objects.
    """

    items: List[InformationItem] = []

    items.extend(get_company_news(ticker))
    items.extend(get_sec_filings(ticker))
    items.extend(get_earnings_information(ticker))
    items.extend(get_macro_news())
    items.extend(get_geopolitical_news())

    overall_materiality = determine_overall_materiality(items)

    return InformationBriefing(
        ticker=ticker,
        company=company,
        items=items,
        overall_materiality=overall_materiality,
        briefing_summary=build_briefing_summary(items, overall_materiality),
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
        f"{len(items)} information item(s) identified. "
        f"Overall materiality is {overall_materiality}."
    )