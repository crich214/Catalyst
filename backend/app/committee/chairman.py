from app.committee.models import CommitteeReview


def chairman_review(
    ticker: str,
    company: str,
    decision_engine_recommendation: str,
    decision_engine_score: float,
    analyst_reviews,
):
    supportive_count = len([
        review for review in analyst_reviews
        if review.stance in ["Supportive", "Constructive"]
    ])

    cautious_count = len([
        review for review in analyst_reviews
        if review.stance in ["Cautious", "Restrictive", "Defensive"]
    ])

    total_reviews = len(analyst_reviews)

    # Default: committee affirms the Decision Engine.
    committee_action = "AFFIRM"
    final_recommendation = decision_engine_recommendation

    # Committee modifies only when there is meaningful caution.
    if cautious_count >= 2:
        committee_action = "MODIFY"
        final_recommendation = "WATCH"

    # Committee overrides only in rare high-risk situations.
    if cautious_count >= 3:
        committee_action = "OVERRIDE"
        final_recommendation = "WAIT"

    conviction = round(
        (decision_engine_score * 0.65)
        + ((supportive_count / max(total_reviews, 1)) * 100 * 0.35)
    )

    chairman_summary = (
        f"The Decision Engine recommends {decision_engine_recommendation}. "
        f"The Investment Committee reviewed {company} across macro, business, risk, "
        f"and portfolio perspectives. The committee action is {committee_action}. "
        f"The final recommendation is {final_recommendation}."
    )

    return CommitteeReview(
        ticker=ticker,
        company=company,
        decision_engine_recommendation=decision_engine_recommendation,
        decision_engine_score=decision_engine_score,
        committee_action=committee_action,
        final_recommendation=final_recommendation,
        conviction=max(0, min(100, conviction)),
        chairman_summary=chairman_summary,
        analyst_reviews=analyst_reviews,
    )