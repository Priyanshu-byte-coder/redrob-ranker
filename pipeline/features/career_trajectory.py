"""
Career Trajectory scorer.
THE key differentiator — analyzes career_history descriptions for actual ML work.
Catches "plain-language Tier 5s" and penalizes keyword stuffers.
"""
from jd.taxonomy import (
    PRODUCTION_ML_KEYWORDS,
    ML_DOMAIN_KEYWORDS,
    CONSULTING_KEYWORDS,
    CONSULTING_COMPANIES,
    PRODUCT_COMPANIES,
)


def _count_keyword_hits(text: str, keywords: set) -> int:
    """Count how many distinct keywords appear in text."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def _analyze_descriptions(candidate: dict) -> dict:
    """Analyze all career_history descriptions for ML evidence."""
    career = candidate.get("career_history", [])

    all_text = ""
    ml_job_count = 0
    production_ml_job_count = 0
    total_jobs = len(career)
    recent_ml_months = 0
    consulting_job_count = 0
    product_company_count = 0

    for job in career:
        desc = job.get("description", "")
        company = job.get("company", "").lower()
        all_text += " " + desc

        desc_lower = desc.lower()
        ml_hits = _count_keyword_hits(desc, ML_DOMAIN_KEYWORDS)
        prod_hits = _count_keyword_hits(desc, PRODUCTION_ML_KEYWORDS)
        consulting_hits = _count_keyword_hits(desc, CONSULTING_KEYWORDS)

        if ml_hits >= 2:
            ml_job_count += 1
            if job.get("is_current") or (job.get("duration_months", 0) > 0):
                recent_ml_months += job.get("duration_months", 0)

        if prod_hits >= 2:
            production_ml_job_count += 1

        # Company classification
        if company in CONSULTING_COMPANIES:
            consulting_job_count += 1
        if company in PRODUCT_COMPANIES:
            product_company_count += 1

    total_ml_keywords = _count_keyword_hits(all_text, ML_DOMAIN_KEYWORDS)
    total_prod_keywords = _count_keyword_hits(all_text, PRODUCTION_ML_KEYWORDS)

    return {
        "ml_job_count": ml_job_count,
        "production_ml_job_count": production_ml_job_count,
        "total_jobs": total_jobs,
        "total_ml_keywords": total_ml_keywords,
        "total_prod_keywords": total_prod_keywords,
        "recent_ml_months": recent_ml_months,
        "consulting_job_count": consulting_job_count,
        "product_company_count": product_company_count,
    }


def score_career_trajectory(candidate: dict) -> tuple[float, dict]:
    """
    Score career trajectory based on:
    1. ML work evidence in descriptions (0-0.40)
    2. Production ML evidence (0-0.25)
    3. Product company experience (0-0.20)
    4. Career progression toward ML (0-0.15)
    """
    analysis = _analyze_descriptions(candidate)

    # 1. ML work evidence (how many jobs involve ML)
    if analysis["total_jobs"] > 0:
        ml_ratio = analysis["ml_job_count"] / analysis["total_jobs"]
    else:
        ml_ratio = 0
    ml_evidence = min(1.0, ml_ratio * 1.5)  # Scale so 67%+ ML jobs = 1.0

    # Boost for high keyword density
    if analysis["total_ml_keywords"] >= 15:
        ml_evidence = min(1.0, ml_evidence + 0.2)
    elif analysis["total_ml_keywords"] >= 8:
        ml_evidence = min(1.0, ml_evidence + 0.1)

    # 2. Production ML evidence
    if analysis["production_ml_job_count"] >= 2:
        prod_score = 1.0
    elif analysis["production_ml_job_count"] == 1:
        prod_score = 0.7
    elif analysis["total_prod_keywords"] >= 3:
        prod_score = 0.4
    else:
        prod_score = 0.0

    # 3. Product company experience
    if analysis["product_company_count"] >= 2:
        product_score = 1.0
    elif analysis["product_company_count"] == 1:
        product_score = 0.7
    else:
        product_score = 0.2  # Unknown companies aren't necessarily bad

    # Penalty for all-consulting career
    if (analysis["consulting_job_count"] == analysis["total_jobs"]
            and analysis["total_jobs"] > 0):
        product_score = 0.0

    # 4. Career progression
    # Recent ML months as fraction of total career
    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience", 1)
    total_months = max(yoe * 12, 1)
    ml_career_fraction = min(1.0, analysis["recent_ml_months"] / total_months)
    progression_score = ml_career_fraction

    # Composite
    score = (
        0.40 * ml_evidence
        + 0.25 * prod_score
        + 0.20 * product_score
        + 0.15 * progression_score
    )

    detail = {
        "ml_evidence": ml_evidence,
        "production_score": prod_score,
        "product_company_score": product_score,
        "progression": progression_score,
        "ml_jobs": analysis["ml_job_count"],
        "total_jobs": analysis["total_jobs"],
    }

    return min(1.0, score), detail
