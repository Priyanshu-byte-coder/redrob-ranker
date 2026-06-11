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
    How much to trust this skill claim based on proficiency + duration + endorsements.
    Expert with 0 months = likely keyword stuffer.
    Endorsements provide social validation boost.
    """
    prof = skill.get("proficiency", "beginner")
    duration = skill.get("duration_months", 0)
    endorsements = skill.get("endorsements", 0)

    if prof == "expert":
        if duration == 0:
            base = SKILL_TRUST_MULTIPLIERS["expert_zero_duration"]
        else:
            base = SKILL_TRUST_MULTIPLIERS["expert_with_duration"]
    elif prof == "advanced":
        if duration == 0:
            base = SKILL_TRUST_MULTIPLIERS["advanced_zero_duration"]
        else:
            base = SKILL_TRUST_MULTIPLIERS["advanced_with_duration"]
    elif prof == "intermediate":
        base = SKILL_TRUST_MULTIPLIERS["intermediate"]
    else:
        base = SKILL_TRUST_MULTIPLIERS["beginner"]

    # Endorsement boost — community validation strengthens trust
    if endorsements >= 10:
        base = min(1.0, base + 0.10)
    elif endorsements >= 5:
        base = min(1.0, base + 0.05)

    return base


def _assessment_boost(candidate: dict) -> tuple[float, int]:
    """
    Boost from Redrob platform skill_assessment_scores.
    Platform-validated scores are stronger evidence than self-reported proficiency.
    Returns (boost_value, count_of_assessed_relevant_skills).
    """
    signals = candidate.get("redrob_signals", {})
    assessments = signals.get("skill_assessment_scores", {})
    if not assessments:
        return 0.0, 0

    relevant_count = 0
    total_score = 0.0

    for skill_name, score in assessments.items():
        canonical = _resolve_skill_name(skill_name)
        tier = SKILL_TIER_LOOKUP.get(canonical)
        if tier is not None and score > 0:
            relevant_count += 1
            # Weight by tier importance and assessment score
            tier_weight = {1: 1.0, 2: 0.6, 3: 0.3}.get(tier, 0.3)
            total_score += tier_weight * (score / 100.0)

    if relevant_count == 0:
        return 0.0, 0

    # Average assessment quality, capped at 0.15 bonus
    avg = total_score / relevant_count
    boost = min(0.15, avg * 0.15 * min(relevant_count, 5) / 3)
    return boost, relevant_count


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

    # Platform assessment boost — validated skills are stronger than self-reported
    assess_boost, assess_count = _assessment_boost(candidate)
    composite += assess_boost

    detail = {
        "tier1": tier_scores[1],
        "tier2": tier_scores[2],
        "tier3": tier_scores[3],
        "matched_skills": matched_skills[:10],  # Top 10 for reasoning
        "assessment_boost": round(assess_boost, 3),
        "assessed_relevant_skills": assess_count,
    }

    return min(1.0, composite), detail
