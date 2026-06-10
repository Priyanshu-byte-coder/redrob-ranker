"""
Stage 1: Coarse filter.
Reduces 100K candidates to ~3-5K worth scoring in detail.
Single-pass, combined with honeypot detection for efficiency.
"""
from config import MIN_EXPERIENCE_YEARS
from jd.taxonomy import (
    NON_TECHNICAL_TITLES,
    MAYBE_TECHNICAL_TITLES,
    ML_DOMAIN_KEYWORDS,
)
from pipeline.honeypot import detect_honeypot


def _has_ml_in_descriptions(candidate: dict) -> bool:
    """Check if any career_history description mentions ML/AI work."""
    for job in candidate.get("career_history", []):
        desc = job.get("description", "").lower()
        if any(kw in desc for kw in ML_DOMAIN_KEYWORDS):
            return True
    return False


def _has_ml_skills(candidate: dict, threshold: int = 2) -> bool:
    """Check if candidate has at least `threshold` ML-related skills."""
    from jd.taxonomy import SKILL_TIER_LOOKUP, SKILL_ALIASES

    count = 0
    for skill in candidate.get("skills", []):
        name = skill.get("name", "").lower()
        # Check direct match
        if name in SKILL_TIER_LOOKUP and SKILL_TIER_LOOKUP[name] <= 2:
            count += 1
        # Check aliases
        elif name in SKILL_ALIASES:
            canonical = SKILL_ALIASES[name]
            if canonical in SKILL_TIER_LOOKUP and SKILL_TIER_LOOKUP[canonical] <= 2:
                count += 1
        if count >= threshold:
            return True
    return False


def coarse_filter(candidate: dict) -> tuple[bool, bool, list[str]]:
    """
    Returns (should_keep, is_honeypot, honeypot_reasons).
    Combined pass for efficiency.
    """
    # Honeypot check first
    is_honeypot, hp_reasons = detect_honeypot(candidate)
    if is_honeypot:
        return False, True, hp_reasons

    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "")

    # Too junior
    if yoe < MIN_EXPERIENCE_YEARS:
        return False, False, []

    # Non-technical title with no ML evidence
    if title in NON_TECHNICAL_TITLES:
        if not _has_ml_in_descriptions(candidate):
            return False, False, []
        # Has ML in descriptions but non-tech title — this is a keyword stuffer
        # Unless they actually have career history in ML (rare)
        if not _has_ml_skills(candidate, threshold=3):
            return False, False, []
        # Keep but will be heavily penalized by anti-pattern scorer

    # Maybe-technical titles: keep if any ML signal
    if title in MAYBE_TECHNICAL_TITLES:
        if not (_has_ml_in_descriptions(candidate) or _has_ml_skills(candidate, threshold=2)):
            return False, False, []

    # For all other titles (tech titles), keep them
    return True, False, []
