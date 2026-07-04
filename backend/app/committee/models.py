from dataclasses import dataclass
from typing import List


@dataclass
class CommitteeView:
    member: str
    stance: str
    confidence: int
    score: int
    summary: str
    positives: List[str]
    concerns: List[str]


@dataclass
class CommitteeDecision:
    ticker: str
    company: str
    recommendation: str
    conviction: int
    chairman_summary: str
    member_views: List[CommitteeView]