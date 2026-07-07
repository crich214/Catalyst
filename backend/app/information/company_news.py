from typing import List

from app.information.models import InformationItem


def get_company_news(ticker: str) -> List[InformationItem]:
    """
    Temporary implementation.

    v1.0 will later replace this with live company news.
    """

    items: List[InformationItem] = []

    if ticker.upper() == "FISV":
        items.append(
            InformationItem(
                title="Strategic review of debit processing business",
                source="Catalyst Demo",
                category="Company News",
                ticker="FISV",
                summary=(
                    "Reports indicate Fiserv is evaluating strategic "
                    "alternatives for part of its debit processing business."
                ),
                materiality="High",
                direction="Neutral",
                confidence=90,
                affected_domains=[
                    "Business",
                    "Risk",
                    "Portfolio",
                ],
                url=None,
            )
        )

    return items