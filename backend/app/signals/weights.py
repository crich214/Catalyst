SIGNAL_TYPE_WEIGHTS = {
    "macro": 1.0,
    "market": 0.9,
    "event": 0.8,
    "company": 1.0,
    "insider": 0.7,
    "congress": 0.7,
}


def weighted_score(strength: int, confidence: int, signal_type: str) -> int:
    weight = SIGNAL_TYPE_WEIGHTS.get(signal_type, 0.5)
    raw_score = (strength * 0.7) + (confidence * 0.3)
    return round(raw_score * weight)