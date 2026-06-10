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

    # 7. Profile completeness (weight: 0.05)
    components["profile_complete"] = signals.get("profile_completeness_score", 50) / 100.0

    # 8. Verification trust (weight: 0.10)
    verified = 0
    if signals.get("verified_email", False):
        verified += 1
    if signals.get("verified_phone", False):
        verified += 1
    if signals.get("linkedin_connected", False):
        verified += 1
    components["verification"] = verified / 3.0

    # Weighted composite
    score = (
        0.20 * components["notice"]
        + 0.20 * components["response_rate"]
        + 0.15 * components["recency"]
        + 0.10 * components["open_to_work"]
        + 0.10 * components["github"]
        + 0.10 * components["interview_completion"]
        + 0.05 * components["profile_complete"]
        + 0.10 * components["verification"]
    )

    return min(1.0, score), components
