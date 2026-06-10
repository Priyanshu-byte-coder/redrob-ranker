#!/usr/bin/env python3
"""
Redrob Intelligent Candidate Discovery & Ranking System
Main entry point — produces a ranked CSV of top 100 candidates.

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv
"""
import argparse
import sys
import time
from pathlib import Path

from pipeline.loader import load_candidates
from pipeline.coarse_filter import coarse_filter
from pipeline.scorer import score_candidate
from pipeline.ranker import rank_and_output


def main():
    parser = argparse.ArgumentParser(
        description="Rank top 100 candidates for the Senior AI Engineer role"
    )
    parser.add_argument(
        "--candidates", required=True,
        help="Path to candidates.jsonl or candidates.jsonl.gz"
    )
    parser.add_argument(
        "--out", required=True,
        help="Output CSV path (e.g., submission.csv)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print detailed progress"
    )
    args = parser.parse_args()

    candidates_path = Path(args.candidates)
    if not candidates_path.exists():
        print(f"Error: {candidates_path} not found", file=sys.stderr)
        sys.exit(1)

    start_time = time.time()

    # === Stage 0+1: Stream through candidates, filter honeypots and non-fits ===
    if args.verbose:
        print("Stage 0+1: Loading and filtering candidates...")

    kept = []
    honeypot_ids = set()
    total = 0
    filtered = 0

    for candidate in load_candidates(str(candidates_path)):
        total += 1
        should_keep, is_honeypot, hp_reasons = coarse_filter(candidate)

        if is_honeypot:
            honeypot_ids.add(candidate["candidate_id"])

        if should_keep:
            kept.append(candidate)
        else:
            filtered += 1

        if args.verbose and total % 10000 == 0:
            elapsed = time.time() - start_time
            print(f"  Processed {total:,} candidates ({elapsed:.1f}s)")

    stage1_time = time.time() - start_time
    if args.verbose:
        print(f"  Done: {total:,} total, {len(kept):,} kept, "
              f"{filtered:,} filtered, {len(honeypot_ids)} honeypots "
              f"({stage1_time:.1f}s)")

    # === Stage 2: Score remaining candidates ===
    if args.verbose:
        print(f"Stage 2: Scoring {len(kept):,} candidates...")

    scored = []
    for candidate in kept:
        result = score_candidate(candidate)
        scored.append(result)

    stage2_time = time.time() - start_time - stage1_time
    if args.verbose:
        print(f"  Done scoring ({stage2_time:.1f}s)")

    # === Stage 3: Rank and output ===
    if args.verbose:
        print("Stage 3: Ranking and generating output...")

    top_100 = rank_and_output(scored, args.out)

    total_time = time.time() - start_time

    # Verify no honeypots in top 100
    honeypots_in_top = sum(
        1 for c in top_100 if c["candidate_id"] in honeypot_ids
    )

    print(f"\nResults:")
    print(f"  Total candidates: {total:,}")
    print(f"  After filtering:  {len(kept):,}")
    print(f"  Honeypots found:  {len(honeypot_ids)}")
    print(f"  Honeypots in top 100: {honeypots_in_top}")
    print(f"  Output: {args.out}")
    print(f"  Runtime: {total_time:.1f}s")

    if honeypots_in_top > 0:
        print(f"\n  WARNING: {honeypots_in_top} honeypots in top 100!")

    if args.verbose:
        print("\nTop 10 candidates:")
        for i, c in enumerate(top_100[:10], 1):
            profile = c["profile"]
            print(f"  {i}. {c['candidate_id']} — "
                  f"{profile.get('current_title', '?')} at "
                  f"{profile.get('current_company', '?')} "
                  f"({profile.get('years_of_experience', 0):.0f}yr) "
                  f"— score: {c['composite_score']:.4f}")

    # Validate format
    if Path(args.out).exists():
        print(f"\nValidate with: python validate_submission.py {args.out}")


if __name__ == "__main__":
    main()
