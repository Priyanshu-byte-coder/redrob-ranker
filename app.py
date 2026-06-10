"""
Gradio sandbox app for the Redrob Intelligent Candidate Ranking System.
Compatible with Gradio 5.x / 6.x (HuggingFace Spaces).

Run locally:  python app.py
"""
import json
import time
import sys
import os
import csv
import io
from pathlib import Path

import gradio as gr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.coarse_filter import coarse_filter
from pipeline.scorer import score_candidate
from pipeline.ranker import generate_reasoning


SAMPLE_PATH = Path(__file__).parent / "sample_candidates.json"


def run_ranking(upload_file, use_sample: bool, top_n: int):
    """Main ranking function called by Gradio."""
    candidates = []

    if upload_file is not None:
        content = Path(upload_file).read_text(encoding="utf-8")
        if str(upload_file).endswith(".json"):
            candidates = json.loads(content)
        else:
            candidates = [json.loads(l) for l in content.strip().split("\n") if l.strip()]
    elif use_sample and SAMPLE_PATH.exists():
        candidates = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    else:
        return "No input. Enable sample or upload a file.", "", "", "", ""

    start = time.time()

    kept = []
    honeypots = []
    for c in candidates:
        should_keep, is_hp, reasons = coarse_filter(c)
        if is_hp:
            honeypots.append(f"{c['candidate_id']}: {'; '.join(reasons)}")
        if should_keep:
            kept.append(c)

    scored = [score_candidate(c) for c in kept]
    scored.sort(key=lambda x: (-x["composite_score"], x["candidate_id"]))
    top_n = min(top_n, len(scored), 100)
    elapsed = time.time() - start

    summary = (
        f"**{len(candidates):,}** candidates processed in **{elapsed:.2f}s** | "
        f"After filter: **{len(kept):,}** | "
        f"Honeypots found: **{len(honeypots)}** | "
        f"Showing top **{top_n}**"
    )

    # Rankings markdown table
    lines = ["| Rank | Score | Candidate | Title | Company | Exp | Location |",
             "|-----:|------:|-----------|-------|---------|----:|----------|"]
    for i, s in enumerate(scored[:top_n], 1):
        p = s["profile"]
        title = p.get("current_title", "?")[:30]
        company = p.get("current_company", "?")[:20]
        loc = p.get("location", "?")[:15]
        lines.append(
            f"| {i} | {s['composite_score']:.4f} "
            f"| `{s['candidate_id']}` "
            f"| {title} "
            f"| {company} "
            f"| {p.get('years_of_experience',0):.1f}yr "
            f"| {loc} |"
        )
    ranking_md = "\n".join(lines)

    # Score breakdown text
    breakdown_lines = [
        "| Rank | ID | Title | Title | Skills | Career | Exp | Beh | Anti | **Total** |",
        "|-----:|:---|:------|------:|-------:|-------:|----:|----:|-----:|----------:|",
    ]
    for i, s in enumerate(scored[:min(20, top_n)], 1):
        sub = s["sub_scores"]
        t = s["profile"].get("current_title", "?")[:25]
        breakdown_lines.append(
            f"| {i} | `{s['candidate_id']}` | {t} "
            f"| {sub['title']:.3f} | {sub['skills']:.3f} | {sub['career']:.3f} "
            f"| {sub['experience']:.3f} | {sub['behavioral']:.3f} | {sub['anti_penalty']:.3f} "
            f"| **{s['composite_score']:.4f}** |"
        )
    breakdown_text = "\n".join(breakdown_lines)

    # Reasoning tab
    reasoning_lines = ["| Rank | Candidate | Reasoning |",
                       "|-----:|-----------|-----------|"]
    for i, s in enumerate(scored[:min(20, top_n)], 1):
        r = generate_reasoning(s).replace("|", "/")[:200]
        reasoning_lines.append(f"| {i} | `{s['candidate_id']}` | {r} |")
    reasoning_md = "\n".join(reasoning_lines)

    # CSV output
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["candidate_id", "rank", "score", "reasoning"])
    for i, s in enumerate(scored[:top_n], 1):
        w.writerow([s["candidate_id"], i, round(s["composite_score"], 4), generate_reasoning(s)])
    csv_out = buf.getvalue()

    hp_text = "\n".join(honeypots) if honeypots else "No honeypots detected in this dataset."

    return summary, ranking_md, breakdown_text, reasoning_md, csv_out, hp_text


theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
    font=gr.themes.GoogleFont("Inter"),
)

with gr.Blocks(title="Redrob Candidate Ranker", theme=theme) as demo:
    gr.Markdown("""
# Redrob Intelligent Candidate Discovery & Ranking

**Senior AI Engineer — Founding Team** at Redrob AI | India Runs Hackathon 2026

Multi-signal pipeline: Title Alignment · Skills Match · Career Trajectory · Experience Fit · Location · Education · Behavioral Signals · Anti-Pattern Detection
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            upload = gr.File(label="Upload .jsonl or .json", file_types=[".jsonl", ".json"])
            use_sample = gr.Checkbox(label="Use built-in sample (50 candidates)", value=True)
            top_n = gr.Slider(5, 100, value=20, step=5, label="Show top N results")
            run_btn = gr.Button("Run Ranking Pipeline", variant="primary", size="lg")

        with gr.Column(scale=2):
            gr.Markdown("""
### Scoring Architecture
*CPU-only · No GPU · No network · <1min for 100K candidates*

| Dimension | Weight | Signal |
|-----------|-------:|--------|
| Title Alignment | 20% | Current + historical title fit |
| Skills Match | 20% | 3-tier taxonomy + trust multiplier |
| Career Trajectory | 20% | Description analysis for ML evidence |
| Experience Fit | 10% | Bell curve centered at 7yr (5-9yr ideal) |
| Behavioral Signals | 10% | Notice period, response rate, recency |
| Location | 8% | Pune/Noida preferred, Tier-1 India OK |
| Anti-Pattern Penalty | 7% | Consulting-only, keyword stuffers, title chasers |
| Education | 5% | CS/AI field + institution tier |
            """)

    summary_out = gr.Markdown(label="Summary")

    with gr.Tabs():
        with gr.Tab("Rankings"):
            ranking_out = gr.Markdown()
        with gr.Tab("Score Breakdown"):
            breakdown_out = gr.Markdown()
        with gr.Tab("Per-Candidate Reasoning"):
            reasoning_out = gr.Markdown()
        with gr.Tab("CSV Export"):
            csv_out = gr.Textbox(label="Copy-paste into .csv file", lines=12, show_copy_button=True)
        with gr.Tab("Honeypots Detected"):
            hp_out = gr.Textbox(label="Flagged impossible profiles", lines=5)

    run_btn.click(
        fn=run_ranking,
        inputs=[upload, use_sample, top_n],
        outputs=[summary_out, ranking_out, breakdown_out, reasoning_out, csv_out, hp_out],
    )

    gr.Markdown("""
---
**[GitHub](https://github.com/Priyanshu-byte-coder/redrob-ranker)** · Built by Priyanshu · India Runs Hackathon 2026
    """)

if __name__ == "__main__":
    demo.launch()
