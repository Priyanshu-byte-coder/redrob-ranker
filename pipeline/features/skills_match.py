"""
Skills Match scorer.
3-tier skill taxonomy with trust multiplier to penalize keyword stuffers.
"""
from jd.taxonomy import SKILL_TIER_LOOKUP, SKILL_ALIASES, TIER1_SKILLS, TIER2_SKILLS, TIER3_SKILLS
from config import SKILL_TRUST_MULTIPLIERS, SKILL_TIER_WEIGHTS


def _resolve_skill_name(name: str) -> str:
    """Resolve a skill name to its canonical lowercase form."""
    lower = name.lower().strip()
    if lower in SKILL_ALIASES:
        return SKILL_ALIASES[lower]
    return lower


def _trust_multiplier(skill: dict) -> float:
    """
    How much to trust this skill claim based on proficiency + duration.
    Expert with 0 months = likely keyword stuffer.
    """
    prof = skill.get("proficiency", "beginner")
    duration = skill.get("duration_months", 0)
    endorsements = skill.get("endorsements", 0)

    if prof == "expert":
        if duration == 0:
            return SKILL_TRUST_MULTIPLIERS["expert_zero_duration"]
        return SKILL_TRUST_MULTIPLIERS["expert_with_duration"]
    elif prof == "advanced":
        if duration == 0:
            return SKILL_TRUST_MULTIPLIERS["advanced_zero_duration"]
        return SKILL_TRUST_MULTIPLIERS["advanced_with_duration"]
    elif prof == "intermediate":
        return SKILL_TRUST_MULTIPLIERS["intermediate"]
    else:
        return SKILL_TRUST_MULTIPLIERS["beginner"]


def score_skills_match(candidate: dict) -> tuple[float, dict]:
    """
    Returns (score, detail_dict) where detail_dict has per-tier breakdowns.
    """
    skills = candidate.get("skills", [])

    tier_hits = {1: 0.0, 2: 0.0, 3: 0.0}
    tier_totals = {
        1: len(TIER1_SKILLS),
        2: len(TIER2_SKILLS),
        3: len(TIER3_SKILLS),
    }
    matched_skills = []

    for skill in skills:
        name = skill.get("name", "")
        canonical = _resolve_skill_name(name)
        tier = SKILL_TIER_LOOKUP.get(canonical)

        if tier is not None:
            trust = _trust_multiplier(skill)
            tier_hits[tier] += trust
            if trust > 0.5:
                matched_skills.append(name)

    # Normalize each tier to 0-1
    tier_scores = {}
    for t in (1, 2, 3):
        # Cap at 1.0 — having more matches than expected doesn't help
        tier_scores[t] = min(1.0, tier_hits[t] / max(tier_totals[t] * 0.3, 1))

    # Weighted composite
    composite = (
        SKILL_TIER_WEIGHTS["tier1"] * tier_scores[1]
        + SKILL_TIER_WEIGHTS["tier2"] * tier_scores[2]
        + SKILL_TIER_WEIGHTS["tier3"] * tier_scores[3]
    )

    detail = {
        "tier1": tier_scores[1],
        "tier2": tier_scores[2],
        "tier3": tier_scores[3],
        "matched_skills": matched_skills[:10],  # Top 10 for reasoning
    }

    return min(1.0, composite), detail
