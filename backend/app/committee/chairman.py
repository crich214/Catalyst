from app.committee.models import CommitteeDecision


def chairman_decision(ticker: str, company: str, member_views):
    average_score = round(
        sum(view.score for view in member_views) / len(member_views)
    )

    bullish_count = len([v for v in member_views if v.stance == "Bullish"])
    cautious_count = len([v for v in member_views if v.stance == "Cautious"])
    bearish_count = len([v for v in member_views if v.stance == "Bearish"])

    if average_score >= 80 and cautious_count == 0 and bearish_count == 0:
        recommendation = "BUY"
    elif average_score >= 70 and bearish_count == 0:
        recommendation = "WATCH / ACCUMULATE ON WEAKNESS"
    elif cautious_count >= 2 or bearish_count >= 1:
        recommendation = "WAIT"
    else:
        recommendation = "WATCH"

    chairman_summary = (
        f"The committee reviewed {company} using macro, business, risk, "
        f"and portfolio perspectives. Average committee score is {average_score}. "
        f"The resulting recommendation is {recommendation}."
    )

    return CommitteeDecision(
        ticker=ticker,
        company=company,
        recommendation=recommendation,
        conviction=average_score,
        chairman_summary=chairman_summary,
        member_views=member_views,
    )