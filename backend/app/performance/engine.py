from datetime import datetime, timezone
from typing import Dict, List

import yfinance as yf


BENCHMARKS = {
    "S&P 500": "SPY",
    "Nasdaq 100": "QQQ",
}


def build_performance_report(portfolio: Dict) -> Dict:
    """
    Calculate current portfolio performance and compare it with benchmarks.

    The portfolio is expected to contain:
      - created_at
      - starting_capital
      - cash
      - positions
    """

    positions = portfolio.get("positions", [])
    cash = float(portfolio.get("cash", 0))
    starting_capital = float(portfolio.get("starting_capital", 0))

    updated_positions = update_positions(positions)

    invested_value = round(
        sum(position["current_value"] for position in updated_positions),
        2,
    )

    total_value = round(invested_value + cash, 2)
    total_gain_loss = round(total_value - starting_capital, 2)

    total_return_pct = (
        round((total_gain_loss / starting_capital) * 100, 2)
        if starting_capital
        else 0.0
    )

    benchmark_results = build_benchmark_results(
        created_at=portfolio.get("created_at"),
    )

    return {
        "calculated_at": current_timestamp(),
        "starting_capital": starting_capital,
        "invested_value": invested_value,
        "cash": cash,
        "total_value": total_value,
        "total_gain_loss": total_gain_loss,
        "total_return_pct": total_return_pct,
        "positions": updated_positions,
        "benchmarks": benchmark_results,
        "relative_performance": build_relative_performance(
            portfolio_return=total_return_pct,
            benchmarks=benchmark_results,
        ),
        "status": "READY",
    }


def update_positions(positions: List[Dict]) -> List[Dict]:
    updated = []

    for position in positions:
        ticker = position.get("ticker")
        shares = float(position.get("shares", 0))
        entry_price = float(position.get("entry_price", 0))
        cost_basis = float(position.get("cost_basis", 0))

        current_price = get_current_price(ticker)

        if current_price is None:
            current_price = entry_price

        current_value = round(shares * current_price, 2)
        gain_loss = round(current_value - cost_basis, 2)

        return_pct = (
            round((gain_loss / cost_basis) * 100, 2)
            if cost_basis
            else 0.0
        )

        updated.append(
            {
                **position,
                "current_price": round(current_price, 2),
                "current_value": current_value,
                "unrealized_gain_loss": gain_loss,
                "unrealized_return_pct": return_pct,
            }
        )

    return updated


def get_current_price(ticker: str):
    if not ticker:
        return None

    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="5d")

        if history.empty:
            return None

        return float(history["Close"].dropna().iloc[-1])

    except Exception:
        return None


def build_benchmark_results(created_at: str | None) -> List[Dict]:
    if not created_at:
        return []

    start_date = parse_start_date(created_at)

    if not start_date:
        return []

    results = []

    for benchmark_name, ticker in BENCHMARKS.items():
        result = benchmark_return(
            name=benchmark_name,
            ticker=ticker,
            start_date=start_date,
        )

        if result:
            results.append(result)

    return results


def benchmark_return(
    name: str,
    ticker: str,
    start_date: str,
):
    try:
        history = yf.download(
            ticker,
            start=start_date,
            progress=False,
            auto_adjust=True,
        )

        if history.empty:
            return None

        closes = history["Close"].dropna()

        if len(closes) < 1:
            return None

        start_price = extract_scalar(closes.iloc[0])
        current_price = extract_scalar(closes.iloc[-1])

        gain_loss_pct = (
            round(
                ((current_price - start_price) / start_price) * 100,
                2,
            )
            if start_price
            else 0.0
        )

        return {
            "name": name,
            "ticker": ticker,
            "start_price": round(start_price, 2),
            "current_price": round(current_price, 2),
            "return_pct": gain_loss_pct,
        }

    except Exception:
        return None


def build_relative_performance(
    portfolio_return: float,
    benchmarks: List[Dict],
) -> List[Dict]:
    return [
        {
            "benchmark": item["name"],
            "benchmark_return_pct": item["return_pct"],
            "outperformance_pct": round(
                portfolio_return - item["return_pct"],
                2,
            ),
        }
        for item in benchmarks
    ]


def parse_start_date(created_at: str):
    try:
        parsed = datetime.fromisoformat(
            created_at.replace("Z", "+00:00")
        )

        return parsed.date().isoformat()

    except (TypeError, ValueError):
        return None


def extract_scalar(value) -> float:
    if hasattr(value, "iloc"):
        value = value.iloc[0]

    return float(value)


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()