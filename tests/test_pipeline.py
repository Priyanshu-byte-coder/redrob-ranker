"""
End-to-end tests for the ranking pipeline.
Uses sample_candidates.json as test data.
"""
import json
import csv
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.honeypot import detect_honeypot
from pipeline.coarse_filter import coarse_filter
from pipeline.scorer import score_candidate
from pipeline.ranker import generate_reasoning, rank_and_output
from pipeline.features.title_alignment import score_title_alignment
from pipeline.features.skills_match import score_skills_match
from pipeline.features.experience_fit import score_experience_fit
from pipeline.features.anti_patterns import score_anti_patterns
from pipeline.features.career_trajectory import score_career_trajectory


def load_sample():
    sample_path = Path(__file__).parent.parent / "sample_candidates.json"
    return json.loads(sample_path.read_text(encoding="utf-8"))


def test_honeypot_detection():
    """Honeypot detector should not flag normal candidates."""
    candidates = load_sample()
    flagged = 0
    for c in candidates:
        is_hp, reasons = detect_honeypot(c)
        if is_hp:
            flagged += 1
    # Sample data should have very few honeypots (0-5)
    assert flagged <= 10, f"Too many honeypots in sample: {flagged}"
    print(f"  Honeypots in sample: {flagged}/50")


def test_coarse_filter():
    """Coarse filter should keep technical candidates."""
    candidates = load_sample()
    kept = 0
    for c in candidates:
        should_keep, _, _ = coarse_filter(c)
        if should_keep:
            kept += 1
    assert kept > 0, "Filter eliminated all candidates"
    print(f"  Kept after filter: {kept}/50")


def test_title_scoring():
    """ML titles should score higher than non-tech titles."""
    ml_candidate = {"profile": {"current_title": "ML Engineer"}, "career_history": []}
    hr_candidate = {"profile": {"current_title": "HR Manager"}, "career_history": []}

    ml_score = score_title_alignment(ml_candidate)
    hr_score = score_title_alignment(hr_candidate)

    assert ml_score > hr_score, f"ML ({ml_score}) should beat HR ({hr_score})"
    assert ml_score > 0.5
    assert hr_score < 0.1
    print(f"  ML Engineer: {ml_score:.3f}, HR Manager: {hr_score:.3f}")


def test_experience_fit():
    """7yr experience should score highest."""
    ideal = {"profile": {"years_of_experience": 7.0}}
    junior = {"profile": {"years_of_experience": 2.0}}
    senior = {"profile": {"years_of_experience": 15.0}}

    ideal_score = score_experience_fit(ideal)
    junior_score = score_experience_fit(junior)
    senior_score = score_experience_fit(senior)

    assert ideal_score > junior_score
    assert ideal_score > senior_score
    print(f"  7yr: {ideal_score:.3f}, 2yr: {junior_score:.3f}, 15yr: {senior_score:.3f}")


def test_full_pipeline():
    """Score all sample candidates and verify output format."""
    candidates = load_sample()
    scored = []
    for c in candidates:
        should_keep, _, _ = coarse_filter(c)
        if should_keep:
            result = score_candidate(c)
            scored.append(result)
            assert "composite_score" in result
            assert "sub_scores" in result
            assert 0 <= result["composite_score"] <= 1.0

    scored.sort(key=lambda x: -x["composite_score"])
    if scored:
        print(f"  Top candidate: {scored[0]['candidate_id']} "
              f"({scored[0]['profile'].get('current_title', '?')}) "
              f"score={scored[0]['composite_score']:.4f}")
    print(f"  Scored {len(scored)} candidates")


