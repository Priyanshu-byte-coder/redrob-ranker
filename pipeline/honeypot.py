"""
Stage 0: Honeypot detection.
Identifies ~80 candidates with subtly impossible profiles.
Any honeypot in top 100 wastes a slot; >10% = disqualification.
"""
from datetime import datetime, date

from config import (
    HONEYPOT_EXPERT_ZERO_THRESHOLD,
    HONEYPOT_DURATION_TOLERANCE_MONTHS,
    HONEYPOT_CAREER_OVERFLOW_FACTOR,
)


def _parse_date(d: str | None) -> date | None:
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _months_between(d1: date, d2: date) -> int:
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def detect_honeypot(candidate: dict) -> tuple[bool, list[str]]:
    """
    Returns (is_honeypot, list_of_reasons).
    Multiple flags increase confidence.
    """
    reasons = []
    today = date(2026, 6, 10)

    # --- Rule 1: Expert skills with 0 duration ---
    skills = candidate.get("skills", [])
    expert_zero_count = sum(
        1 for s in skills
        if s.get("proficiency") == "expert" and s.get("duration_months", 1) == 0
    )
    if expert_zero_count >= HONEYPOT_EXPERT_ZERO_THRESHOLD:
        reasons.append(f"{expert_zero_count} expert skills with 0 months duration")

    # --- Rule 2: Job duration_months >> calendar difference ---
    for job in candidate.get("career_history", []):
        start = _parse_date(job.get("start_date"))
        end = _parse_date(job.get("end_date"))
        claimed_months = job.get("duration_months", 0)

        if start and end:
            actual_months = _months_between(start, end)
            if claimed_months > actual_months + HONEYPOT_DURATION_TOLERANCE_MONTHS:
                reasons.append(
                    f"Job '{job.get('title')}' claims {claimed_months}mo "
                    f"but dates span {actual_months}mo"
                )
        elif start and not end and job.get("is_current"):
            actual_months = _months_between(start, today)
            if claimed_months > actual_months + HONEYPOT_DURATION_TOLERANCE_MONTHS:
                reasons.append(
                    f"Current job '{job.get('title')}' claims {claimed_months}mo "
                    f"but started {actual_months}mo ago"
                )

    # --- Rule 3: Total career duration wildly exceeds years_of_experience ---
    total_career_months = sum(
        j.get("duration_months", 0) for j in candidate.get("career_history", [])
    )
    yoe = candidate.get("profile", {}).get("years_of_experience", 0)
    expected_max = yoe * 12 * HONEYPOT_CAREER_OVERFLOW_FACTOR
    if total_career_months > expected_max + 24 and yoe > 0:
        reasons.append(
            f"Total career {total_career_months}mo but only {yoe}yr experience"
        )

    # --- Rule 4: Future dates ---
    for job in candidate.get("career_history", []):
        start = _parse_date(job.get("start_date"))
        if start and start > today:
            # Allow up to 1 month in future (rounding)
            if _months_between(today, start) > 1:
                reasons.append(f"Job start date {start} is in the future")

    # --- Rule 5: Contradictory skill count vs experience ---
    advanced_expert_count = sum(
        1 for s in skills
        if s.get("proficiency") in ("advanced", "expert")
    )
    if yoe < 2 and advanced_expert_count >= 10:
        reasons.append(
            f"{advanced_expert_count} advanced/expert skills with only {yoe}yr experience"
        )

    # --- Rule 6: All behavioral rates perfectly 1.0 (too good to be true) ---
    signals = candidate.get("redrob_signals", {})
    perfect_rates = (
        signals.get("recruiter_response_rate", 0) == 1.0
        and signals.get("interview_completion_rate", 0) == 1.0
        and signals.get("offer_acceptance_rate", 0) == 1.0
        and signals.get("profile_completeness_score", 0) == 100
    )
    if perfect_rates:
        reasons.append("All behavioral rates perfectly 1.0 — synthetic profile")

    is_honeypot = len(reasons) >= 1
    return is_honeypot, reasons
