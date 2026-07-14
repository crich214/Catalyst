import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


DATA_DIR = Path(__file__).resolve().parent / "data"
JOURNAL_FILE = DATA_DIR / "decisions.json"


def record_decision(
    ticker: str,
    company: str,
    recommendation: str,
    rich_alpha_score: float,
    conviction_score: float,
    risk_score: float,
    price: float,
    committee_action: str = "",
    chairman_summary: str = "",
    reasons: List[str] | None = None,
) -> Dict:
    """
    Persist a Catalyst investment decision to the local decision journal.
    """

    entry = {
        "recorded_at": current_timestamp(),
        "ticker": ticker.upper(),
        "company": company,
        "recommendation": recommendation,
        "rich_alpha_score": rich_alpha_score,
        "conviction_score": conviction_score,
        "risk_score": risk_score,
        "price": price,
        "committee_action": committee_action,
        "chairman_summary": chairman_summary,
        "reasons": reasons or [],
    }

    journal = read_journal()
    journal.append(entry)
    write_journal(journal)

    return entry


def read_journal() -> List[Dict]:
    """
    Return all saved Catalyst decisions.
    """

    ensure_storage()

    try:
        with JOURNAL_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def latest_decisions(limit: int = 50) -> List[Dict]:
    """
    Return the most recent journal entries.
    """

    journal = read_journal()

    return list(
        reversed(
            journal[-max(1, limit):]
        )
    )


def decisions_for_ticker(ticker: str) -> List[Dict]:
    """
    Return all journal entries for a specific ticker.
    """

    target = ticker.upper().strip()

    return [
        entry
        for entry in read_journal()
        if entry.get("ticker") == target
    ]


def write_journal(entries: List[Dict]) -> None:
    """
    Persist the full journal safely.
    """

    ensure_storage()

    temporary_file = JOURNAL_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(
            entries,
            file,
            indent=2,
        )

    temporary_file.replace(JOURNAL_FILE)


def ensure_storage() -> None:
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not JOURNAL_FILE.exists():
        JOURNAL_FILE.write_text(
            "[]",
            encoding="utf-8",
        )


def current_timestamp() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()