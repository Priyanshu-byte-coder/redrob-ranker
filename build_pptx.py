"""
Build the hackathon submission PPTX from the Redrob template.
Preserves branding (background images, fonts) and fills content + diagrams.
Template has WHITE body background — all text must be DARK.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pathlib import Path

TEMPLATE = Path(__file__).parent / "Idea Submission Template _ Redrob.pptx"
ASSETS = Path(__file__).parent / "assets"
OUTPUT = Path(__file__).parent / "Redrob_Submission_v3.pptx"

# Colors — DARK text on WHITE background
DARK = RGBColor(0x1E, 0x29, 0x3B)       # Primary text
MED = RGBColor(0x47, 0x55, 0x69)         # Secondary text
DIM = RGBColor(0x94, 0xA3, 0xB8)         # Muted/caption
ACCENT = RGBColor(0x4F, 0x46, 0xE5)      # Indigo headings
GREEN = RGBColor(0x05, 0x96, 0x69)
RED = RGBColor(0xDC, 0x26, 0x26)
# For slide 11 (dark background) — white text
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xCB, 0xD5, 0xE1)


def clear_textbox(shape):
    tf = shape.text_frame
    tf.clear()
    return tf


def add_p(tf, text, size=11, bold=False, color=DARK, space_after=Pt(3)):
    p = tf.add_paragraph()
    p.space_after = space_after
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return p


def first_p(tf, text, size=11, bold=False, color=DARK):
    p = tf.paragraphs[0]
    p.space_after = Pt(3)
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_img(slide, path, left, top, width=None, height=None):
    kw = {"image_file": str(path), "left": left, "top": top}
    if width: kw["width"] = width
    if height: kw["height"] = height
    slide.shapes.add_picture(**kw)


def build():
    prs = Presentation(str(TEMPLATE))
    slides = list(prs.slides)

    # ===================== SLIDE 1: Title =====================
    s = slides[0]
    for shape in s.shapes:
        if not shape.has_text_frame:
            continue
        text = shape.text_frame.text
        if "Team Name" in text:
            tf = clear_textbox(shape)
            first_p(tf, "Team Name :  Umbrella.co", size=16, bold=True, color=DARK)
        elif "Team Leader" in text:
            tf = clear_textbox(shape)
            first_p(tf, "Team Leader :  Priyanshu", size=16, bold=True, color=DARK)
        elif "Problem Statement" in text:
            tf = clear_textbox(shape)
            first_p(tf, "Track 1: Data & AI  |  Intelligent Candidate Discovery & Ranking", size=14, bold=True, color=DARK)

    # ===================== SLIDE 2: Solution Overview =====================
    s = slides[1]
    for shape in s.shapes:
        if shape.has_text_frame and "proposed solution" in shape.text_frame.text.lower():
            tf = clear_textbox(shape)
            tf.word_wrap = True

            first_p(tf, "What is your proposed solution?", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "A rule-based multi-signal ranking pipeline that processes 100K candidates in ~25 seconds on CPU. Uses 22/22 Redrob signals + profile text. No GPU, no LLM API calls, no network.", size=10, color=DARK)
            add_p(tf, "")
            add_p(tf, "4-Stage Funnel:", size=10, bold=True, color=ACCENT)
            add_p(tf, "  Stage 0:  Honeypot Detection  (6 rules \u2192 67 impossible profiles caught)", size=9, color=MED)
            add_p(tf, "  Stage 1:  Coarse Filter  (100K \u2192 40,789 via title + description analysis)", size=9, color=MED)
            add_p(tf, "  Stage 2:  Multi-Signal Scoring  (8 weighted dimensions)", size=9, color=MED)
            add_p(tf, "  Stage 3:  Final Ranking + Reasoning  (top 100 CSV with explanations)", size=9, color=MED)
            add_p(tf, "")
            add_p(tf, "What differentiates from traditional matching?", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "\u2022  Traditional: keyword/embedding similarity \u2014 gets fooled by keyword stuffers", size=9, color=DARK)
            add_p(tf, "\u2022  Ours: reads career descriptions to find actual ML work evidence", size=9, color=DARK)
            add_p(tf, "\u2022  Marketing Manager listing \"PyTorch\" scores 0 \u2014 descriptions show zero ML", size=9, color=DARK)
            add_p(tf, "\u2022  Trust multiplier: \"Expert\" skill + 0 months = only 0.3\u00d7 credit", size=9, color=DARK)

    # ===================== SLIDE 3: JD Understanding =====================
    s = slides[2]
    for shape in s.shapes:
        if shape.has_text_frame and "key requirements" in shape.text_frame.text.lower():
            tf = clear_textbox(shape)
            tf.word_wrap = True

            first_p(tf, "Key requirements extracted from the JD:", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "\u2022  Role: Senior AI Engineer for founding team at product company", size=9, color=DARK)
            add_p(tf, "\u2022  Experience: 5\u20139 years (sweet spot: 7yr), production ML required", size=9, color=DARK)
            add_p(tf, "\u2022  Must-have: embeddings, vector DBs, PyTorch/TF, semantic search, NLP", size=9, color=DARK)
            add_p(tf, "\u2022  Location: Pune/Noida preferred, India Tier-1 acceptable", size=9, color=DARK)
            add_p(tf, "\u2022  Founding team = needs leadership ability + startup mindset", size=9, color=DARK)
            add_p(tf, "")
            add_p(tf, "Most important signals for relevance:", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "1.  Career Trajectory \u2014 what someone actually did > what they claim", size=9, bold=True, color=DARK)
            add_p(tf, "     Descriptions > titles > skills listed", size=8, color=DIM)
            add_p(tf, "2.  Trust Multiplier \u2014 \"Expert\" proficiency + 0mo duration = 0.3\u00d7 credit", size=9, bold=True, color=DARK)
            add_p(tf, "3.  Anti-Patterns \u2014 consulting-only, keyword stuffers, title chasers", size=9, bold=True, color=DARK)
            add_p(tf, "4.  Behavioral Signals \u2014 17 components from 22/22 Redrob signals", size=9, bold=True, color=DARK)
            add_p(tf, "5.  Skill Assessments \u2014 platform-validated scores boost trust", size=9, bold=True, color=DARK)
            add_p(tf, "6.  Profile Headline/Summary \u2014 ML keywords in professional text", size=9, bold=True, color=DARK)

    # ===================== SLIDE 4: Ranking Methodology =====================
    s = slides[3]
    for shape in s.shapes:
        if shape.has_text_frame and "retrieve" in shape.text_frame.text.lower():
            tf = clear_textbox(shape)
            tf.word_wrap = True

            first_p(tf, "How does the system score and rank?", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "Retrieve: Stream 100K JSONL, coarse filter to ~40K", size=9, color=DARK)
            add_p(tf, "Score: 8 weighted sub-scores \u2192 composite", size=9, color=DARK)
            add_p(tf, "Rank: Sort, tie-break by ID, per-candidate reasoning", size=9, color=DARK)
            add_p(tf, "")
            add_p(tf, "Algorithms:", size=11, bold=True, color=ACCENT)
            add_p(tf, "\u2022  No ML models \u2014 pure rule-based", size=9, color=DARK)
            add_p(tf, "\u2022  Bell curve for experience (7yr center)", size=9, color=DARK)
            add_p(tf, "\u2022  3-tier skill taxonomy (178 skills)", size=9, color=DARK)
            add_p(tf, "\u2022  Platform skill_assessment_scores boost", size=9, color=DARK)
            add_p(tf, "\u2022  Leadership + startup bonuses", size=9, color=DARK)
            add_p(tf, "")
            add_p(tf, "Composite = \u03a3(weight_i \u00d7 score_i)", size=9, bold=True, color=MED)
            add_p(tf, "Anti-pattern: (1 \u2212 penalty) reduces score", size=9, color=MED)

    # Scoring chart — right side
    img = ASSETS / "scoring_weights.png"
    if img.exists():
        add_img(s, img, left=Emu(4800000), top=Emu(1350000), width=Emu(4100000))

    # ===================== SLIDE 5: Explainability =====================
    s = slides[4]
    for shape in s.shapes:
        if shape.has_text_frame and "ranking decisions" in shape.text_frame.text.lower():
            tf = clear_textbox(shape)
            tf.word_wrap = True

            first_p(tf, "How are ranking decisions explained?", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "Per-candidate reasoning from actual profile fields:", size=9, color=DARK)
            add_p(tf, "  \"ML Engineer at Razorpay with 7.2yr exp, based in Bangalore.", size=8, color=DIM)
            add_p(tf, "   3/4 roles in ML/AI; skills: pytorch, embeddings, faiss. 85% response rate.\"", size=8, color=DIM)
            add_p(tf, "")
            add_p(tf, "How do we prevent hallucinations?", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "\u2022  Zero LLM calls \u2014 every claim traces to a specific profile field", size=9, color=DARK)
            add_p(tf, "\u2022  Skills only counted if present in candidate's skills array", size=9, color=DARK)
            add_p(tf, "\u2022  ML job count from description keyword analysis, not inference", size=9, color=DARK)
            add_p(tf, "")
            add_p(tf, "How do we handle suspicious profiles?", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "\u2022  Honeypot detection: 6 rules \u2192 67 caught, 0 in top 100", size=9, color=DARK)
            add_p(tf, "\u2022  Trust multiplier: expert + 0mo = 0.3\u00d7 credit", size=9, color=DARK)
            add_p(tf, "\u2022  Keyword stuffer flag: AI skills + zero ML in descriptions", size=9, color=DARK)
            add_p(tf, "\u2022  Date arithmetic catches fabricated timelines", size=9, color=DARK)

    # ===================== SLIDE 6: Workflow (diagram) =====================
    s = slides[5]
    for shape in s.shapes:
        if shape.has_text_frame and "complete workflow" in shape.text_frame.text.lower():
            tf = clear_textbox(shape)
            first_p(tf, "", size=1)
    img = ASSETS / "pipeline_flow.png"
    if img.exists():
        add_img(s, img, left=Emu(350000), top=Emu(1050000), width=Emu(8450000))

    # ===================== SLIDE 7: Architecture (diagram) =====================
    s = slides[6]
    img = ASSETS / "architecture.png"
    if img.exists():
        add_img(s, img, left=Emu(350000), top=Emu(1050000), width=Emu(8450000))

    # ===================== SLIDE 8: Results (dashboard) =====================
    s = slides[7]
    for shape in s.shapes:
        if shape.has_text_frame and "results" in shape.text_frame.text.lower() and "insights" in shape.text_frame.text.lower():
            tf = clear_textbox(shape)
            first_p(tf, "", size=1)
    img = ASSETS / "results_dashboard.png"
    if img.exists():
        add_img(s, img, left=Emu(350000), top=Emu(1050000), width=Emu(8450000))

    # ===================== SLIDE 9: Technologies =====================
    s = slides[8]
    for shape in s.shapes:
        if shape.has_text_frame and "technologies" in shape.text_frame.text.lower() and "frameworks" in shape.text_frame.text.lower():
            tf = clear_textbox(shape)
            tf.word_wrap = True

            first_p(tf, "Core Stack:", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "\u2022  Python 3.11 \u2014 core language, zero ML library dependencies", size=10, color=DARK)
            add_p(tf, "\u2022  Rule-based scoring \u2014 hand-crafted features from deep JD analysis", size=10, color=DARK)
            add_p(tf, "\u2022  Streaming JSONL \u2014 memory-efficient, handles 100K in single pass", size=10, color=DARK)
            add_p(tf, "\u2022  Gradio 5.x \u2014 interactive sandbox on HuggingFace Spaces", size=10, color=DARK)
            add_p(tf, "\u2022  Git \u2014 16 meaningful commits, iterative development", size=10, color=DARK)
            add_p(tf, "")
            add_p(tf, "Why rule-based over ML/embeddings?", size=12, bold=True, color=ACCENT)
            add_p(tf, "")
            add_p(tf, "The JD explicitly warns: keyword matching is a trap.", size=10, bold=True, color=DARK)
            add_p(tf, "")
            add_p(tf, "\u2022  Embeddings treat all keywords equally \u2014 can't distinguish real ML engineers from stuffers", size=9, color=MED)
            add_p(tf, "\u2022  Rules encode domain knowledge: career trajectories, company classification, trust multipliers", size=9, color=MED)
            add_p(tf, "\u2022  No GPU, no API costs \u2014 ~25 seconds on CPU", size=9, color=MED)
            add_p(tf, "\u2022  Every decision fully explainable and auditable", size=9, color=MED)

    # ===================== SLIDE 10: Submission Assets =====================
    s = slides[9]
    for shape in s.shapes:
        if shape.has_text_frame and "github" in shape.text_frame.text.lower():
            tf = clear_textbox(shape)
            tf.word_wrap = True

            first_p(tf, "GitHub Repository:", size=12, bold=True, color=ACCENT)
            add_p(tf, "github.com/Priyanshu-byte-coder/redrob-ranker", size=10, color=DARK)
            add_p(tf, "")
            add_p(tf, "Live Sandbox Demo:", size=12, bold=True, color=ACCENT)
            add_p(tf, "huggingface.co/spaces/bladebutcher/redrob-ranker", size=10, color=DARK)
            add_p(tf, "")
            add_p(tf, "Submission Output:", size=12, bold=True, color=ACCENT)
            add_p(tf, "submission.csv \u2014 100 candidates ranked with per-candidate reasoning", size=10, color=DARK)
            add_p(tf, "")
            add_p(tf, "Quality Assurance:", size=12, bold=True, color=ACCENT)
            add_p(tf, "\u2022  10 automated tests, all passing", size=10, color=DARK)
            add_p(tf, "\u2022  Submission validator passes all checks", size=10, color=DARK)
            add_p(tf, "\u2022  0 honeypots in top 100, top 10 manually verified", size=10, color=DARK)
            add_p(tf, "\u2022  25s runtime (limit: 5 min)  |  <2GB RAM (limit: 16GB)", size=10, color=DARK)

    # ===================== SLIDE 11: Thank You (DARK bg) =====================
    s = slides[10]
    txBox = s.shapes.add_textbox(Emu(1500000), Emu(2200000), Emu(6000000), Emu(2200000))
    tf = txBox.text_frame
    tf.word_wrap = True
    first_p(tf, "Umbrella.co", size=30, bold=True, color=WHITE)
    add_p(tf, "", size=8)
    add_p(tf, "Priyanshu  |  Team Lead", size=16, bold=True, color=WHITE)
    add_p(tf, "", size=6)
    add_p(tf, "doshipriyanshu3@gmail.com", size=12, color=LIGHT)
    add_p(tf, "+91-9549926195", size=12, color=LIGHT)
    add_p(tf, "", size=6)
    add_p(tf, "India Runs Hackathon 2026  |  Track 1: Data & AI Challenge", size=11, color=LIGHT)

    # ===================== SAVE =====================
    prs.save(str(OUTPUT))
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    build()
