"""
Streaming JSONL loader for candidate data.
Handles both plain .jsonl and gzipped .jsonl.gz files.
"""
import gzip
import json
from pathlib import Path
from typing import Iterator


def load_candidates(path: str) -> Iterator[dict]:
    """Yield candidate dicts one at a time from JSONL file."""
    p = Path(path)

    if p.suffix == ".gz":
        opener = lambda: gzip.open(p, "rt", encoding="utf-8")
    else:
        opener = lambda: open(p, "r", encoding="utf-8")

    with opener() as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_candidates_list(path: str) -> list[dict]:
    """Load all candidates into memory as a list."""
    return list(load_candidates(path))


def count_candidates(path: str) -> int:
    """Count total lines in JSONL file without loading into memory."""
    p = Path(path)
    count = 0
    if p.suffix == ".gz":
        opener = lambda: gzip.open(p, "rt", encoding="utf-8")
    else:
        opener = lambda: open(p, "r", encoding="utf-8")

    with opener() as f:
        for line in f:
            if line.strip():
                count += 1
    return count
