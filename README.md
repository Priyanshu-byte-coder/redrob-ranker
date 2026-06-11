---
title: Redrob Intelligent Candidate Ranker
emoji: "\U0001F3AF"
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
python_version: "3.11"
pinned: false
license: mit
---

<div align="center">

# Redrob Intelligent Candidate Discovery & Ranking

**A multi-signal ranking system that finds the best Senior AI Engineers from 100,000 candidates in 25 seconds**

[![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CPU Only](https://img.shields.io/badge/compute-CPU%20only-orange.svg)](#performance)
[![Runtime](https://img.shields.io/badge/runtime-25s%20%2F%20100K-brightgreen.svg)](#performance)
[![Signals](https://img.shields.io/badge/Redrob%20signals-22%2F22-blueviolet)](#behavioral-signals)
[![Honeypots](https://img.shields.io/badge/honeypots%20in%20top%20100-0-red)](#honeypot-detection)

[Live Demo](https://huggingface.co/spaces/bladebutcher/redrob-ranker) | [Submission CSV](submission.csv) | [Methodology](#how-it-works)

</div>

---

## The Problem

Given 100,000 candidate profiles with rich structured data (skills, career history, behavioral signals, education), rank the **top 100** best fits for a **Senior AI Engineer — Founding Team** position at a product company.

The catch: the dataset contains honeypot profiles (impossible candidates designed to fool naive rankers), keyword stuffers (non-technical people listing AI skills), and consulting-only careers that look impressive on paper but don't match the founding-team requirement.

**Naive keyword matching is explicitly the wrong answer.** The JD says so.

---

## Results at a Glance

| Metric | Value |
|--------|------:|
| Candidates processed | 100,000 |
| After coarse filter | 40,789 |
| Honeypots detected | 67 |
| **Honeypots in top 100** | **0** |
| Runtime | **25.2 seconds** |
| Memory | < 2 GB |
| GPU required | No |
| LLM API calls | 0 |
| Network during ranking | None |

**Top 5 candidates:**

| Rank | Candidate | Title | Company | Exp | Key Signal |
|:----:|-----------|-------|---------|:---:|------------|
| 1 | CAND_0071974 | Senior AI Engineer | Netflix | 7.8yr | 3/3 ML roles, leadership, LoRA + L2R |
| 2 | CAND_0018499 | Senior ML Engineer | Zomato | 7.2yr | 3/3 ML roles, Noida, RecSys + DL |
| 3 | CAND_0002025 | Senior AI Engineer | Apple | 5.9yr | 2/2 ML roles, FAISS + TensorFlow |
| 4 | CAND_0081846 | Lead AI Engineer | Razorpay | 6.7yr | IR + LlamaIndex + pgvector |
| 5 | CAND_0033861 | Senior NLP Engineer | Mad Street Den | 8.0yr | 3/3 ML, Indian AI startup |

Every candidate in the top 10 is a genuine AI/ML engineer at a product company, in the 5-9 year experience sweet spot, with production ML evidence in their career descriptions.

---

## How It Works

### 4-Stage Pipeline

```
                    ┌─────────────────────────────────────┐
                    │         100,000 candidates           │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
    Stage 0         │     Honeypot Detection (6 rules)     │──── 67 impossible
                    │  date arithmetic, skill impossibility │     profiles flagged
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
    Stage 1         │       Coarse Filter                  │──── 59,211 eliminated
                    │  title + description + experience    │     (non-tech, <2yr exp)
                    └──────────────┬──────────────────────┘
                                   │  40,789 candidates
                    ┌──────────────▼──────────────────────┐
    Stage 2         │     Multi-Signal Scoring             │
                    │  8 weighted dimensions per candidate  │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
    Stage 3         │    Rank + Reasoning Generation       │──── submission.csv
                    │  sort, tiebreak, per-candidate text   │     (top 100)
                    └─────────────────────────────────────┘
```

### 8 Scoring Dimensions

| Dimension | Weight | What It Measures |
|-----------|:------:|------------------|
| **Title Alignment** | 20% | Current title fit to "Senior AI Engineer" (70+ titles scored) + career trajectory titles + headline signal |
| **Skills Match** | 20% | 3-tier taxonomy (178 skills) with trust multiplier + platform assessment boost + endorsement validation |
| **Career Trajectory** | 20% | Production ML evidence in descriptions, headline/summary analysis, AI industry experience, leadership + startup signals |
| **Experience Fit** | 10% | Bell curve centered at 7yr (JD sweet spot: 5-9yr) |
| **Behavioral Signals** | 10% | 17 components from all 22 Redrob platform signals |
| **Location** | 8% | Pune/Noida preferred (JD), Tier-1 India acceptable, international with penalty |
| **Anti-Pattern** | 7% | Penalties for consulting-only, keyword stuffing, title chasing, CV-only focus |
| **Education** | 5% | Field relevance (CS/AI > EE > Mech) + institution tier + ML certification bonus |

### The Key Insight: Career Descriptions > Listed Skills

The JD warns that keyword matching is a trap. Our **career trajectory scorer** is the key differentiator:

```
Candidate A: "Senior AI Engineer" at TCS
  → Skills list: PyTorch, TensorFlow, BERT, FAISS, RAG
  → Career descriptions: "managed client deliverables", "requirement gathering", "stakeholder management"
  → Result: HIGH title score, but ZERO production ML evidence → consulting penalty → ranked LOW

Candidate B: "Software Engineer" at Razorpay
  → Skills list: Python, PyTorch
  → Career descriptions: "built recommendation pipeline serving 2M daily users",
    "deployed embedding model with p99 < 50ms", "A/B tested ranking algorithm"
  → Result: MODERATE title score, but STRONG production ML evidence → ranked HIGH
```

This is why embeddings fail here — they see Candidate A's keyword list and rank them high. We read what they actually *did*.

---

## Detailed Scoring Breakdown

### Honeypot Detection

Six rules catch impossible profiles before scoring begins:

| Rule | What It Catches | Example |
|------|-----------------|---------|
| Expert + 0 months | Skills claimed as "Expert" with zero actual usage time | 5 "Expert" skills, all 0 months |
| Calendar overflow | Job duration exceeds time between start and end dates | "2020-2021" but claims 36 months |
| Career overflow | Total career months > years_of_experience x 2 | 3yr exp but 120 months of jobs |
| Future dates | Start/end dates in the future | Job starting in 2027 |
| Skill explosion | Impossible skill count for experience level | 50 expert skills with 2yr exp |
| Perfect signals | Synthetically perfect behavioral scores | All rates exactly 1.0 |

**Result: 67 honeypots detected, 0 in top 100.**

### Trust Multiplier

Not all skill claims are equal:

| Proficiency | Duration | Endorsements | Multiplier |
|-------------|----------|:------------:|:----------:|
| Expert | > 0 months | 10+ | **1.0x** (full trust) |
| Expert | > 0 months | < 5 | 0.9x |
| Expert | **0 months** | any | **0.3x** (likely fake) |
| Advanced | > 0 months | - | 0.9x |
| Intermediate | - | - | 0.7x |
| Beginner | - | - | 0.4x |

This single mechanism eliminates most keyword stuffers from the top rankings.

### Anti-Pattern Detection

| Pattern | Penalty | How Detected |
|---------|:-------:|--------------|
| **Keyword Stuffer** | -0.80 | Non-technical title + AI skills listed + zero ML keywords in career descriptions |
| **Consulting Only** | -0.50 | Every job at consulting companies (54 tracked: TCS, Infosys, Wipro, Accenture, etc.) |
| **Title Chaser** | -0.20 | 70%+ jobs under 18 months with 3+ total positions |
| **CV Only** | -0.15 | Computer Vision focus only, no NLP/IR/search exposure |

### Behavioral Signals

All **22 Redrob platform signals** are used across 17 weighted components:

| Component | Weight | Signal Used |
|-----------|:------:|-------------|
| Notice period | 14% | `notice_period_days` |
| Recruiter response rate | 14% | `recruiter_response_rate` |
| Activity recency | 11% | `last_active_date` |
| Open to work | 7% | `open_to_work_flag` |
| GitHub activity | 7% | `github_activity_score` |
| Interview completion | 7% | `interview_completion_rate` |
| Verification trust | 7% | `verified_email` + `verified_phone` + `linkedin_connected` |
| Saved by recruiters | 6% | `saved_by_recruiters_30d` |
| Search appearances | 4% | `search_appearance_30d` |
| Avg response time | 4% | `avg_response_time_hours` |
| Offer acceptance | 4% | `offer_acceptance_rate` |
| Profile completeness | 4% | `profile_completeness_score` |
| Applications submitted | 3% | `applications_submitted_30d` |
| Profile views | 3% | `profile_views_received_30d` |
| Connections | 2% | `connection_count` |
| Endorsements | 2% | `endorsements_received` |
| Platform tenure | 1% | `signup_date` |

**Excluded:** `expected_salary_range_inr_lpa` — salary is a recruiter's budget constraint, not a candidate quality signal.

---

## Reasoning Examples

Every candidate gets a specific, fact-based reasoning string. No templates, no hallucination — each claim traces to actual profile fields.

**Strong candidate (Rank #1):**
> Senior AI Engineer at Netflix with 7.8yr exp. based in Vizag, Andhra Pradesh. 3/3 roles in ML/AI; ML leadership experience; startup/early-stage background; skills: LoRA, Learning to Rank, Weaviate, PEFT; 76% recruiter response rate.

**Good candidate with concerns (Rank #5):**
> Senior NLP Engineer at Mad Street Den with 8.0yr exp. based in Vizag, Andhra Pradesh. 3/3 roles in ML/AI; ML leadership experience; startup/early-stage background; skills: Reinforcement Learning, Weaviate, LoRA, LLMs. Concerns: low recruiter response rate (16%).

31 out of 100 candidates include honest concern flags — the system doesn't hide gaps.

---

## Quick Start

### Requirements

- Python 3.10+
- No GPU, no internet, no API keys

### Install & Run

```bash
# Install (only pyyaml + tqdm)
pip install -r requirements.txt

# Rank 100K candidates
python rank.py --candidates ./candidates.jsonl --out ./submission.csv

# Validate output format
python validate_submission.py submission.csv

# Run tests
python -m pytest tests/ -v

# Launch sandbox UI
python app.py
```

### Docker (for reproducibility testing)

```bash
docker build -t redrob-ranker .
docker run --rm -v $(pwd):/data redrob-ranker \
  python rank.py --candidates /data/candidates.jsonl --out /data/submission.csv
```

---

## Performance

| Constraint | Limit | Actual |
|-----------|------:|-------:|
| Runtime | 5 minutes | **25.2 seconds** |
| Memory | 16 GB | **< 2 GB** |
| GPU | Not available | **Not needed** |
| Network | Not available | **Not needed** |
| Dependencies | Minimal | **2 packages** (pyyaml, tqdm) |

---

## Project Structure

```
redrob-ranker/
├── rank.py                        # CLI entry point — orchestrates the 4-stage pipeline
├── config.py                      # All weights, thresholds, and tunable parameters
│
├── pipeline/
│   ├── loader.py                  # Streaming JSONL reader (memory-efficient)
│   ├── honeypot.py                # Stage 0: 6-rule impossible profile detection
│   ├── coarse_filter.py           # Stage 1: fast elimination (100K → 40K)
│   ├── scorer.py                  # Stage 2: composite scoring orchestrator
│   ├── ranker.py                  # Stage 3: final ranking + reasoning generation
│   └── features/
│       ├── title_alignment.py     # 70+ titles scored + headline boost
│       ├── skills_match.py        # 178 skills, 3 tiers, trust multiplier + assessments
│       ├── career_trajectory.py   # THE differentiator — description analysis for ML work
│       ├── experience_fit.py      # Bell curve centered at 7yr
│       ├── location_score.py      # India tier-based (Pune/Noida > Bangalore > Tier-2)
│       ├── education_score.py     # Field relevance + institution + certifications
│       ├── behavioral_signals.py  # 17 components from 22/22 Redrob signals
│       └── anti_patterns.py       # 4 detectors: stuffer, consulting, chaser, cv-only
│
├── jd/
│   ├── requirements.py            # Structured JD representation
│   └── taxonomy.py                # Title hierarchy, skill taxonomy, company classification
│
├── app.py                         # Gradio sandbox (live on HuggingFace Spaces)
├── tests/test_pipeline.py         # 10 tests covering all pipeline components
├── analysis/
│   ├── explore_data.py            # Dataset distribution analysis
│   └── inspect_top100.py          # Top 100 quality validation
├── validate_submission.py         # Official submission format validator
├── submission.csv                 # Final output: 100 ranked candidates with reasoning
├── submission_metadata.yaml       # Hackathon metadata
├── sample_candidates.json         # 50 sample candidates for sandbox/testing
├── requirements.txt               # Minimal: pyyaml + tqdm
└── LICENSE
```

**~1,900 lines** of hand-crafted scoring logic across 15 modules.

---

## Design Decisions

### Why rule-based over embeddings/LLMs?

| Consideration | Embeddings | LLM-based | Rule-based (ours) |
|---------------|:----------:|:---------:|:-----------------:|
| Detects keyword stuffers | No | Maybe | **Yes** |
| Reads career descriptions | Shallow | Yes | **Yes** |
| Catches honeypots | No | No | **Yes** |
| Evaluates behavioral signals | No | No | **Yes** |
| Explainable decisions | No | Partially | **Fully** |
| Runs in 25s on CPU | Unlikely | No | **Yes** |
| Zero dependencies | No | No | **Yes** |
| Deterministic output | Mostly | No | **Yes** |

The JD explicitly says keyword matching is the wrong approach. Embeddings are sophisticated keyword matching. We built something that understands *context*.

### Why these weights?

- **Title + Skills + Career = 60%** — what someone is and what they've done dominates
- **Career Trajectory at 20%** — same weight as skills, because *doing ML work* matters as much as *listing ML skills*
- **Behavioral at 10%** — availability is a real constraint; a perfect candidate with 0% response rate is useless
- **Anti-Pattern at 7%** — not a score, but a penalty. Catches the candidates that look good on surface but fail deeper inspection
- **Education at 5%** — matters least for a senior role; career speaks louder than degrees

### Key taxonomy numbers

| Category | Count |
|----------|------:|
| Titles scored | 70+ |
| Skills in taxonomy | 178 |
| Skill aliases mapped | 50+ |
| Consulting companies tracked | 54 |
| Product companies tracked | 80+ |
| AI-native companies | 20+ |
| Location tiers | 3 |
| Education field tiers | 3 |

---

## AI Tools Declaration

| Tool | Usage |
|------|-------|
| Claude | Architecture discussion, code review, iterative development |
| Claude Code | Development environment and implementation |

**No candidate data was fed to any LLM.** The ranking system uses zero AI inference — it's purely rule-based scoring with hand-crafted features derived from deep JD analysis.

---

## Testing

```
$ python -m pytest tests/ -v

tests/test_pipeline.py::test_honeypot_detection               PASSED
tests/test_pipeline.py::test_coarse_filter                     PASSED
tests/test_pipeline.py::test_title_scoring                     PASSED
tests/test_pipeline.py::test_experience_fit                    PASSED
tests/test_pipeline.py::test_full_pipeline                     PASSED
tests/test_pipeline.py::test_tiebreak_correctness              PASSED
tests/test_pipeline.py::test_anti_pattern_consulting_only      PASSED
tests/test_pipeline.py::test_anti_pattern_keyword_stuffer      PASSED
tests/test_pipeline.py::test_career_trajectory_leadership_bonus PASSED
tests/test_pipeline.py::test_reasoning_has_content             PASSED

10 passed in 0.74s
```

---

<div align="center">

**Built for the India Runs Hackathon 2026 | Track 1: Data & AI Challenge**

Team Umbrella.co | Priyanshu

</div>
