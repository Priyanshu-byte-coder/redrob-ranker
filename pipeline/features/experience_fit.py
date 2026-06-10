"""
Experience Fit scorer.
Bell curve centered at 7 years. JD range is 5-9 years.
"""
from config import IDEAL_EXPERIENCE_YEARS, EXPERIENCE_RANGE_MIN, EXPERIENCE_RANGE_MAX


def score_experience_fit(candidate: dict) -> float:
    """Score how well candidate's years of experience match JD requirement."""
    yoe = candidate.get("profile", {}).get("years_of_experience", 0)

    if EXPERIENCE_RANGE_MIN <= yoe <= EXPERIENCE_RANGE_MAX:
        # Within ideal range: score 0.85-1.0
        distance = abs(yoe - IDEAL_EXPERIENCE_YEARS)
        return 1.0 - 0.075 * distance  # Max distance is 2yr -> 0.85

    elif 4.0 <= yoe < EXPERIENCE_RANGE_MIN:
        # Slightly junior: 0.6-0.75
        return 0.75 - 0.15 * (EXPERIENCE_RANGE_MIN - yoe)

    elif EXPERIENCE_RANGE_MAX < yoe <= 12.0:
        # Slightly senior: 0.5-0.7
        return 0.70 - 0.07 * (yoe - EXPERIENCE_RANGE_MAX)

    elif yoe < 4.0:
        # Too junior
        return max(0.1, 0.5 - 0.15 * (4.0 - yoe))

    else:
        # Very senior (>12 years) — JD says this is OK if other signals strong
        return max(0.3, 0.5 - 0.02 * (yoe - 12.0))
