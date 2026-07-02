from dataclasses import dataclass
from typing import List


@dataclass
class Signal:
    source: str
    signal_type: str
    title: str
    direction: str
    strength: int
    confidence: int
    affected_sectors: List[str]
    affected_companies: List[str]
    summary: str