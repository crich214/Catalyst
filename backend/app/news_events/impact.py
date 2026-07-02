def calculate_event_score(event):
    base_score = event.importance * 0.7 + event.confidence * 0.3

    if event.bullish and event.bearish:
        direction = "mixed"
    elif event.bullish:
        direction = "bullish"
    elif event.bearish:
        direction = "bearish"
    else:
        direction = "neutral"

    return {
        "event_score": round(base_score),
        "direction": direction,
        "risk_level": "High" if base_score >= 85 else "Medium" if base_score >= 65 else "Low",
    }