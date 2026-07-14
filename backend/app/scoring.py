BUY_THRESHOLD = 88
ACCUMULATE_THRESHOLD = 75
WATCH_THRESHOLD = 65

HIGH_RISK_THRESHOLD = 85
MOONSHOT_STARTER_THRESHOLD = 75


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


def valuation_score(stock):
    score = 50

    pe = stock.get("pe_ratio")
    fcf = stock.get("fcf_yield")
    price = stock.get("price", 0)
    intrinsic = stock.get("intrinsic_value", 0)
    decline = stock.get("price_decline_pct", 0)

    if pe is None:
        score -= 5
    elif pe < 10:
        score += 25
    elif pe < 15:
        score += 18
    elif pe < 25:
        score += 6
    else:
        score -= 8

    if fcf is None:
        score -= 2
    elif fcf >= 8:
        score += 22
    elif fcf >= 5:
        score += 14
    elif fcf >= 2:
        score += 5
    elif fcf < 0:
        score -= 20

    if intrinsic and price:
        discount = (intrinsic - price) / intrinsic

        if discount >= 0.35:
            score += 20
        elif discount >= 0.20:
            score += 12
        elif discount >= 0.10:
            score += 5
        elif discount < 0:
            score -= 12

    if decline >= 40:
        score += 10
    elif decline >= 25:
        score += 6

    return round(clamp(score), 1)


def opportunity_score(stock):
    valuation = valuation_score(stock)

    score = (
        valuation * 0.30
        + stock["quality"] * 0.20
        + stock["insider"] * 0.20
        + stock["macro"] * 0.15
        + stock["catalyst"] * 0.15
    )

    return round(clamp(score), 1)


def conviction_score(stock, opportunity):
    raw = (
        opportunity * 0.35
        + stock["quality"] * 0.30
        + stock["catalyst"] * 0.15
        + stock["insider"] * 0.10
        - stock["risk"] * 0.10
        + 10
    )

    return round(clamp(raw), 1)


def execution_score(stock):
    price = stock["price"]
    intrinsic = stock["intrinsic_value"]
    insider = stock["insider"]
    decline = stock["price_decline_pct"]

    score = 50
    discount = (intrinsic - price) / intrinsic if intrinsic else 0

    if discount >= 0.35:
        score += 25
    elif discount >= 0.20:
        score += 15
    elif discount >= 0.10:
        score += 6

    if insider >= 80:
        score += 12
    elif insider >= 60:
        score += 6

    if decline >= 35:
        score += 10
    elif decline >= 20:
        score += 5

    return round(clamp(score), 1)


def rich_alpha_score(opportunity, conviction, execution, risk):
    score = (
        opportunity * 0.45
        + conviction * 0.30
        + execution * 0.20
        - risk * 0.10
        + 10
    )

    return round(clamp(score), 1)


def recommendation_from_metrics(
    category: str,
    risk: float,
    rich_alpha: float,
    conviction: float,
) -> str:
    """
    Convert final investment metrics into an actionable recommendation.

    V1 calibration:
      BUY: exceptional score with strong conviction
      ACCUMULATE: attractive opportunity suitable for gradual deployment
      WATCH: promising but not yet actionable
      AVOID: below the minimum opportunity threshold
    """

    if risk >= HIGH_RISK_THRESHOLD:
        return "SPECULATIVE / WATCH ONLY"

    if "Moonshot" in category:
        if rich_alpha >= MOONSHOT_STARTER_THRESHOLD:
            return "SPECULATIVE STARTER"

        return "WATCH"

    if rich_alpha >= BUY_THRESHOLD and conviction >= 75:
        return "BUY"

    if (
        rich_alpha >= ACCUMULATE_THRESHOLD
        and conviction >= 65
        and risk < 70
    ):
        return "ACCUMULATE"

    if rich_alpha >= WATCH_THRESHOLD:
        return "WATCH"

    return "AVOID"


def recommendation(stock, rich_alpha, conviction):
    return recommendation_from_metrics(
        category=stock.get("category", ""),
        risk=float(stock.get("risk", 50)),
        rich_alpha=float(rich_alpha),
        conviction=float(conviction),
    )


def accumulation_plan(stock, recommendation_text):
    price = stock["price"]
    intrinsic = stock["intrinsic_value"]

    max_position = 0.04

    if stock["quality"] >= 90 and stock["risk"] <= 40:
        max_position = 0.08
    elif stock["quality"] >= 80 and stock["risk"] <= 55:
        max_position = 0.06
    elif "Moonshot" in stock["category"]:
        max_position = 0.015

    actionable_recommendations = {
        "BUY",
        "ACCUMULATE",
        "SPECULATIVE STARTER",
    }

    return {
        "strategy": (
            "accumulate"
            if recommendation_text in actionable_recommendations
            else "watch"
        ),
        "current_price": price,
        "intrinsic_value": intrinsic,
        "estimated_margin_of_safety_pct": (
            round(((intrinsic - price) / intrinsic) * 100, 1)
            if intrinsic
            else None
        ),
        "max_position": f"{round(max_position * 100, 1)}%",
        "ladder": [
            {
                "price_zone": f"Below ${round(intrinsic * 0.90, 2)}",
                "action": "Begin position",
                "target_position": (
                    f"{round(max_position * 0.25 * 100, 1)}%"
                ),
            },
            {
                "price_zone": f"Below ${round(intrinsic * 0.80, 2)}",
                "action": "Accumulate",
                "target_position": (
                    f"{round(max_position * 0.50 * 100, 1)}%"
                ),
            },
            {
                "price_zone": f"Below ${round(intrinsic * 0.70, 2)}",
                "action": "Aggressive accumulate if thesis unchanged",
                "target_position": (
                    f"{round(max_position * 0.75 * 100, 1)}%"
                ),
            },
            {
                "price_zone": f"Below ${round(intrinsic * 0.60, 2)}",
                "action": "Maximum allocation if thesis remains intact",
                "target_position": f"{round(max_position * 100, 1)}%",
            },
            {
                "price_zone": f"Above ${round(intrinsic, 2)}",
                "action": "Stop buying / reassess",
                "target_position": "Hold or trim",
            },
        ],
    }


def score_stock(stock):
    valuation = valuation_score(stock)
    opportunity = opportunity_score(stock)
    conviction = conviction_score(stock, opportunity)
    execution = execution_score(stock)

    rich_alpha = rich_alpha_score(
        opportunity,
        conviction,
        execution,
        stock["risk"],
    )

    rec = recommendation(stock, rich_alpha, conviction)

    return {
        "ticker": stock["ticker"],
        "company": stock["company"],
        "category": stock["category"],
        "sector": stock.get("sector"),
        "price": stock["price"],
        "market_cap": stock.get("market_cap"),
        "intrinsic_value": stock["intrinsic_value"],
        "pe_ratio": stock.get("pe_ratio"),
        "fcf_yield": stock.get("fcf_yield"),
        "price_decline_pct": round(
            stock.get("price_decline_pct", 0),
            1,
        ),
        "valuation_score": valuation,
        "opportunity_score": opportunity,
        "conviction_score": conviction,
        "execution_score": execution,
        "risk_score": stock["risk"],
        "rich_alpha_score": rich_alpha,
        "recommendation": rec,
        "top_reason": stock["reason"],
        "data_status": stock.get("data_status", "unknown"),
        "data_warnings": stock.get("data_warnings", []),
        "accumulation_plan": accumulation_plan(stock, rec),
    }