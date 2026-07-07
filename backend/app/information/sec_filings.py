from typing import List

from app.information.models import InformationItem


def get_sec_filings(ticker: str) -> List[InformationItem]:
    """
    Placeholder for SEC filing intelligence.

    v1 will retrieve and normalize:
      - 8-K filings
      - 10-Q filings
      - 10-K filings
      - Insider transactions
      - Proxy statements
      - Material SEC disclosures
    """

    return []