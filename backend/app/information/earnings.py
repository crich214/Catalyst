from typing import List

import yfinance as yf

from app.information.classifier import (
    determine_direction,
    determine_event_type,
    determine_materiality,
)
from app.information.domain_router import determine_domains
from app.information.models import InformationItem


def get_earnings_information(ticker: str) -> List[InformationItem]:
    """
    Retrieve live earnings intelligence from Yahoo Finance.

    This module produces normalized InformationItems that flow
    through the same Event Engine as Company News and SEC filings.
    """

    items: List[InformationItem] = []

    try:
        stock = yf.Ticker(ticker)

        calendar = stock.calendar
        info = stock.info

    except Exception:
        return items

    # ----------------------------------------------------------
    # Upcoming Earnings Date
    # ----------------------------------------------------------

    earnings_date = extract_earnings_date(calendar)

    if earnings_date:
        title = f"{ticker.upper()} Upcoming Earnings"

        summary = (
            f"{ticker.upper()} is expected to report earnings on "
            f"{earnings_date}."
        )

        event_type = "Earnings"

        items.append(
            InformationItem(
                title=title,
                source="Yahoo Finance",
                category="Earnings",
                ticker=ticker.upper(),
                summary=summary,
                materiality="Medium",
                direction="Neutral",
                confidence=90,
                affected_domains=determine_domains(event_type),
                event_type=event_type,
            )
        )

    # ----------------------------------------------------------
    # Analyst EPS Estimate
    # ----------------------------------------------------------

    eps = info.get("forwardEps")

    if eps:
        title = f"{ticker.upper()} Forward EPS Estimate"

        summary = (
            f"Consensus forward EPS estimate is {eps}."
        )

        event_type = "Earnings"

        items.append(
            InformationItem(
                title=title,
                source="Yahoo Finance",
                category="Earnings",
                ticker=ticker.upper(),
                summary=summary,
                materiality="Low",
                direction=determine_direction(title, summary),
                confidence=80,
                affected_domains=determine_domains(event_type),
                event_type=event_type,
            )
        )

    # ----------------------------------------------------------
    # Revenue Growth
    # ----------------------------------------------------------

    revenue_growth = info.get("revenueGrowth")

    if revenue_growth is not None:

        pct = round(revenue_growth * 100, 1)

        title = f"{ticker.upper()} Revenue Growth"

        summary = (
            f"Revenue growth is currently {pct}%."
        )

        event_type = "Earnings"

        items.append(
            InformationItem(
                title=title,
                source="Yahoo Finance",
                category="Earnings",
                ticker=ticker.upper(),
                summary=summary,
                materiality=determine_materiality(title, summary),
                direction=determine_direction(title, summary),
                confidence=80,
                affected_domains=determine_domains(event_type),
                event_type=event_type,
            )
        )

    return items


def extract_earnings_date(calendar):
    """
    Handles the different calendar formats returned by yfinance.
    """

    if calendar is None:
        return None

    try:

        if hasattr(calendar, "index"):

            if "Earnings Date" in calendar.index:

                value = calendar.loc["Earnings Date"]

                if hasattr(value, "iloc"):
                    return str(value.iloc[0])[:10]

                return str(value)[:10]

    except Exception:
        pass

    try:

        if isinstance(calendar, dict):

            value = calendar.get("Earnings Date")

            if isinstance(value, list):
                return str(value[0])[:10]

            if value:
                return str(value)[:10]

    except Exception:
        pass

    return None