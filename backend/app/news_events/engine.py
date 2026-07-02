from app.news_events.collector import collect_sample_events
from app.news_events.impact import calculate_event_score


def build_event_report():

    events = collect_sample_events()

    report = []

    for event in events:

        score = calculate_event_score(event)

        report.append({
            "title": event.title,
            "source": event.source,
            "category": event.category,
            "importance": event.importance,
            "confidence": event.confidence,
            "time_horizon": event.time_horizon,
            "affected_sectors": event.affected_sectors,
            "affected_companies": event.affected_companies,
            "summary": event.summary,
            "event_score": score["event_score"],
            "direction": score["direction"],
            "risk_level": score["risk_level"],
        })

    report.sort(key=lambda x: x["event_score"], reverse=True)

    return report