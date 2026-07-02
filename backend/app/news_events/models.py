from dataclasses import dataclass
from typing import List


@dataclass
class Event:

    title: str

    source: str

    category: str

    importance: int

    confidence: int

    time_horizon: str

    affected_sectors: List[str]

    affected_companies: List[str]

    summary: str

    bullish: bool

    bearish: bool