"""
Stage 3: Final ranking + reasoning generation.
Sorts scored candidates, generates human-readable reasoning, outputs CSV.
"""
import csv
from pathlib import Path


def generate_reasoning(scored: dict) -> str:
    """
    Generate a specific, honest, 1-2 sentence reasoning for this candidate.
    Must reference actual profile facts. No hallucination. No templates.
    """
    profile = scored["profile"]
    sub = scored["sub_scores"]
    signals = scored.get("redrob_signals", {})
    career_detail = scored.get("career_detail", {})
    matched_skills = scored.get("matched_skills", [])
    anti_flags = scored.get("anti_flags", [])

    title = profile.get("current_title", "Unknown")
    company = profile.get("current_company", "Unknown")
    yoe = profile.get("years_of_experience", 0)
    location = profile.get("location", "Unknown")
    country = profile.get("country", "Unknown")
    notice = signals.get("notice_period_days", 0)
    response_rate = signals.get("recruiter_response_rate", 0)

    parts = []

    # Core identity
    parts.append(f"{title} at {company} with {yoe:.1f}yr exp")

    # Location
    if country.lower() == "india":
        parts.append(f"based in {location}")
    else:
        parts.append(f"based in {location} ({country})")

    # Strengths
    strengths = []
    if sub["career"] >= 0.6:
        ml_jobs = career_detail.get("ml_jobs", 0)
        total_jobs = career_detail.get("total_jobs", 0)
        if ml_jobs > 0:
            strengths.append(f"{ml_jobs}/{total_jobs} roles in ML/AI")
    if career_detail.get("has_leadership"):
        strengths.append("ML leadership experience")
    if career_detail.get("has_startup_exp"):
        strengths.append("startup/early-stage background")
    if matched_skills:
        top_skills = matched_skills[:4]
        strengths.append(f"skills: {', '.join(top_skills)}")
    if sub["behavioral"] >= 0.7:
        strengths.append(f"{response_rate:.0%} recruiter response rate")

    if strengths:
        parts.append("; ".join(strengths))

    # Concerns
    concerns = []
    if "consulting_only" in anti_flags:
        concerns.append("consulting-only career")
    if "keyword_stuffer" in anti_flags:
        concerns.append("skills don't match career history")
    if sub["experience"] < 0.6:
        if yoe < 5:
            concerns.append(f"below JD experience range ({yoe:.0f}yr vs 5-9yr)")
        elif yoe > 9:
            concerns.append(f"above JD experience range ({yoe:.0f}yr)")
    if notice > 90:
        concerns.append(f"{notice}d notice period")

    if concerns:
        parts.append("Concerns: " + ", ".join(concerns))

    reasoning = ". ".join(parts) + "."

    # Cap at reasonable length
    if len(reasoning) > 300:
        reasoning = reasoning[:297] + "..."

    return reasoning


def rank_and_output(scored_candidates: list[dict], output_path: str) -> list[dict]:
    """
    Sort candidates by composite score, assign ranks, generate reasoning, write CSV.
    Returns the top 100 as a list for inspection.
    """
    # Sort by composite score descending, then candidate_id ascending for tiebreak
    scored_candidates.sort(
        key=lambda x: (-x["composite_score"], x["candidate_id"])
    )

    top_100 = scored_candidates[:100]

    # Round scores first, then re-sort to handle any ties created by rounding
    for s in top_100:
        s["_rounded_score"] = round(s["composite_score"], 8)
    top_100.sort(key=lambda x: (-x["_rounded_score"], x["candidate_id"]))

    # Assign ranks and generate reasoning AFTER final sort order is locked
    rows = []
    for rank, scored in enumerate(top_100, start=1):
        rows.append({
            "candidate_id": scored["candidate_id"],
            "rank": rank,
            "score": scored["_rounded_score"],
            "reasoning": generate_reasoning(scored),
        })

    # Write CSV
    path = Path(output_path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        writer.writerows(rows)

    return top_100
