from typing import List

import yfinance as yf

from app.information.classifier import determine_direction, determine_materiality
from app.information.domain_router import determine_domains
from app.information.models import InformationItem


def get_company_news(ticker: str) -> List[InformationItem]:
    """
    Retrieves recent company news from Yahoo Finance and converts it
    into Catalyst InformationItems.
    """

    items: List[InformationItem] = []

    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news or []
    except Exception:
        return items

    for article in news_items[:5]:
        content = article.get("content", article)

        title = content.get("title") or "Untitled"
        summary = (
            content.get("summary")
            or content.get("description")
            or title
        )

        provider = content.get("provider") or {}
        source = provider.get("displayName") or "Yahoo Finance"

        canonical = content.get("canonicalUrl") or {}
        clickthrough = content.get("clickThroughUrl") or {}

        url = (
            canonical.get("url")
            or clickthrough.get("url")
            or article.get("link")
        )

        items.append(
            InformationItem(
                title=title,
                source=source,
                category="Company News",
                ticker=ticker.upper(),
                summary=summary,
                materiality=determine_materiality(title, summary),
                direction=determine_direction(title, summary),
                confidence=75,
                affected_domains=determine_domains(title, summary),
                url=url,
            )
        )

    return items