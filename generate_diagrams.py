"""Generate visual diagrams for the hackathon presentation (light theme)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)

# Light theme palette (matching white PPTX background)
BG = '#FFFFFF'
CARD_LIGHT = '#F8FAFC'
DARK_TEXT = '#1E293B'
MED_TEXT = '#475569'
DIM_TEXT = '#94A3B8'
ACCENT = '#4F46E5'  # Indigo
ACCENT2 = '#7C3AED'  # Violet
GREEN = '#059669'
ORANGE = '#D97706'
RED = '#DC2626'
BLUE = '#2563EB'
TEAL = '#0D9488'
BORDER = '#E2E8F0'


def draw_pipeline_flow():
    """Diagram 1: Vertical pipeline funnel for Slide 6."""
    fig, ax = plt.subplots(figsize=(11, 6.5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis('off')

    stages = [
        ("candidates.jsonl", "100,000 candidates", 6.0, '#CBD5E1', '#64748B', 9.5),
        ("Stage 0: Honeypot Detection", "6 rules  \u00b7  67 impossible profiles flagged", 4.9, '#FEE2E2', RED, 8.2),
        ("Stage 1: Coarse Filter", "Title + Description analysis  \u00b7  40,789 kept", 3.8, '#DBEAFE', BLUE, 7.0),
        ("Stage 2: Multi-Signal Scoring", "8 dimensions  \u00b7  weighted composite", 2.7, '#E0E7FF', ACCENT, 5.8),
        ("Stage 3: Ranking + Reasoning", "Sort \u00b7 Tie-break \u00b7 Per-candidate explanation", 1.6, '#D1FAE5', GREEN, 4.6),
        ("submission.csv", "Top 100 ranked candidates", 0.5, '#D1FAE5', GREEN, 3.5),
    ]

    for title, subtitle, y, bg_color, border_color, width in stages:
        x = 5.5 - width / 2
        box = FancyBboxPatch((x, y), width, 0.75, boxstyle="round,pad=0.12",
                             facecolor=bg_color, edgecolor=border_color, linewidth=1.8)
        ax.add_patch(box)
        ax.text(5.5, y + 0.50, title, ha='center', va='center',
                fontsize=12, fontweight='bold', color=DARK_TEXT, fontfamily='sans-serif')
        ax.text(5.5, y + 0.22, subtitle, ha='center', va='center',
                fontsize=8.5, color=MED_TEXT, fontfamily='sans-serif')

    # Arrows
    arrow_x = 5.5
    for i in range(len(stages) - 1):
        y_from = stages[i][2]
        y_to = stages[i + 1][2] + 0.75
        ax.annotate('', xy=(arrow_x, y_to + 0.02), xytext=(arrow_x, y_from - 0.02),
                     arrowprops=dict(arrowstyle='->', color='#94A3B8', lw=1.8))

    # Side annotations
    ax.text(10.0, 4.9 + 0.38, "67 impossible\nprofiles caught", ha='center',
            fontsize=8.5, color=RED, fontfamily='sans-serif', fontweight='bold')
    ax.text(10.0, 3.8 + 0.38, "59,211\neliminated", ha='center',
            fontsize=8.5, color=ORANGE, fontfamily='sans-serif', fontweight='bold')
    ax.text(10.0, 0.5 + 0.38, "0 honeypots\nin top 100 \u2713", ha='center',
            fontsize=8.5, color=GREEN, fontweight='bold', fontfamily='sans-serif')

    plt.tight_layout(pad=0.5)
    plt.savefig(ASSETS / "pipeline_flow.png", dpi=200, facecolor=BG,
                bbox_inches='tight', pad_inches=0.2)
    plt.close()
    print("  Created pipeline_flow.png")


def draw_architecture():
    """Diagram 2: System architecture for Slide 7."""
    fig, ax = plt.subplots(figsize=(11, 6.5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis('off')

    def draw_box(x, y, w, h, label, sublabel, bg, border, fontsize=10):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                             facecolor=bg, edgecolor=border, linewidth=1.6)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2 + (0.12 if sublabel else 0), label,
                ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color=DARK_TEXT, fontfamily='sans-serif')
        if sublabel:
            ax.text(x + w/2, y + h/2 - 0.17, sublabel,
                    ha='center', va='center', fontsize=7.5,
                    color=MED_TEXT, fontfamily='sans-serif')

    # Input section
    draw_box(0.2, 5.2, 2.0, 0.9, "candidates.jsonl", "100K profiles", '#F1F5F9', '#94A3B8')
    draw_box(0.2, 3.9, 2.0, 0.9, "config.py", "Weights & thresholds", '#F1F5F9', '#94A3B8')

    # Pipeline section label
    ax.text(4.3, 6.6, "pipeline/", ha='center', fontsize=11,
            fontweight='bold', color=ACCENT, fontfamily='sans-serif')

    # Pipeline boxes
    draw_box(3.2, 5.5, 2.2, 0.7, "honeypot.py", "6 detection rules", '#FEE2E2', RED)
    draw_box(3.2, 4.5, 2.2, 0.7, "coarse_filter.py", "Title + desc filter", '#FEF3C7', ORANGE)
    draw_box(3.2, 3.5, 2.2, 0.7, "scorer.py", "8-dim composite", '#E0E7FF', ACCENT)
    draw_box(3.2, 2.5, 2.2, 0.7, "ranker.py", "Sort + reasoning", '#D1FAE5', GREEN)

    # JD/Taxonomy section
    draw_box(6.2, 5.5, 2.2, 0.9, "jd/taxonomy.py", "178 skills \u00b7 62 titles", '#EDE9FE', ACCENT2)
    draw_box(6.2, 4.2, 2.2, 0.9, "jd/requirements.py", "Structured JD", '#EDE9FE', ACCENT2)

    # Output section
    draw_box(9.0, 4.8, 1.8, 0.9, "submission.csv", "Top 100 ranked", '#D1FAE5', GREEN)
    draw_box(9.0, 3.5, 1.8, 0.9, "rank.py", "CLI orchestrator", '#DBEAFE', BLUE)

    # Feature modules
    ax.text(5.5, 1.8, "pipeline/features/", ha='center', fontsize=10,
            fontweight='bold', color=ACCENT, fontfamily='sans-serif')

    features = [
        ("Title\nAlignment", "20%"),
        ("Skills\nMatch", "20%"),
        ("Career\nTrajectory", "20%"),
        ("Experience\nFit", "10%"),
        ("Behavioral\nSignals", "10%"),
        ("Location", "8%"),
        ("Anti-\nPattern", "7%"),
        ("Education", "5%"),
    ]

    for i, (name, weight) in enumerate(features):
        x = 0.3 + i * 1.33
        box = FancyBboxPatch((x, 0.2), 1.15, 1.2, boxstyle="round,pad=0.06",
                             facecolor='#F8FAFC', edgecolor=ACCENT, linewidth=1.0, alpha=0.8)
        ax.add_patch(box)
        ax.text(x + 0.575, 1.0, name, ha='center', va='center',
                fontsize=7, fontweight='bold', color=DARK_TEXT, fontfamily='sans-serif')
        ax.text(x + 0.575, 0.5, weight, ha='center', va='center',
                fontsize=9, color=ACCENT, fontweight='bold', fontfamily='sans-serif')

    # Arrows
    ax.annotate('', xy=(3.15, 5.9), xytext=(2.25, 5.65),
                arrowprops=dict(arrowstyle='->', color='#94A3B8', lw=1.3))
    ax.annotate('', xy=(3.15, 4.3), xytext=(2.25, 4.35),
                arrowprops=dict(arrowstyle='->', color='#94A3B8', lw=1.3))
    ax.annotate('', xy=(8.95, 5.2), xytext=(5.45, 2.9),
                arrowprops=dict(arrowstyle='->', color='#94A3B8', lw=1.3))
    # Features to scorer
    ax.annotate('', xy=(4.3, 3.45), xytext=(4.3, 1.45),
                arrowprops=dict(arrowstyle='->', color=ACCENT, lw=1.2, linestyle='dashed'))

    plt.tight_layout(pad=0.3)
    plt.savefig(ASSETS / "architecture.png", dpi=200, facecolor=BG,
                bbox_inches='tight', pad_inches=0.2)
    plt.close()
    print("  Created architecture.png")


def draw_scoring_weights():
    """Diagram 3: Horizontal bar chart of scoring dimensions for Slide 4."""
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=BG)
    ax.set_facecolor(BG)

    dims = [
        ("Education", 0.05, '#94A3B8'),
        ("Anti-Pattern Penalty", 0.07, RED),
        ("Location", 0.08, TEAL),
        ("Experience Fit", 0.10, ORANGE),
        ("Behavioral Signals", 0.10, ACCENT2),
        ("Career Trajectory", 0.20, GREEN),
        ("Skills Match", 0.20, BLUE),
        ("Title Alignment", 0.20, ACCENT),
    ]

    names = [d[0] for d in dims]
    weights = [d[1] for d in dims]
    colors = [d[2] for d in dims]

    y_pos = np.arange(len(dims))
    bars = ax.barh(y_pos, weights, height=0.6, color=colors, alpha=0.75,
                   edgecolor=colors, linewidth=1.2)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9.5, color=DARK_TEXT, fontfamily='sans-serif')
    ax.set_xlim(0, 0.27)

    # Percentage labels
    for i, (bar, w) in enumerate(zip(bars, weights)):
        ax.text(w + 0.005, i, f'{int(w*100)}%', va='center',
                fontsize=11, fontweight='bold', color=colors[i], fontfamily='sans-serif')

    # Style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(BORDER)
    ax.spines['left'].set_color(BORDER)
    ax.tick_params(colors=MED_TEXT)
    ax.set_xticks([0.05, 0.10, 0.15, 0.20])
    ax.set_xticklabels(['5%', '10%', '15%', '20%'], color=DIM_TEXT, fontsize=8)
    ax.xaxis.grid(True, alpha=0.3, color=BORDER)

    plt.tight_layout(pad=0.8)
    plt.savefig(ASSETS / "scoring_weights.png", dpi=200, facecolor=BG,
                bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print("  Created scoring_weights.png")


def draw_results_dashboard():
    """Diagram 4: Results metrics dashboard for Slide 8."""
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis('off')

    def metric_card(x, y, value, label, color, w=2.1, h=1.7):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                             facecolor='#F8FAFC', edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2 + 0.22, value, ha='center', va='center',
                fontsize=22, fontweight='bold', color=color, fontfamily='sans-serif')
        ax.text(x + w/2, y + h/2 - 0.35, label, ha='center', va='center',
                fontsize=8.5, color=MED_TEXT, fontfamily='sans-serif')

    # Row 1
    metric_card(0.2, 3.0, "100K", "Candidates\nProcessed", BLUE)
    metric_card(2.6, 3.0, "40,789", "After\nFiltering", ACCENT)
    metric_card(5.0, 3.0, "67", "Honeypots\nDetected", ORANGE)
    metric_card(7.4, 3.0, "0", "Honeypots\nin Top 100", GREEN)

    # Row 2
    metric_card(0.2, 0.8, "25.2s", "Runtime\n(limit: 5 min)", GREEN)
    metric_card(2.6, 0.8, "<2 GB", "Memory\n(limit: 16 GB)", BLUE)
    metric_card(5.0, 0.8, "22/22", "Redrob Signals\nUsed", ACCENT2)
    metric_card(7.4, 0.8, "0", "LLM API\nCalls", ACCENT)

    plt.tight_layout(pad=0.3)
    plt.savefig(ASSETS / "results_dashboard.png", dpi=200, facecolor=BG,
                bbox_inches='tight', pad_inches=0.2)
    plt.close()
    print("  Created results_dashboard.png")


if __name__ == "__main__":
    print("Generating diagrams (light theme)...")
    draw_pipeline_flow()
    draw_architecture()
    draw_scoring_weights()
    draw_results_dashboard()
    print("Done!")
