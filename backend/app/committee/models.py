from dataclasses import dataclass
from typing import List


@dataclass
class AnalystReview:
    member: str
    role: str
    domain: str
    assessment: str
    stance: str
    confidence: int
    material_concern: bool
    summary: str
    positives: List[str]
    concerns: List[str]


@dataclass
class CommitteeReview:
    ticker: str
    company: str
    decision_engine_recommendation: str
    decision_engine_score: float
    committee_action: str
    final_recommendation: str
    conviction: int
    chairman_summary: str
    analyst_reviews: List[AnalystReview]