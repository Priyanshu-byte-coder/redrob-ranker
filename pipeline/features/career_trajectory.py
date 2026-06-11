"""
Career Trajectory scorer.
THE key differentiator — analyzes career_history descriptions for actual ML work.
Catches "plain-language Tier 5s" and penalizes keyword stuffers.
"""
import re

from jd.taxonomy import (
    PRODUCTION_ML_KEYWORDS,
    ML_DOMAIN_KEYWORDS,
    CONSULTING_KEYWORDS,
    CONSULTING_COMPANIES,
    PRODUCT_COMPANIES,
    AI_INDUSTRIES,
    TECH_INDUSTRIES,
)

# Leadership signals — founding team needs people who can lead
LEADERSHIP_KEYWORDS = {
    "led", "lead", "managed", "built team", "hired",
    "mentored", "architected", "designed system",
    "technical lead", "tech lead", "team lead",
    "principal", "staff", "founding", "co-founded",
    "head of", "director of",
}

# Startup / early-stage signals — founding team fit
STARTUP_KEYWORDS = {
    "startup", "early-stage", "early stage", "seed",
    "series a", "founding", "co-founder", "first engineer",
    "0-to-1", "zero to one", "greenfield", "from scratch",
    "built from ground up", "mvp", "minimum viable",
}


def _count_keyword_hits(text: str, keywords: set) -> int:
    """Count how many distinct keywords appear in text (substring match)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def _analyze_descriptions(candidate: dict) -> dict:
    """Analyze all career_history descriptions + profile text for ML evidence."""
    career = candidate.get("career_history", [])
    profile = candidate.get("profile", {})

    all_text = ""
    ml_job_count = 0
    production_ml_job_count = 0
    total_jobs = len(career)
    recent_ml_months = 0
    consulting_job_count = 0
    product_company_count = 0
    has_leadership = False
    has_startup_exp = False
    ai_industry_jobs = 0
    small_company_jobs = 0

    # Check current industry and company size from profile
    current_industry = profile.get("current_industry", "").lower()
    if any(ind in current_industry for ind in AI_INDUSTRIES):
        ai_industry_jobs += 1  # Count current as well
    current_comp_size = profile.get("current_company_size", "")
    if current_comp_size in ("1-10", "11-50", "51-200"):
        small_company_jobs += 1
        has_startup_exp = True  # Small company = startup-like

    # Include profile headline and summary in ML keyword analysis
    headline = profile.get("headline", "")
    summary = profile.get("summary", "")
    profile_text = f"{headline} {summary}"
    all_text += " " + profile_text

    # Check headline/summary for leadership and startup signals
    if _count_keyword_hits(profile_text, LEADERSHIP_KEYWORDS) >= 1:
        has_leadership = True
    if _count_keyword_hits(profile_text, STARTUP_KEYWORDS) >= 1:
        has_startup_exp = True

    for job in career:
        desc = job.get("description", "")
        company = job.get("company", "").lower()
        title = job.get("title", "").lower()
        all_text += " " + desc

        ml_hits = _count_keyword_hits(desc, ML_DOMAIN_KEYWORDS)
        prod_hits = _count_keyword_hits(desc, PRODUCTION_ML_KEYWORDS)

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

        # Industry classification — AI/ML industries are strong signals
        industry = job.get("industry", "").lower()
        if any(ind in industry for ind in AI_INDUSTRIES):
            ai_industry_jobs += 1

        # Company size — small companies signal startup/founding-team fit
        comp_size = job.get("company_size", "")
        if comp_size in ("1-10", "11-50", "51-200"):
            small_company_jobs += 1

        # Leadership and startup signals (check desc + title)
        combined = (desc + " " + title).lower()
        if _count_keyword_hits(combined, LEADERSHIP_KEYWORDS) >= 1:
            has_leadership = True
        if _count_keyword_hits(combined, STARTUP_KEYWORDS) >= 1:
            has_startup_exp = True

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
        "has_leadership": has_leadership,
        "has_startup_exp": has_startup_exp,
        "ai_industry_jobs": ai_industry_jobs,
        "small_company_jobs": small_company_jobs,
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

    # Leadership + startup bonuses (founding team role values these)
    leadership_bonus = 0.06 if analysis["has_leadership"] else 0.0
    startup_bonus = 0.04 if analysis["has_startup_exp"] else 0.0

    # AI industry bonus — working in AI/ML industry is strong evidence
    ai_industry_bonus = min(0.05, analysis["ai_industry_jobs"] * 0.03)

    # Small company bonus — startup/founding team culture fit
    small_co_bonus = min(0.03, analysis["small_company_jobs"] * 0.02)

    # Composite
    score = (
        0.32 * ml_evidence
        + 0.23 * prod_score
        + 0.16 * product_score
        + 0.11 * progression_score
        + leadership_bonus
        + startup_bonus
        + ai_industry_bonus
        + small_co_bonus
    )

    detail = {
        "ml_evidence": ml_evidence,
        "production_score": prod_score,
        "product_company_score": product_score,
        "progression": progression_score,
        "ml_jobs": analysis["ml_job_count"],
        "total_jobs": analysis["total_jobs"],
        "has_leadership": analysis["has_leadership"],
        "has_startup_exp": analysis["has_startup_exp"],
        "ai_industry_jobs": analysis["ai_industry_jobs"],
    }

    return min(1.0, score), detail
