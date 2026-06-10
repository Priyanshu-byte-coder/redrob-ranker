"""
Streamlit sandbox app for the Redrob Intelligent Candidate Ranking System.
Demonstrates the ranking pipeline on a small candidate sample.

Run locally:  streamlit run app.py
"""
import json
import time
import sys
import os
import csv
import io
from pathlib import Path

import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.coarse_filter import coarse_filter
from pipeline.scorer import score_candidate
from pipeline.ranker import generate_reasoning


st.set_page_config(
    page_title="Redrob AI Candidate Ranker",
    page_icon="🎯",
    layout="wide",
)

st.title("Redrob Intelligent Candidate Discovery & Ranking")
st.markdown("""
**Senior AI Engineer — Founding Team at Redrob AI**

This system ranks candidates from a 100K pool using a multi-signal scoring pipeline
that goes beyond keyword matching to understand career trajectories, production ML
experience, and behavioral signals.
""")

# --- Sidebar: Architecture Overview ---
with st.sidebar:
    st.header("Architecture")
    st.markdown("""
    **4-Stage Pipeline:**
    1. Honeypot Detection
    2. Coarse Filter (100K → ~4K)
    3. Multi-Signal Scoring (8 features)
    4. Final Ranking + Reasoning

    **8 Scoring Dimensions:**
    - Title Alignment (20%)
    - Skills Match (20%)
    - Career Trajectory (20%)
    - Experience Fit (10%)
    - Location (8%)
    - Education (5%)
    - Behavioral Signals (10%)
    - Anti-Pattern Penalty (7%)

    **Constraints Met:**
    - CPU-only, no GPU
    - No network calls
    - <5 min for 100K candidates
    - <16 GB RAM
    """)

    st.header("Weight Tuning")
    st.markdown("Adjust scoring weights (for exploration only):")
    w_title = st.slider("Title", 0.0, 0.5, 0.20, 0.05)
    w_skills = st.slider("Skills", 0.0, 0.5, 0.20, 0.05)
    w_career = st.slider("Career", 0.0, 0.5, 0.20, 0.05)
    w_exp = st.slider("Experience", 0.0, 0.3, 0.10, 0.05)
    w_loc = st.slider("Location", 0.0, 0.2, 0.08, 0.02)
    w_edu = st.slider("Education", 0.0, 0.2, 0.05, 0.01)
    w_behav = st.slider("Behavioral", 0.0, 0.3, 0.10, 0.05)
    w_anti = st.slider("Anti-Pattern", 0.0, 0.2, 0.07, 0.01)


# --- Main area ---
st.header("Run the Ranker")

upload = st.file_uploader(
    "Upload a candidate JSONL file (or use the sample)",
    type=["jsonl", "json"],
)

# Try to find sample file
sample_path = None
for p in [
    Path("data/sample_candidates.json"),
    Path("sample_candidates.json"),
    Path("../[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/sample_candidates.json"),
]:
    if p.exists():
        sample_path = p
        break

use_sample = st.checkbox("Use built-in sample (50 candidates)", value=True)

if st.button("Run Ranking Pipeline", type="primary"):
    candidates = []

    if upload is not None:
        content = upload.read().decode("utf-8")
        if upload.name.endswith(".json"):
            candidates = json.loads(content)
        else:
            candidates = [json.loads(line) for line in content.strip().split("\n") if line.strip()]
    elif use_sample and sample_path:
        candidates = json.loads(sample_path.read_text(encoding="utf-8"))
    else:
        st.error("Please upload a file or use the built-in sample.")
        st.stop()

    st.info(f"Processing {len(candidates)} candidates...")

    start = time.time()

    # Stage 0+1: Filter
    kept = []
    honeypots = []
    for c in candidates:
        should_keep, is_hp, reasons = coarse_filter(c)
        if is_hp:
            honeypots.append((c["candidate_id"], reasons))
        if should_keep:
            kept.append(c)

    # Stage 2: Score
    # Apply custom weights if changed
    import config
    config.WEIGHTS["title_alignment"] = w_title
    config.WEIGHTS["skills_match"] = w_skills
    config.WEIGHTS["career_trajectory"] = w_career
    config.WEIGHTS["experience_fit"] = w_exp
    config.WEIGHTS["location"] = w_loc
    config.WEIGHTS["education"] = w_edu
    config.WEIGHTS["behavioral_signals"] = w_behav
    config.WEIGHTS["anti_pattern"] = w_anti

    scored = [score_candidate(c) for c in kept]

    # Stage 3: Rank
    scored.sort(key=lambda x: (-x["composite_score"], x["candidate_id"]))
    top_n = min(100, len(scored))

    elapsed = time.time() - start

    # --- Results ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Input", len(candidates))
    col2.metric("After Filter", len(kept))
    col3.metric("Honeypots Found", len(honeypots))
    col4.metric("Runtime", f"{elapsed:.2f}s")

    if honeypots:
        with st.expander(f"Honeypots Detected ({len(honeypots)})"):
            for cid, reasons in honeypots:
                st.write(f"**{cid}**: {'; '.join(reasons)}")

    st.subheader(f"Top {top_n} Candidates")

    for i, s in enumerate(scored[:top_n], 1):
        profile = s["profile"]
        sub = s["sub_scores"]
        reasoning = generate_reasoning(s)

        with st.expander(
            f"#{i} — {profile.get('current_title', '?')} at "
            f"{profile.get('current_company', '?')} "
            f"(Score: {s['composite_score']:.4f})"
        ):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                **{profile.get('anonymized_name', 'N/A')}**
                - Title: {profile.get('current_title', '?')}
                - Company: {profile.get('current_company', '?')}
                - Experience: {profile.get('years_of_experience', 0):.1f} years
                - Location: {profile.get('location', '?')}, {profile.get('country', '?')}
                - Industry: {profile.get('current_industry', '?')}
                """)

            with c2:
                st.markdown("**Score Breakdown:**")
                for key, val in sub.items():
                    bar_val = val if key != "anti_penalty" else 1.0 - val
                    st.progress(min(1.0, max(0.0, bar_val)), text=f"{key}: {val:.3f}")

            st.markdown(f"**Reasoning:** {reasoning}")
            if s.get("matched_skills"):
                st.markdown(f"**Matched Skills:** {', '.join(s['matched_skills'])}")
            if s.get("anti_flags"):
                st.warning(f"Anti-pattern flags: {', '.join(s['anti_flags'])}")

    # Download CSV
    if scored:
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        for i, s in enumerate(scored[:top_n], 1):
            writer.writerow({
                "candidate_id": s["candidate_id"],
                "rank": i,
                "score": round(s["composite_score"], 4),
                "reasoning": generate_reasoning(s),
            })
        st.download_button(
            "Download Ranking CSV",
            csv_buffer.getvalue(),
            "ranking_output.csv",
            "text/csv",
        )
