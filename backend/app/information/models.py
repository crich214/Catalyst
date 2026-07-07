from dataclasses import dataclass
from typing import List, Optional


@dataclass
class InformationItem:
    title: str
    source: str
    category: str
    ticker: Optional[str]
    summary: str
    materiality: str
    direction: str
    confidence: int
    affected_domains: List[str]
    url: Optional[str] = None


@dataclass
class InformationBriefing:
    ticker: str
    company: str
    items: List[InformationItem]
    overall_materiality: str
    briefing_summary: str