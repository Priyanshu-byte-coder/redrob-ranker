"""
Data exploration script: understand the 100K candidate pool distribution.
Run before building the ranker to inform design decisions.

Usage: python analysis/explore_data.py --candidates ./candidates.jsonl
"""
import json
import sys
import argparse
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def explore(candidates_path: str, limit: int = None):
    title_counts = Counter()
    industry_counts = Counter()
    country_counts = Counter()
    yoe_buckets = Counter()
    ai_skill_counts = Counter()
    company_size_counts = Counter()

    total = 0
    india_count = 0
    open_to_work = 0
    has_github = 0

    from jd.taxonomy import SKILL_TIER_LOOKUP, SKILL_ALIASES

    with open(candidates_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            total += 1
            if limit and total > limit:
                break

            p = c.get("profile", {})
            title_counts[p.get("current_title", "Unknown")] += 1
            industry_counts[p.get("current_industry", "Unknown")] += 1
            country = p.get("country", "Unknown")
            country_counts[country] += 1
            if country.lower() == "india":
                india_count += 1

            yoe = p.get("years_of_experience", 0)
            bucket = f"{int(yoe // 2) * 2}-{int(yoe // 2) * 2 + 1}yr"
            yoe_buckets[bucket] += 1

            company_size_counts[p.get("current_company_size", "?")] += 1

            signals = c.get("redrob_signals", {})
            if signals.get("open_to_work_flag"):
                open_to_work += 1
            if signals.get("github_activity_score", -1) >= 0:
                has_github += 1

            # Count AI skills
            ai_count = 0
            for skill in c.get("skills", []):
                name = skill.get("name", "").lower()
                canonical = SKILL_ALIASES.get(name, name)
                if canonical in SKILL_TIER_LOOKUP and SKILL_TIER_LOOKUP[canonical] <= 2:
                    ai_count += 1
            ai_skill_counts[min(ai_count, 10)] += 1

    print(f"\n{'='*60}")
    print(f"DATASET OVERVIEW ({total:,} candidates)")
    print(f"{'='*60}")

    print(f"\n--- Top 20 Titles ---")
    for title, count in title_counts.most_common(20):
        bar = "█" * (count // 500)
        print(f"  {title:<40} {count:>6,}  {bar}")

    print(f"\n--- Country Distribution (top 10) ---")
    for country, count in country_counts.most_common(10):
        pct = count / total * 100
        print(f"  {country:<25} {count:>6,}  ({pct:.1f}%)")

    print(f"\n--- India Stats ---")
    print(f"  India candidates: {india_count:,} / {total:,} ({india_count/total*100:.1f}%)")

    print(f"\n--- AI Skill Count Distribution ---")
    for k in sorted(ai_skill_counts):
        pct = ai_skill_counts[k] / total * 100
        bar = "█" * int(pct)
        print(f"  {k:>2} AI skills: {ai_skill_counts[k]:>7,}  {bar} ({pct:.1f}%)")

    print(f"\n--- Experience Buckets ---")
    for bucket in sorted(yoe_buckets):
        count = yoe_buckets[bucket]
        pct = count / total * 100
        print(f"  {bucket:<12} {count:>6,}  ({pct:.1f}%)")

    print(f"\n--- Behavioral ---")
    print(f"  Open to work:  {open_to_work:>7,} ({open_to_work/total*100:.1f}%)")
    print(f"  Has GitHub:    {has_github:>7,} ({has_github/total*100:.1f}%)")

    print(f"\n--- Top Industries ---")
    for ind, count in industry_counts.most_common(15):
        pct = count / total * 100
        print(f"  {ind:<40} {count:>6,}  ({pct:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    explore(args.candidates, args.limit)
