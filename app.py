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
        return "No input. Enable sample or upload a file.", "", "", ""

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
        f"Input: {len(candidates)} candidates | "
        f"After filter: {len(kept)} | "
        f"Honeypots found: {len(honeypots)} | "
        f"Runtime: {elapsed:.2f}s"
    )

    # Rankings markdown table
    lines = ["| Rank | Score | Title | Company | Exp | Location | Reasoning |",
             "|------|-------|-------|---------|-----|----------|-----------|"]
    for i, s in enumerate(scored[:top_n], 1):
        p = s["profile"]
        r = generate_reasoning(s).replace("|", "/")[:100]
        lines.append(
            f"| {i} | {s['composite_score']:.4f} "
            f"| {p.get('current_title','?')} "
            f"| {p.get('current_company','?')} "
            f"| {p.get('years_of_experience',0):.1f}yr "
            f"| {p.get('location','?')} "
            f"| {r} |"
        )
    ranking_md = "\n".join(lines)

    # Score breakdown text
    breakdown_lines = ["```", f"{'Rank':<5} {'ID':<15} {'Title':<38} {'Title':>6} {'Skills':>7} {'Career':>7} {'Exp':>5} {'Beh':>5} {'Anti':>5} {'TOTAL':>7}"]
    breakdown_lines.append("-" * 100)
    for i, s in enumerate(scored[:min(20, top_n)], 1):
        sub = s["sub_scores"]
        t = s["profile"].get("current_title", "?")[:37]
        breakdown_lines.append(
            f"{i:<5} {s['candidate_id']:<15} {t:<38} "
            f"{sub['title']:>6.3f} {sub['skills']:>7.3f} {sub['career']:>7.3f} "
            f"{sub['experience']:>5.3f} {sub['behavioral']:>5.3f} {sub['anti_penalty']:>5.3f} "
            f"{s['composite_score']:>7.4f}"
        )
    breakdown_lines.append("```")
    breakdown_text = "\n".join(breakdown_lines)

    # CSV output
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["candidate_id", "rank", "score", "reasoning"])
    for i, s in enumerate(scored[:top_n], 1):
        w.writerow([s["candidate_id"], i, round(s["composite_score"], 4), generate_reasoning(s)])
    csv_out = buf.getvalue()

    hp_text = "\n".join(honeypots) if honeypots else "No honeypots detected."

    return summary, ranking_md, breakdown_text, csv_out, hp_text


with gr.Blocks(title="Redrob Candidate Ranker") as demo:
    gr.Markdown("""
    # 🎯 Redrob Intelligent Candidate Discovery & Ranking
    **Senior AI Engineer — Founding Team at Redrob AI** · India Runs Hackathon 2026

    Multi-signal pipeline: Title Alignment · Skills Match · Career Trajectory · Experience · Location · Education · Behavioral · Anti-Patterns
    """)

    with gr.Row():
        with gr.Column(scale=1):
            upload = gr.File(label="Upload .jsonl or .json", file_types=[".jsonl", ".json"])
            use_sample = gr.Checkbox(label="Use built-in sample (50 candidates)", value=True)
            top_n = gr.Slider(5, 100, value=20, step=5, label="Show top N results")
            run_btn = gr.Button("Run Ranking Pipeline", variant="primary")

        with gr.Column(scale=2):
            gr.Markdown("""
            **Architecture (CPU-only · No GPU · No network · <5min for 100K)**

            | Dimension | Weight |
            |-----------|--------|
            | Title Alignment | 20% |
            | Skills Match (3-tier + trust) | 20% |
            | Career Trajectory (desc analysis) | 20% |
            | Experience Fit (5-9yr bell) | 10% |
            | Location (Pune/Noida preferred) | 8% |
            | Behavioral Signals | 10% |
            | Education | 5% |
            | Anti-Pattern Penalty | 7% |
            """)

    summary_out = gr.Textbox(label="Summary", interactive=False)

    with gr.Tabs():
        with gr.Tab("Rankings"):
            ranking_out = gr.Markdown()
        with gr.Tab("Score Breakdown (Top 20)"):
            breakdown_out = gr.Markdown()
        with gr.Tab("CSV Output"):
            csv_out = gr.Textbox(label="Paste into .csv file", lines=10, show_copy_button=True)
        with gr.Tab("Honeypots Detected"):
            hp_out = gr.Textbox(label="Honeypot candidates", lines=5)

    run_btn.click(
        fn=run_ranking,
        inputs=[upload, use_sample, top_n],
        outputs=[summary_out, ranking_out, breakdown_out, csv_out, hp_out],
    )

    gr.Markdown("**GitHub:** [Priyanshu-byte-coder/redrob-ranker](https://github.com/Priyanshu-byte-coder/redrob-ranker)")

if __name__ == "__main__":
    demo.launch()
