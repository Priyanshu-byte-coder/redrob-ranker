"""
Title Alignment scorer.
Maps current_title (and career history titles) to JD fit.
"""
from jd.taxonomy import TITLE_SCORES


def _normalize_title(title: str) -> str:
    """Normalize title for lookup."""
    return title.strip()


def _get_title_score(title: str) -> float:
    """Get score for a single title. Falls back to partial matching."""
    normalized = _normalize_title(title)

    # Direct lookup
    if normalized in TITLE_SCORES:
        return TITLE_SCORES[normalized]

    # Case-insensitive lookup
    lower = normalized.lower()
    for known_title, score in TITLE_SCORES.items():
        if known_title.lower() == lower:
            return score

    # Partial keyword matching for unknown titles
    lower_title = lower
    if any(kw in lower_title for kw in ("ai engineer", "ml engineer", "machine learning")):
        return 0.85
    if any(kw in lower_title for kw in ("data scientist", "applied scientist")):
        return 0.75
    if any(kw in lower_title for kw in ("nlp", "search engineer", "recommendation")):
        return 0.80
    if any(kw in lower_title for kw in ("software engineer", "developer", "backend")):
        return 0.35
    if any(kw in lower_title for kw in ("data engineer", "analytics")):
        return 0.40
    if any(kw in lower_title for kw in ("devops", "cloud", "infrastructure")):
        return 0.20
    if any(kw in lower_title for kw in ("manager", "lead", "director", "vp", "head")):
        if any(kw in lower_title for kw in ("ai", "ml", "machine learning", "data science")):
            return 0.70
        return 0.10
    if any(kw in lower_title for kw in ("intern", "trainee", "fresher")):
        return 0.05

    return 0.15  # Unknown title default


def _headline_boost(headline: str) -> float:
    """Boost from profile headline if it signals AI/ML focus."""
    lower = headline.lower()
    if any(kw in lower for kw in ("ai engineer", "ml engineer", "machine learning engineer")):
        return 0.10
    if any(kw in lower for kw in ("nlp", "deep learning", "artificial intelligence",
                                   "computer vision", "data scientist")):
        return 0.07
    if any(kw in lower for kw in ("founding", "staff", "principal", "lead ai", "lead ml")):
        return 0.05
    return 0.0


def score_title_alignment(candidate: dict) -> float:
    """
    Score based on current title + career trajectory titles + headline signal.
    Current title gets 65% weight, trajectory 25%, headline 10%.
    """
    profile = candidate.get("profile", {})
    current_title = profile.get("current_title", "")
    headline = profile.get("headline", "")

    current_score = _get_title_score(current_title)

    # Check career history for progression toward ML/AI
    career = candidate.get("career_history", [])
    best_historical = 0.0
    for job in career:
        if not job.get("is_current", False):
            title_score = _get_title_score(job.get("title", ""))
            best_historical = max(best_historical, title_score)

    # If career history shows ML progression, boost
    trajectory_score = max(current_score, best_historical * 0.8)

    # Headline provides additional signal about self-identified role
    h_boost = _headline_boost(headline)

    final = 0.65 * current_score + 0.25 * trajectory_score + h_boost
    return min(1.0, final)
