"""
Anti-Pattern detector.
Identifies and penalizes JD-specified anti-patterns:
- Consulting-only career
- Keyword stuffers (AI skills but non-tech career)
- Title chasers
- Pure CV/robotics without NLP/IR
"""
from jd.taxonomy import (
    CONSULTING_COMPANIES,
    NON_TECHNICAL_TITLES,
    ML_DOMAIN_KEYWORDS,
    SKILL_TIER_LOOKUP,
    SKILL_ALIASES,
)


def _is_consulting_only(candidate: dict) -> bool:
    """All career at consulting companies."""
    career = candidate.get("career_history", [])
    if not career:
        return False
    return all(
        job.get("company", "").lower() in CONSULTING_COMPANIES
        for job in career
    )


def _is_keyword_stuffer(candidate: dict) -> bool:
    """
    Non-tech title but lots of AI skills listed.
    The critical check: do descriptions actually mention ML work?
    """
    title = candidate.get("profile", {}).get("current_title", "")
    if title not in NON_TECHNICAL_TITLES:
        return False

    # Count AI-related skills
    ai_skill_count = 0
    for skill in candidate.get("skills", []):
        name = skill.get("name", "").lower()
        canonical = SKILL_ALIASES.get(name, name)
        if canonical in SKILL_TIER_LOOKUP and SKILL_TIER_LOOKUP[canonical] <= 2:
            ai_skill_count += 1

    if ai_skill_count < 3:
        return False

    # Check if descriptions actually have ML work
    has_ml_work = False
    for job in candidate.get("career_history", []):
        desc = job.get("description", "").lower()
        ml_hits = sum(1 for kw in ML_DOMAIN_KEYWORDS if kw in desc)
        if ml_hits >= 3:
            has_ml_work = True
            break

    return not has_ml_work


def _is_cv_only(candidate: dict) -> bool:
    """Primary expertise is Computer Vision without NLP/IR exposure."""
    skills = candidate.get("skills", [])
    cv_keywords = {"computer vision", "opencv", "image classification",
                   "object detection", "image segmentation", "yolo",
                   "cnn", "convolutional neural network"}
    nlp_ir_keywords = {"nlp", "natural language processing", "information retrieval",
                       "search", "retrieval", "text", "embedding", "semantic",
                       "transformers", "bert", "gpt", "llm"}

    cv_count = 0
    nlp_count = 0
    for skill in skills:
        name = skill.get("name", "").lower()
        if any(kw in name for kw in cv_keywords):
            cv_count += 1
        if any(kw in name for kw in nlp_ir_keywords):
            nlp_count += 1

    # Also check career descriptions
    for job in candidate.get("career_history", []):
        desc = job.get("description", "").lower()
        if any(kw in desc for kw in nlp_ir_keywords):
            nlp_count += 1

    return cv_count >= 3 and nlp_count == 0


def _is_title_chaser(candidate: dict) -> bool:
    """
    Rapid title inflation: many short stints with escalating titles.
    JD says: "optimizing for title jumps every 1.5 years."
    """
    career = candidate.get("career_history", [])
    if len(career) < 3:
        return False

    short_stints = sum(
        1 for job in career
        if job.get("duration_months", 0) < 18 and not job.get("is_current", False)
    )
    non_current = sum(1 for job in career if not job.get("is_current", False))

    if non_current == 0:
        return False

    return short_stints / non_current >= 0.7 and non_current >= 3


def score_anti_patterns(candidate: dict) -> tuple[float, list[str]]:
    """
    Returns (penalty, list_of_flags).
    Penalty is 0.0 (no issues) to 1.0 (severe anti-pattern).
    """
    flags = []
    penalty = 0.0

    if _is_keyword_stuffer(candidate):
        flags.append("keyword_stuffer")
        penalty += 0.8

    if _is_consulting_only(candidate):
        flags.append("consulting_only")
        penalty += 0.5

    if _is_cv_only(candidate):
        flags.append("cv_only_no_nlp")
        penalty += 0.15

    if _is_title_chaser(candidate):
        flags.append("title_chaser")
        penalty += 0.2

    return min(1.0, penalty), flags
