"""
Structured representation of the Senior AI Engineer JD.
Used by scorers to evaluate candidates against specific requirements.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class JDRequirements:
    title: str = "Senior AI Engineer — Founding Team"
    company: str = "Redrob AI"
    location_preferred: tuple = ("Pune", "Noida")
    location_acceptable: tuple = ("Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Kolkata")
    employment_type: str = "Full-time"
    work_mode: str = "Hybrid"

    # Experience
    experience_min: float = 5.0
    experience_max: float = 9.0
    experience_ideal: float = 7.0

    # Notice period preference
    notice_period_ideal_max: int = 30
    notice_period_acceptable_max: int = 90

    # What the role actually does
    role_summary: str = (
        "Own the intelligence layer: ranking, retrieval, and matching systems. "
        "Ship v2 ranking system with embeddings, hybrid retrieval, LLM-based re-ranking. "
        "Set up evaluation infrastructure with offline benchmarks and online A/B testing."
    )

    # Disqualifiers from JD
    disqualifiers: tuple = (
        "Pure research without production deployment",
        "AI experience only from recent LangChain/OpenAI projects (<12 months)",
        "Senior engineer who hasn't written production code in 18+ months",
        "Career entirely at consulting firms",
        "Primary expertise in CV/speech/robotics without NLP/IR",
        "Title-chasers switching every 1.5 years for title inflation",
        "Framework enthusiasts with only demo projects",
    )


JD = JDRequirements()
