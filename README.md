---
title: Redrob Intelligent Candidate Ranker
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
python_version: "3.11"
pinned: false
license: mit
---

# Redrob Intelligent Candidate Discovery & Ranking System

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CPU Only](https://img.shields.io/badge/compute-CPU%20only-orange.svg)](#)
[![Runtime](https://img.shields.io/badge/runtime-~65s%20for%20100K-brightgreen.svg)](#performance)

> **[Live Demo on HuggingFace Spaces](https://huggingface.co/spaces/bladebutcher/redrob-ranker)**

A multi-signal candidate ranking system for the **Senior AI Engineer — Founding Team** role at Redrob AI. Built for the India Runs Hackathon 2026 (Data & AI Challenge).

---

## Architecture

The system uses a **4-stage funnel pipeline** that processes 100K candidates in ~65 seconds on CPU, leveraging **21/22 Redrob behavioral signals** + profile text analysis:

```
100K candidates
    │
    ▼
Stage 0: Honeypot Detection ──────── ~80 impossible profiles flagged
    │
    ▼
Stage 1: Coarse Filter ───────────── 100K → ~40K
    │  ├─ Eliminate non-technical titles with no AI work
    │  ├─ Detect keyword stuffers (AI skills ≠ ML career)
    │  └─ Filter <2yr experience
    ▼
Stage 2: Multi-Signal Scoring ────── ~40K → scored list
    │  8 weighted sub-scores
    ▼
Stage 3: Final Ranking + Reasoning ─ top 100 CSV with per-candidate explanations
```

### Why Rule-Based Over Embeddings?

The JD explicitly warns: *"find candidates whose skills section contains the most AI keywords"* is the **wrong answer**.

- A Marketing Manager with all AI keywords is **NOT** a fit
- A Backend Engineer who built a recommendation system at a product company **IS** a fit
- A "Senior AI Engineer" at TCS with only consulting projects is a **weak** fit

Embedding similarity treats all keywords equally. Our system reads **career trajectories**, detects **anti-patterns**, and evaluates **behavioral signals** — things embeddings miss entirely.

| Approach | Handles Keyword Stuffers | Reads Career Context | Detects Honeypots | Production Evidence |
|----------|:------------------------:|:-------------------:|:-----------------:|:-------------------:|
| Keyword Matching | ✗ | ✗ | ✗ | ✗ |
| Embedding Similarity | ✗ | Partial | ✗ | ✗ |
| **Our Rule-Based Pipeline** | **✓** | **✓** | **✓** | **✓** |

### 8 Scoring Dimensions

| Dimension | Weight | What It Measures |
|-----------|-------:|-----------------|
| Title Alignment | 20% | How well current_title maps to "Senior AI Engineer" (62 titles scored) |
| Skills Match | 20% | 3-tier taxonomy + trust multiplier + platform assessment boost (178 skills) |
| Career Trajectory | 20% | Description + headline/summary analysis for production ML + leadership |
| Experience Fit | 10% | Bell curve centered at 7yr (JD range: 5-9yr) |
| Behavioral Signals | 10% | 16 components from 21/22 Redrob signals (notice, response, recency, market demand, etc.) |
| Location | 8% | Pune/Noida preferred, Tier-1 India acceptable |
| Anti-Pattern Penalty | 7% | Consulting-only, keyword stuffer, title chaser, CV-only |
| Education | 5% | CS/AI field relevance + institution tier + ML certification bonus |

### Honeypot Detection

Identifies ~80 impossible profiles using 6 rules:
1. Expert proficiency + 0 months actual experience (≥3 skills = flag)
2. Claimed job duration exceeds calendar date arithmetic
3. Total career duration exceeds stated years_of_experience
4. Future dates in career history
5. Impossible skill count vs experience ratio
6. Synthetically perfect behavioral signals (all rates = 1.0)

### Anti-Pattern Detection

Directly from the JD's disqualifiers:

| Anti-Pattern | Penalty | Detection Logic |
|-------------|--------:|-----------------|
| Keyword Stuffer | -0.80 | Non-tech title + AI skills + 0 ML in descriptions |
| Consulting Only | -0.50 | All career at TCS/Infosys/Wipro/etc. (54 companies tracked) |
| Title Chaser | -0.20 | ≥70% short stints (<18mo) with ≥3 past jobs |
| CV Only | -0.15 | 3+ CV keywords, 0 NLP/IR exposure in skills or descriptions |

### Trust Multiplier

Skills are not all equal:
- Expert proficiency + 0 months duration → **0.3x** credit (likely keyword stuffing)
- Expert + endorsed + years of use → **full credit**
- This alone eliminates most "fake expert" profiles from the top

---

## Quick Start

### Requirements

- Python 3.10+
- No GPU required
- No internet during ranking

### Installation

```bash
pip install -r requirements.txt
```

### Run Ranking

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

With verbose progress:

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv --verbose
```

### Validate Submission

```bash
python validate_submission.py submission.csv
```

### Run Sandbox App

```bash
python app.py
```

---

## Performance

| Metric | Value |
|--------|-------|
| Total Runtime | ~65 seconds |
| Memory Usage | <2 GB |
| Candidates Processed | 100,000 |
| After Filtering | ~40,000 |
| Honeypots Detected | ~67 |
| Honeypots in Top 100 | **0** |

---

## Project Structure

```
redrob-ranker/
├── rank.py                    # CLI entry point
├── config.py                  # All weights and thresholds
├── pipeline/
│   ├── loader.py              # Streaming JSONL reader
│   ├── honeypot.py            # Impossible profile detection (6 rules)
│   ├── coarse_filter.py       # Fast elimination (100K → ~40K)
│   ├── scorer.py              # Multi-signal composite scoring
│   ├── ranker.py              # Final ranking + per-candidate reasoning
│   └── features/
│       ├── title_alignment.py # 62 titles scored, current + historical
│       ├── skills_match.py    # 178 skills, 3 tiers, trust multiplier
│       ├── career_trajectory.py # THE differentiator — description analysis
│       ├── experience_fit.py  # Bell curve, 5-9yr sweet spot
│       ├── location_score.py  # India tier-based scoring
│       ├── education_score.py # Field + institution + degree level
│       ├── behavioral_signals.py # 16-component availability score (21/22 signals)
│       └── anti_patterns.py   # 4 detectors, additive penalties
├── jd/
│   ├── requirements.py        # Structured JD representation
│   └── taxonomy.py            # Title hierarchy, skill taxonomy, company lists
├── app.py                     # Gradio sandbox (live on HuggingFace)
├── tests/
│   └── test_pipeline.py       # 10 tests covering all components
├── analysis/
│   ├── explore_data.py        # Dataset distribution analysis
│   └── inspect_top100.py      # Top 100 quality validation
├── validate_submission.py     # Submission format validator
├── sample_candidates.json     # 50 sample candidates for testing
├── submission_metadata.yaml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Design Philosophy

1. **Read between the lines.** The JD says keyword matching is wrong. We built a system that understands career trajectories — what someone actually *did*, not what they *claim*.

2. **Trust but verify.** Skills with "expert" proficiency and 0 months duration get 0.3x credit. Skills backed by experience and endorsements get full credit.

3. **Availability matters.** A perfect-on-paper candidate who hasn't logged in for 6 months with a 5% response rate is not actually available. We use 18/22 Redrob platform signals — including market demand (saved by recruiters), engagement speed, and offer acceptance history.

4. **Product > consulting.** The JD explicitly penalizes consulting-only careers. We track 54 consulting companies and 38+ product companies (including Indian AI startups like Sarvam AI, Haptik, Yellow.ai).

5. **Founding team fit.** Leadership experience and startup background get explicit bonuses — this role needs someone who can build, not just execute.

---

## AI Tools Declaration

- **Claude** — Architecture discussion, code review, iterative development
- **Claude Code** — Development environment

No candidate data was fed to any LLM during ranking. The system uses **no AI inference** — it's purely rule-based scoring with hand-crafted features.
