from app.news_events.engine import build_event_report

from app.signals.models import Signal
from app.signals.weights import weighted_score


def build_signal_engine():
    signals = []

    report = build_event_report()

    for event in report:
        signals.append(
            Signal(
                source=event["source"],
                signal_type="event",
                title=event["title"],
                direction=event["direction"],
                strength=event["event_score"],
                confidence=event["confidence"],
                affected_sectors=event["affected_sectors"],
                affected_companies=event["affected_companies"],
                summary=event["summary"],
            )
        )

    output = []

    for signal in signals:
        output.append(
            {
                "source": signal.source,
                "type": signal.signal_type,
                "title": signal.title,
                "direction": signal.direction,
                "strength": signal.strength,
                "confidence": signal.confidence,
                "weighted_score": weighted_score(
                    signal.strength,
                    signal.confidence,
                    signal.signal_type,
                ),
                "affected_sectors": signal.affected_sectors,
                "affected_companies": signal.affected_companies,
                "summary": signal.summary,
            }
        )

    output.sort(key=lambda x: x["weighted_score"], reverse=True)

    return output