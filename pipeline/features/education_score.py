"""
Education scorer.
Field relevance + institution tier + degree level + certifications.
"""
from jd.taxonomy import EDUCATION_FIELDS_HIGH, EDUCATION_FIELDS_MEDIUM

# ML/AI relevant certification keywords
CERT_KEYWORDS_HIGH = {
    "machine learning", "deep learning", "artificial intelligence",
    "tensorflow", "pytorch", "nlp", "natural language processing",
    "computer vision", "neural network", "reinforcement learning",
    "ml engineer", "ai engineer", "mlops",
}
CERT_KEYWORDS_MEDIUM = {
    "data science", "data engineering", "cloud ml", "sagemaker",
    "vertex ai", "azure ai", "aws ml", "gcp ml",
    "python", "statistics", "big data", "apache spark",
}


def _field_relevance(field_of_study: str) -> float:
    """Score 0-1 based on how relevant the field is to AI/ML."""
    lower = field_of_study.lower().strip()
    for f in EDUCATION_FIELDS_HIGH:
        if f in lower:
            return 1.0
    for f in EDUCATION_FIELDS_MEDIUM:
        if f in lower:
            return 0.6
    return 0.3


def _tier_bonus(tier: str) -> float:
    """Score bonus based on institution tier."""
    return {
        "tier_1": 0.20,
        "tier_2": 0.10,
        "tier_3": 0.0,
        "tier_4": -0.05,
        "unknown": 0.0,
    }.get(tier, 0.0)


def _degree_bonus(degree: str) -> float:
    """Score bonus for advanced degrees."""
    lower = degree.lower().strip()
    if any(d in lower for d in ("ph.d", "phd", "doctorate")):
        return 0.15
    if any(d in lower for d in ("m.tech", "mtech", "m.s.", "ms ", "m.sc", "msc", "master")):
        return 0.08
    if any(d in lower for d in ("mba",)):
        return 0.0
    return 0.0  # B.Tech, B.E., etc.


def _cert_bonus(candidate: dict) -> float:
    """Bonus for ML/AI-relevant certifications. Max 0.15."""
    certs = candidate.get("certifications", [])
    if not certs:
        return 0.0

    high_count = 0
    med_count = 0
    for cert in certs:
        name = cert.get("name", "").lower()
        issuer = cert.get("issuer", "").lower()
        combined = f"{name} {issuer}"
        if any(kw in combined for kw in CERT_KEYWORDS_HIGH):
            high_count += 1
        elif any(kw in combined for kw in CERT_KEYWORDS_MEDIUM):
            med_count += 1

    bonus = min(high_count, 3) * 0.04 + min(med_count, 2) * 0.02
    return min(0.15, bonus)


def score_education(candidate: dict) -> float:
    """Score education relevance. Takes best education entry + certification bonus."""
    education = candidate.get("education", [])
    if not education:
        base = 0.3  # No education info — don't penalize heavily
    else:
        best_score = 0.0
        for edu in education:
            field = edu.get("field_of_study", "")
            tier = edu.get("tier", "unknown")
            degree = edu.get("degree", "")

            field_score = _field_relevance(field)
            tier_adj = _tier_bonus(tier)
            degree_adj = _degree_bonus(degree)

            score = field_score * 0.6 + (0.5 + tier_adj) * 0.25 + (0.4 + degree_adj) * 0.15
            best_score = max(best_score, score)
        base = best_score

    # Certification bonus on top
    cert = _cert_bonus(candidate)

    return min(1.0, base + cert)
