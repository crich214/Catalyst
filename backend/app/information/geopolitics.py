from typing import List

from app.information.models import InformationItem


def get_geopolitical_news() -> List[InformationItem]:
    """
    Temporary non-blocking geopolitical intelligence stub.

    The prior Reuters RSS implementation could hang the entire
    /information/{ticker} request. This stub keeps Catalyst stable
    until a reliable live geopolitical source is added.
    """

    return []