"""
End-to-end tests for the ranking pipeline.
Uses sample_candidates.json as test data.
"""
import json
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.honeypot import detect_honeypot
from pipeline.coarse_filter import coarse_filter
from pipeline.scorer import score_candidate
from pipeline.features.title_alignment import score_title_alignment
from pipeline.features.skills_match import score_skills_match
from pipeline.features.experience_fit import score_experience_fit


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


if __name__ == "__main__":
    tests = [
        ("Honeypot Detection", test_honeypot_detection),
        ("Coarse Filter", test_coarse_filter),
        ("Title Scoring", test_title_scoring),
        ("Experience Fit", test_experience_fit),
        ("Full Pipeline", test_full_pipeline),
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