def test_tiebreak_correctness():
    """When two candidates have identical scores, lower candidate_id should rank first."""
    # Create two fake scored dicts with identical composite scores
    base = {
        "composite_score": 0.75,
        "sub_scores": {"title": 0.8, "skills": 0.7, "career": 0.6,
                       "experience": 0.9, "location": 0.8, "education": 0.5,
                       "behavioral": 0.7, "anti_penalty": 0.0},
        "anti_flags": [],
        "matched_skills": ["python", "pytorch"],
        "career_detail": {"ml_jobs": 2, "total_jobs": 3},
        "profile": {"current_title": "ML Engineer", "current_company": "TestCo",
                     "years_of_experience": 7.0, "location": "Bangalore", "country": "India"},
        "redrob_signals": {"notice_period_days": 30, "recruiter_response_rate": 0.8},
    }
    import copy
    c1 = copy.deepcopy(base)
    c1["candidate_id"] = "CAND_999"
    c2 = copy.deepcopy(base)
    c2["candidate_id"] = "CAND_001"

    import tempfile
    out = tempfile.mktemp(suffix=".csv")
    rank_and_output([c1, c2], out)

    with open(out, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert reader[0]["candidate_id"] == "CAND_001", f"Expected CAND_001 first, got {reader[0]['candidate_id']}"
    assert reader[1]["candidate_id"] == "CAND_999"
    assert int(reader[0]["rank"]) == 1
    assert int(reader[1]["rank"]) == 2
    os.unlink(out)
    print("  Tie-break ordering correct: CAND_001 before CAND_999")


def test_anti_pattern_consulting_only():
    """All-consulting career should be flagged."""
    candidate = {
        "profile": {"current_title": "Software Engineer"},
        "skills": [],
        "career_history": [
            {"company": "TCS", "title": "Developer", "description": "Java apps", "duration_months": 24},
            {"company": "Infosys", "title": "Senior Dev", "description": "Web apps", "duration_months": 36},
        ],
    }
    penalty, flags = score_anti_patterns(candidate)
    assert "consulting_only" in flags, f"Expected consulting_only flag, got {flags}"
    assert penalty >= 0.4
    print(f"  Consulting-only penalty: {penalty:.2f}, flags: {flags}")


def test_anti_pattern_keyword_stuffer():
    """Non-tech title with AI skills but no ML work in descriptions."""
    candidate = {
        "profile": {"current_title": "HR Manager"},
        "skills": [
            {"name": "Machine Learning", "proficiency": "expert", "duration_months": 0},
            {"name": "PyTorch", "proficiency": "advanced", "duration_months": 0},
            {"name": "Deep Learning", "proficiency": "expert", "duration_months": 0},
        ],
        "career_history": [
            {"company": "SomeCo", "title": "HR Manager", "description": "Managed recruitment process and employee relations"},
        ],
    }
    penalty, flags = score_anti_patterns(candidate)
    assert "keyword_stuffer" in flags, f"Expected keyword_stuffer, got {flags}"
    print(f"  Keyword stuffer penalty: {penalty:.2f}, flags: {flags}")


def test_career_trajectory_leadership_bonus():
    """Candidates with ML leadership experience should get a boost."""
    base_candidate = {
        "profile": {"current_title": "ML Engineer", "years_of_experience": 7.0},
        "skills": [],
        "career_history": [
            {"company": "TechCo", "title": "ML Engineer",
             "description": "Built recommendation system using deep learning and embeddings",
             "duration_months": 36, "is_current": True},
        ],
    }
    import copy
    leader = copy.deepcopy(base_candidate)
    leader["career_history"][0]["description"] += ". Led team of 5 ML engineers, architected the system."

    base_score, base_detail = score_career_trajectory(base_candidate)
    leader_score, leader_detail = score_career_trajectory(leader)

    assert leader_score >= base_score, f"Leader ({leader_score}) should score >= base ({base_score})"
    assert leader_detail["has_leadership"] is True
    print(f"  Base trajectory: {base_score:.3f}, With leadership: {leader_score:.3f}")


def test_reasoning_has_content():
    """Reasoning should contain actual profile data, not be empty."""
    candidates = load_sample()
    for c in candidates[:5]:
        should_keep, _, _ = coarse_filter(c)
        if should_keep:
            scored = score_candidate(c)
            reasoning = generate_reasoning(scored)
            assert len(reasoning) > 20, f"Reasoning too short: {reasoning}"
            assert scored["profile"].get("current_title", "X") in reasoning or "Unknown" in reasoning
            break
    print("  Reasoning contains profile data")


if __name__ == "__main__":
    tests = [
        ("Honeypot Detection", test_honeypot_detection),
        ("Coarse Filter", test_coarse_filter),
        ("Title Scoring", test_title_scoring),
        ("Experience Fit", test_experience_fit),
        ("Full Pipeline", test_full_pipeline),
        ("Tie-Break Correctness", test_tiebreak_correctness),
        ("Anti-Pattern: Consulting Only", test_anti_pattern_consulting_only),
        ("Anti-Pattern: Keyword Stuffer", test_anti_pattern_keyword_stuffer),
        ("Career Trajectory: Leadership Bonus", test_career_trajectory_leadership_bonus),
        ("Reasoning Quality", test_reasoning_has_content),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            print(f"Running: {name}")
            test_fn()
            print(f"  PASSED")
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(1 if failed > 0 else 0)
