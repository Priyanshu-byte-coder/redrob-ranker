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

A multi-signal candidate ranking system for the **Senior AI Engineer — Founding Team** role at Redrob AI. Built for the India Runs Hackathon 2026 (Data & AI Challenge).

## Architecture

The system uses a **4-stage funnel pipeline** that processes 100K candidates in ~50 seconds on CPU:

```
100K candidates
    │
    ▼
Stage 0: Honeypot Detection (~80 impossible profiles flagged)
    │
    ▼
Stage 1: Coarse Filter (100K → ~4K)
    │  - Eliminate non-technical titles with no AI work
    │  - Detect keyword stuffers
    │  - Filter <2yr experience
    ▼
Stage 2: Multi-Signal Scoring (~4K → scored list)
    │  8 weighted sub-scores
    ▼
Stage 3: Final Ranking + Reasoning (top 100 CSV)
```

### Why Rule-Based Over Embeddings?

The JD explicitly warns that keyword/embedding matching is a trap. A Marketing Manager with all AI keywords is NOT a fit. A Backend Engineer who built a recommendation system at a product company IS a fit.

Our system reads career trajectories, detects anti-patterns, and evaluates behavioral signals — things embeddings miss entirely.

### 8 Scoring Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Title Alignment | 20% | How well current_title maps to "Senior AI Engineer" |
| Skills Match | 20% | 3-tier skill taxonomy with trust multiplier |
| Career Trajectory | 20% | Description text analysis for production ML evidence |
| Experience Fit | 10% | Bell curve centered at 7yr (JD range: 5-9yr) |
| Location | 8% | Pune/Noida preferred, Tier-1 India acceptable |
| Education | 5% | CS/AI field relevance + institution tier |
| Behavioral Signals | 10% | Notice period, response rate, activity, GitHub |
| Anti-Pattern Penalty | 7% | Consulting-only, keyword stuffer, title chaser |

### Honeypot Detection

Identifies ~80 impossible profiles using 6 rules:
- Expert proficiency + 0 months duration
- Career duration exceeding date arithmetic
- Future dates in career history
- Skill count vs experience impossibility
- "Too perfect" behavioral signals

### Anti-Pattern Detection

Directly from the JD's disqualifiers:
- **Consulting-only career** (TCS, Infosys, Wipro, etc.)
- **Keyword stuffers** (AI skills listed but zero ML in job descriptions)
- **Title chasers** (rapid title inflation via short stints)
- **CV-only** (Computer Vision without NLP/IR exposure)

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

Add `--verbose` for detailed progress:

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv --verbose
```

### Validate Submission

```bash
python validate_submission.py submission.csv
```

### Run Sandbox App

```bash
streamlit run app.py
```

## Performance

| Metric | Value |
|--------|-------|
| Total Runtime | ~50 seconds |
| Memory Usage | <2 GB |
| Candidates Processed | 100,000 |
| After Filtering | ~40,000 |
| Honeypots Detected | ~67 |
| Honeypots in Top 100 | 0 |

## Project Structure

```
redrob-ranker/
├── rank.py                    # CLI entry point
├── config.py                  # All weights and thresholds
├── pipeline/
│   ├── loader.py              # Streaming JSONL reader
│   ├── honeypot.py            # Impossible profile detection
│   ├── coarse_filter.py       # Fast elimination
│   ├── scorer.py              # Multi-signal composite scoring
│   ├── ranker.py              # Final ranking + reasoning
│   └── features/
│       ├── title_alignment.py
│       ├── skills_match.py
│       ├── career_trajectory.py
│       ├── experience_fit.py
│       ├── location_score.py
│       ├── education_score.py
│       ├── behavioral_signals.py
│       └── anti_patterns.py
├── jd/
│   ├── requirements.py        # Structured JD representation
│   └── taxonomy.py            # Title hierarchy, skill taxonomy
├── app.py                     # Streamlit sandbox
├── requirements.txt
└── submission_metadata.yaml
```

## Methodology

### Design Philosophy

1. **Read between the lines.** The JD says "find candidates whose skills section contains the most AI keywords" is the wrong answer. We built a system that understands career trajectories.

2. **Trust but verify.** Skills with "expert" proficiency and 0 months duration get 0.3x credit. Skills backed by experience and endorsements get full credit.

3. **Availability matters.** A perfect-on-paper candidate who hasn't logged in for 6 months with a 5% response rate is not actually available. Behavioral signals serve as an availability multiplier.

4. **Product > consulting.** The JD explicitly penalizes consulting-only careers. Our system checks company classification across the full career history.

### Key Differentiators

- **No LLM API calls** — pure rule-based scoring, runs entirely on CPU
- **Career description analysis** catches "plain-language Tier 5s" who describe building search/recommendation systems without buzzwords
- **Honeypot detection** ensures 0 impossible profiles in the top 100
- **Specific, honest reasoning** that references actual profile data for each ranked candidate

## AI Tools Declaration

- **Claude** — Architecture discussion, code review, iterative development
- **Claude Code** — Development environment

No candidate data was fed to any LLM during the ranking process. The ranking system uses no AI inference — it's purely rule-based scoring with hand-crafted features.
