"""
Behavioral Signals scorer.
Measures candidate availability and engagement — a perfect-on-paper candidate
who hasn't logged in for 6 months is not actually available.
"""
from datetime import datetime, date
from config import NOTICE_PERIOD_IDEAL_MAX, NOTICE_PERIOD_ACCEPTABLE_MAX, RECENCY_CUTOFF_DAYS


def _days_since(date_str: str, today: date) -> int:
    """Days between a date string and today."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (today - d).days
    except (ValueError, TypeError):
        return 999  # Unknown = treat as stale


def score_behavioral_signals(candidate: dict) -> tuple[float, dict]:
    """
    Composite behavioral score from multiple signals.
    Returns (score, detail_dict).
    """
    signals = candidate.get("redrob_signals", {})
    today = date(2026, 6, 10)

    components = {}

    # 1. Notice period (weight: 0.20)
    notice = signals.get("notice_period_days", 90)
    if notice <= NOTICE_PERIOD_IDEAL_MAX:
        components["notice"] = 1.0
    elif notice <= NOTICE_PERIOD_ACCEPTABLE_MAX:
        components["notice"] = 0.7 - 0.3 * (notice - NOTICE_PERIOD_IDEAL_MAX) / (NOTICE_PERIOD_ACCEPTABLE_MAX - NOTICE_PERIOD_IDEAL_MAX)
    elif notice <= 120:
        components["notice"] = 0.3
    else:
        components["notice"] = 0.15

    # 2. Recruiter response rate (weight: 0.20)
    components["response_rate"] = signals.get("recruiter_response_rate", 0.0)

    # 3. Activity recency (weight: 0.15)
    last_active = signals.get("last_active_date", "")
    days_inactive = _days_since(last_active, today)
    if days_inactive <= 30:
        components["recency"] = 1.0
    elif days_inactive <= 90:
        components["recency"] = 0.8
    elif days_inactive <= RECENCY_CUTOFF_DAYS:
        components["recency"] = 0.5
    else:
        components["recency"] = 0.2

    # 4. Open to work (weight: 0.10)
    components["open_to_work"] = 1.0 if signals.get("open_to_work_flag", False) else 0.3

    # 5. GitHub activity (weight: 0.10)
    github = signals.get("github_activity_score", -1)
    if github < 0:
        components["github"] = 0.3  # No GitHub linked — not a penalty
    else:
        components["github"] = github / 100.0

    # 6. Interview completion rate (weight: 0.10)
    components["interview_completion"] = max(0.0, signals.get("interview_completion_rate", 0.5))

    # 7. Profile completeness (weight: 0.04)
    components["profile_complete"] = signals.get("profile_completeness_score", 50) / 100.0

    # 8. Verification trust (weight: 0.08)
    verified = 0
    if signals.get("verified_email", False):
        verified += 1
    if signals.get("verified_phone", False):
        verified += 1
    if signals.get("linkedin_connected", False):
        verified += 1
    components["verification"] = verified / 3.0

    # 9. Saved by recruiters — market demand signal (weight: 0.06)
    saved = signals.get("saved_by_recruiters_30d", 0)
    if saved >= 10:
        components["saved_by_recruiters"] = 1.0
    elif saved >= 5:
        components["saved_by_recruiters"] = 0.8
    elif saved >= 2:
        components["saved_by_recruiters"] = 0.6
    elif saved >= 1:
        components["saved_by_recruiters"] = 0.4
    else:
        components["saved_by_recruiters"] = 0.2

    # 10. Search appearances — recruiter visibility (weight: 0.04)
    appearances = signals.get("search_appearance_30d", 0)
    components["search_appearance"] = min(1.0, appearances / 50.0) if appearances > 0 else 0.2

    # 11. Avg response time — engagement speed (weight: 0.04)
    resp_time = signals.get("avg_response_time_hours", 72)
    if resp_time <= 4:
        components["avg_response_time"] = 1.0
    elif resp_time <= 12:
        components["avg_response_time"] = 0.8
    elif resp_time <= 24:
        components["avg_response_time"] = 0.6
    elif resp_time <= 48:
        components["avg_response_time"] = 0.4
    else:
        components["avg_response_time"] = 0.2

    # 12. Offer acceptance rate — reliability (weight: 0.04)
    oar = signals.get("offer_acceptance_rate", -1)
    if oar < 0:
        components["offer_acceptance"] = 0.5  # No history — neutral
    else:
        components["offer_acceptance"] = oar

    # 13. Applications submitted — active job seeking (weight: 0.03)
    apps = signals.get("applications_submitted_30d", 0)
    if apps >= 1 and apps <= 10:
        components["applications"] = 0.8  # Actively looking but not desperate
    elif apps > 10:
        components["applications"] = 0.5  # Spray-and-pray pattern
    else:
        components["applications"] = 0.3  # Not actively looking

    # 14. Connection count — professional network (weight: 0.02)
    connections = signals.get("connection_count", 0)
    if connections >= 500:
        components["connections"] = 1.0
    elif connections >= 200:
        components["connections"] = 0.7
    elif connections >= 50:
        components["connections"] = 0.5
    else:
        components["connections"] = 0.3

    # 15. Endorsements received — peer validation (weight: 0.02)
    endorsements = signals.get("endorsements_received", 0)
    if endorsements >= 50:
        components["endorsements"] = 1.0
    elif endorsements >= 20:
        components["endorsements"] = 0.7
    elif endorsements >= 5:
        components["endorsements"] = 0.5
    else:
        components["endorsements"] = 0.3

    # 16. Platform tenure via signup_date — established profiles (weight: 0.01)
    signup = signals.get("signup_date", "")
    signup_days = _days_since(signup, today)
    if signup_days >= 365:
        components["tenure"] = 1.0  # 1yr+ on platform
    elif signup_days >= 180:
        components["tenure"] = 0.7
    elif signup_days >= 30:
        components["tenure"] = 0.5
    else:
        components["tenure"] = 0.3  # Very new — could be synthetic

    # 17. Profile views — recruiter interest / market demand (weight: 0.03)
    views = signals.get("profile_views_received_30d", 0)
    if views >= 30:
        components["profile_views"] = 1.0
    elif views >= 15:
        components["profile_views"] = 0.8
    elif views >= 5:
        components["profile_views"] = 0.6
    elif views >= 1:
        components["profile_views"] = 0.4
    else:
        components["profile_views"] = 0.2

    # 18. Salary feasibility — hiring reachability for Series A startup (weight: 0.01)
    # Senior AI Engineer at Series A: realistic range is 15-60 LPA in India
    salary_data = signals.get("expected_salary_range_inr_lpa", {})
    if salary_data and isinstance(salary_data, dict):
        salary_max = salary_data.get("max", 0) or 0
        if salary_max == 0:
            components["salary_feasibility"] = 0.5  # Not specified — neutral
        elif salary_max <= 45:
            components["salary_feasibility"] = 1.0  # Ideal range
        elif salary_max <= 60:
            components["salary_feasibility"] = 0.8  # Acceptable stretch
        elif salary_max <= 80:
            components["salary_feasibility"] = 0.5  # High but possible
        else:
            components["salary_feasibility"] = 0.2  # Likely unreachable for Series A
    else:
        components["salary_feasibility"] = 0.5  # Missing — neutral

    # Weighted composite (18 components, all 23 redrob_signals used, weights sum to 1.0)
    score = (
        0.13 * components["notice"]
        + 0.14 * components["response_rate"]
        + 0.11 * components["recency"]
        + 0.07 * components["open_to_work"]
        + 0.07 * components["github"]
        + 0.07 * components["interview_completion"]
        + 0.04 * components["profile_complete"]
        + 0.07 * components["verification"]
        + 0.06 * components["saved_by_recruiters"]
        + 0.04 * components["search_appearance"]
        + 0.04 * components["avg_response_time"]
        + 0.04 * components["offer_acceptance"]
        + 0.03 * components["applications"]
        + 0.02 * components["connections"]
        + 0.02 * components["endorsements"]
        + 0.01 * components["tenure"]
        + 0.03 * components["profile_views"]
        + 0.01 * components["salary_feasibility"]
    )

    return min(1.0, score), components
