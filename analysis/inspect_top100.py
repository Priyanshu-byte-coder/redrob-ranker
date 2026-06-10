"""
Inspect and validate the top 100 ranked candidates.
Use this after running rank.py to sanity-check the results.

Usage: python analysis/inspect_top100.py --submission submission.csv --candidates candidates.jsonl
"""
import csv
import json
import sys
import argparse
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.honeypot import detect_honeypot
from jd.taxonomy import CONSULTING_COMPANIES, NON_TECHNICAL_TITLES


def load_top100(csv_path: str) -> list[dict]:
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_candidate_by_id(jsonl_path: str, target_ids: set) -> dict:
    """Load specific candidates by ID from JSONL."""
    found = {}
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            if c["candidate_id"] in target_ids:
                found[c["candidate_id"]] = c
            if len(found) == len(target_ids):
                break
    return found


def inspect(submission_path: str, candidates_path: str):
    top100 = load_top100(submission_path)
    target_ids = {row["candidate_id"] for row in top100}

    print(f"Loading {len(target_ids)} candidates from {candidates_path}...")
    candidates = load_candidate_by_id(candidates_path, target_ids)

    print(f"\n{'='*70}")
    print(f"TOP 100 ANALYSIS")
    print(f"{'='*70}")

    title_dist = Counter()
    company_dist = Counter()
    yoe_values = []
    honeypot_count = 0
    consulting_count = 0
    non_tech_count = 0
    india_count = 0
    location_dist = Counter()

    issues = []

    for row in top100:
        cid = row["candidate_id"]
        rank = int(row["rank"])
        score = float(row["score"])
        c = candidates.get(cid)
        if not c:
            issues.append(f"Rank {rank}: {cid} not found in JSONL")
            continue

        profile = c.get("profile", {})
        title = profile.get("current_title", "?")
        company = profile.get("current_company", "?")
        yoe = profile.get("years_of_experience", 0)
        country = profile.get("country", "?")
        location = profile.get("location", "?")

        title_dist[title] += 1
        company_dist[company] += 1
        yoe_values.append(yoe)

        if country.lower() == "india":
            india_count += 1
            location_dist[location.split(",")[0].strip()] += 1

        # Check for honeypots
        is_hp, reasons = detect_honeypot(c)
        if is_hp:
            honeypot_count += 1
            issues.append(f"Rank {rank}: {cid} is HONEYPOT — {'; '.join(reasons)}")

        # Check for consulting-only
        career = c.get("career_history", [])
        if career and all(j.get("company", "").lower() in CONSULTING_COMPANIES for j in career):
            consulting_count += 1
            issues.append(f"Rank {rank}: {cid} is CONSULTING-ONLY career")

        # Check for non-tech title
        if title in NON_TECHNICAL_TITLES:
            non_tech_count += 1
            issues.append(f"Rank {rank}: {cid} has non-tech title '{title}'")

    # Print top 20
    print(f"\n{'Rank':<6} {'Score':<10} {'Title':<40} {'Company':<25} {'YoE'}")
    print("-" * 100)
    for row in top100[:20]:
        cid = row["candidate_id"]
        c = candidates.get(cid, {})
        profile = c.get("profile", {}) if c else {}
        title = profile.get("current_title", "?")[:39]
        company = profile.get("current_company", "?")[:24]
        yoe = profile.get("years_of_experience", 0)
        print(f"#{row['rank']:<5} {float(row['score']):<10.4f} {title:<40} {company:<25} {yoe:.1f}yr")

    print(f"\n--- Score Distribution ---")
    scores = [float(r["score"]) for r in top100]
    print(f"  Min score (rank 100): {min(scores):.4f}")
    print(f"  Max score (rank 1):   {max(scores):.4f}")
    print(f"  Mean score:           {sum(scores)/len(scores):.4f}")

    print(f"\n--- Title Distribution (top 100) ---")
    for title, count in title_dist.most_common(15):
        print(f"  {title:<45} {count:>3}")

    print(f"\n--- Experience Distribution ---")
    if yoe_values:
        avg_yoe = sum(yoe_values) / len(yoe_values)
        in_range = sum(1 for y in yoe_values if 5 <= y <= 9)
        print(f"  Average: {avg_yoe:.1f}yr")
        print(f"  In JD range (5-9yr): {in_range}/100")

    print(f"\n--- Geography ---")
    print(f"  India-based: {india_count}/100")
    print(f"  Top Indian cities:")
    for city, count in location_dist.most_common(5):
        print(f"    {city}: {count}")

    print(f"\n--- Quality Checks ---")
    print(f"  Honeypots in top 100: {honeypot_count}")
    print(f"  Consulting-only careers: {consulting_count}")
    print(f"  Non-tech titles: {non_tech_count}")

    if issues:
        print(f"\n--- Issues Found ---")
        for issue in issues:
            print(f"  ⚠ {issue}")
    else:
        print(f"\n  [OK] No issues found!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", default="submission.csv")
    parser.add_argument("--candidates", required=True)
    args = parser.parse_args()
    inspect(args.submission, args.candidates)
