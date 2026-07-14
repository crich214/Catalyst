import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


PILOT_CAPITAL = 5000.0

ACTIONABLE_RECOMMENDATIONS = {
    "BUY",
    "ACCUMULATE",
    "SPECULATIVE STARTER",
}

DATA_DIR = Path(__file__).resolve().parent / "data"
PORTFOLIO_FILE = DATA_DIR / "pilot_portfolio.json"


def build_pilot_portfolio(
    opportunities: List[dict],
    capital: float = PILOT_CAPITAL,
) -> Dict:
    actionable = [
        item
        for item in opportunities
        if item.get("recommendation") in ACTIONABLE_RECOMMENDATIONS
    ]

    actionable.sort(
        key=lambda item: item.get(
            "adjusted_rich_alpha_score",
            item.get("rich_alpha_score", 0),
        ),
        reverse=True,
    )

    selected = actionable[:3]

    cash_reserve_pct = 35.0
    investable_capital = round(
        capital * (1 - cash_reserve_pct / 100),
        2,
    )

    if not selected:
        portfolio = {
            "created_at": current_timestamp(),
            "starting_capital": capital,
            "invested_capital": 0.0,
            "cash": capital,
            "cash_reserve_pct": 100.0,
            "positions": [],
            "status": "NO_ACTIONABLE_OPPORTUNITIES",
        }

        save_pilot_portfolio(portfolio)
        return portfolio

    total_score = sum(
        float(
            item.get(
                "adjusted_rich_alpha_score",
                item.get("rich_alpha_score", 0),
            )
        )
        for item in selected
    )

    positions = []

    for item in selected:
        score = float(
            item.get(
                "adjusted_rich_alpha_score",
                item.get("rich_alpha_score", 0),
            )
        )

        weight = score / total_score if total_score else 0
        target_amount = round(investable_capital * weight, 2)

        price = float(item.get("price") or 0)
        shares = round(target_amount / price, 4) if price else 0
        actual_cost = round(shares * price, 2)

        positions.append(
            {
                "ticker": item.get("ticker"),
                "company": item.get("company"),
                "recommendation": item.get("recommendation"),
                "rich_alpha_score": score,
                "conviction_score": item.get("conviction_score"),
                "risk_score": item.get("risk_score"),
                "entry_price": price,
                "shares": shares,
                "target_amount": target_amount,
                "cost_basis": actual_cost,
                "current_value": actual_cost,
                "unrealized_gain_loss": 0.0,
                "unrealized_return_pct": 0.0,
                "margin_of_safety_pct": (
                    item.get("accumulation_plan", {})
                    .get("estimated_margin_of_safety_pct")
                ),
                "reason": item.get("top_reason"),
            }
        )

    invested_capital = round(
        sum(position["cost_basis"] for position in positions),
        2,
    )

    portfolio = {
        "created_at": current_timestamp(),
        "starting_capital": capital,
        "invested_capital": invested_capital,
        "cash": round(capital - invested_capital, 2),
        "cash_reserve_pct": round(
            ((capital - invested_capital) / capital) * 100,
            1,
        ),
        "positions": positions,
        "status": "READY",
    }

    save_pilot_portfolio(portfolio)

    return portfolio


def save_pilot_portfolio(portfolio: Dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    temporary_file = PORTFOLIO_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(portfolio, file, indent=2)

    temporary_file.replace(PORTFOLIO_FILE)


def load_pilot_portfolio() -> Dict | None:
    if not PORTFOLIO_FILE.exists():
        return None

    try:
        with PORTFOLIO_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else None

    except (json.JSONDecodeError, OSError):
        return None


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()