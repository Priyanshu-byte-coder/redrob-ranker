"""
Location scorer.
Pune/Noida preferred, Tier-1 Indian cities acceptable, international case-by-case.
"""
from jd.taxonomy import LOCATION_TIER1_INDIA, LOCATION_TIER2_INDIA, LOCATION_TIER3_INDIA


def score_location(candidate: dict) -> float:
    """Score candidate's location fit for Pune/Noida hybrid role."""
    profile = candidate.get("profile", {})
    location = profile.get("location", "").lower().strip()
    country = profile.get("country", "").lower().strip()
    signals = candidate.get("redrob_signals", {})
    willing_to_relocate = signals.get("willing_to_relocate", False)
    work_mode = signals.get("preferred_work_mode", "onsite")

    # Check India tiers
    for city in LOCATION_TIER1_INDIA:
        if city in location:
            return 1.0

    for city in LOCATION_TIER2_INDIA:
        if city in location:
            return 0.90

    # India but not Tier 1/2
    if country == "india":
        for city in LOCATION_TIER3_INDIA:
            if city in location:
                return 0.80
        # Some other Indian city
        return 0.75

    # International
    base = 0.40
    if willing_to_relocate:
        base += 0.20
    if work_mode in ("remote", "flexible"):
        base += 0.10
    return min(0.80, base)
