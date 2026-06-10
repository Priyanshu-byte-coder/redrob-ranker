"""
Stage 2: Multi-signal composite scorer.
Combines all 8 sub-scores into a final ranking score.
"""
from config import WEIGHTS
from pipeline.features.title_alignment import score_title_alignment
from pipeline.features.skills_match import score_skills_match
from pipeline.features.career_trajectory import score_career_trajectory
from pipeline.features.experience_fit import score_experience_fit
from pipeline.features.location_score import score_location
from pipeline.features.education_score import score_education
from pipeline.features.behavioral_signals import score_behavioral_signals
from pipeline.features.anti_patterns import score_anti_patterns


def score_candidate(candidate: dict) -> dict:
    """
    Score a single candidate across all dimensions.
    Returns a dict with composite score, sub-scores, and reasoning data.
    """
    # Individual scores
    title_score = score_title_alignment(candidate)
    skills_score, skills_detail = score_skills_match(candidate)
    career_score, career_detail = score_career_trajectory(candidate)
    exp_score = score_experience_fit(candidate)
    loc_score = score_location(candidate)
    edu_score = score_education(candidate)
    behavioral_score, behavioral_detail = score_behavioral_signals(candidate)
    anti_penalty, anti_flags = score_anti_patterns(candidate)

    # Weighted composite
    composite = (
        WEIGHTS["title_alignment"] * title_score
        + WEIGHTS["skills_match"] * skills_score
        + WEIGHTS["career_trajectory"] * career_score
        + WEIGHTS["experience_fit"] * exp_score
        + WEIGHTS["location"] * loc_score
        + WEIGHTS["education"] * edu_score
        + WEIGHTS["behavioral_signals"] * behavioral_score
        + WEIGHTS["anti_pattern"] * (1.0 - anti_penalty)
    )

    return {
        "candidate_id": candidate["candidate_id"],
        "composite_score": composite,  # Full precision — rounding happens at CSV output
        "sub_scores": {
            "title": round(title_score, 3),
            "skills": round(skills_score, 3),
            "career": round(career_score, 3),
            "experience": round(exp_score, 3),
            "location": round(loc_score, 3),
            "education": round(edu_score, 3),
            "behavioral": round(behavioral_score, 3),
            "anti_penalty": round(anti_penalty, 3),
        },
        "anti_flags": anti_flags,
        "matched_skills": skills_detail.get("matched_skills", []),
        "career_detail": career_detail,
        "profile": candidate.get("profile", {}),
        "redrob_signals": candidate.get("redrob_signals", {}),
    }
