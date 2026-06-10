"""
Central configuration for the Redrob candidate ranking system.
All weights, thresholds, and tunable parameters live here.
"""

# --- Composite score weights (must sum to ~1.0) ---
WEIGHTS = {
    "title_alignment": 0.20,
    "skills_match": 0.20,
    "career_trajectory": 0.20,
    "experience_fit": 0.10,
    "location": 0.08,
    "education": 0.05,
    "behavioral_signals": 0.10,
    "anti_pattern": 0.07,  # This is (1 - penalty), so no penalty = full 0.07
}

# --- Experience fit ---
IDEAL_EXPERIENCE_YEARS = 7.0
EXPERIENCE_RANGE_MIN = 5.0
EXPERIENCE_RANGE_MAX = 9.0

# --- Coarse filter ---
MIN_EXPERIENCE_YEARS = 2.0

# --- Honeypot detection ---
HONEYPOT_EXPERT_ZERO_THRESHOLD = 3  # Flag if >= this many expert skills with 0 duration
HONEYPOT_DURATION_TOLERANCE_MONTHS = 6  # Calendar mismatch tolerance
HONEYPOT_CAREER_OVERFLOW_FACTOR = 2.0  # Total career months > yoe*12 * this factor

# --- Behavioral signals ---
NOTICE_PERIOD_IDEAL_MAX = 30
NOTICE_PERIOD_ACCEPTABLE_MAX = 60
RECENCY_CUTOFF_DAYS = 180  # Last active within this = good

# --- Skill matching ---
SKILL_TRUST_MULTIPLIERS = {
    "expert_with_duration": 1.0,
    "advanced_with_duration": 0.9,
    "expert_zero_duration": 0.3,  # Likely keyword stuffer
    "advanced_zero_duration": 0.5,
    "intermediate": 0.7,
    "beginner": 0.4,
}

# --- Skill tier weights in composite ---
SKILL_TIER_WEIGHTS = {
    "tier1": 0.55,
    "tier2": 0.30,
    "tier3": 0.15,
}
