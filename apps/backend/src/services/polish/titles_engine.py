"""Deterministic suggested-titles engine.

Uses canonical profile experience titles, skills clusters, and user preferences
to produce transparent title suggestions. No blackbox recommender —
every suggestion traces back to concrete evidence.
"""
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Common title families mapped from skill/domain signals
TITLE_FAMILIES = {
    "backend":   ["Backend Engineer", "Python Developer", "API Engineer", "Platform Engineer"],
    "frontend":  ["Frontend Engineer", "React Developer", "UI Engineer"],
    "fullstack": ["Full-Stack Engineer", "Software Engineer", "Web Developer"],
    "ml":        ["ML Engineer", "Machine Learning Engineer", "Data Scientist", "Applied Scientist"],
    "genai":     ["GenAI Engineer", "Applied AI Engineer", "LLM Engineer"],
    "data":      ["Data Engineer", "Analytics Engineer", "Data Platform Engineer"],
    "devops":    ["DevOps Engineer", "SRE", "Infrastructure Engineer", "Cloud Engineer"],
    "mobile":    ["Mobile Engineer", "iOS Developer", "Android Developer"],
}

SKILL_DOMAIN_MAP = {
    "python": "backend", "fastapi": "backend", "django": "backend", "flask": "backend",
    "react": "frontend", "vue": "frontend", "angular": "frontend", "typescript": "frontend",
    "next.js": "fullstack", "node.js": "fullstack",
    "pytorch": "ml", "tensorflow": "ml", "scikit-learn": "ml", "pandas": "data",
    "langchain": "genai", "llm": "genai", "openai": "genai", "huggingface": "genai",
    "docker": "devops", "kubernetes": "devops", "terraform": "devops", "aws": "devops",
    "spark": "data", "airflow": "data", "kafka": "data",
    "swift": "mobile", "kotlin": "mobile", "react native": "mobile",
}


class TitlesEngine:
    @staticmethod
    def suggest(canonical_profile: dict, preferences: dict | None = None) -> list[dict]:
        """Return a ranked list of suggested titles with rationale."""
        logger.info("Generating suggested target titles")

        # 1. Collect signals
        domain_votes: Counter = Counter()

        # 1a. Existing experience titles
        existing_titles: list[str] = []
        for exp in canonical_profile.get("experience", []):
            title = exp.get("title", "")
            if title:
                existing_titles.append(title)

        # 1b. Skills → domain votes
        skills = [s.lower() for s in canonical_profile.get("skills", [])]
        for skill in skills:
            domain = SKILL_DOMAIN_MAP.get(skill)
            if domain:
                domain_votes[domain] += 1

        # 1c. Preference emphasis adds weight
        if preferences:
            emphasis = (preferences.get("resume_emphasis") or "").lower()
            if emphasis in TITLE_FAMILIES:
                domain_votes[emphasis] += 3  # strong boost

        # 2. Build ranked suggestions
        suggestions: list[dict] = []

        # 2a. Direct titles from experience (highest confidence)
        seen_titles: set[str] = set()
        for t in existing_titles[:3]:
            norm = t.strip()
            if norm.lower() not in seen_titles:
                seen_titles.add(norm.lower())
                suggestions.append({
                    "title": norm,
                    "confidence": "high",
                    "rationale": f"You held this exact title in your experience history.",
                })

        # 2b. Domain-family titles
        for domain, count in domain_votes.most_common(4):
            for family_title in TITLE_FAMILIES.get(domain, [])[:2]:
                if family_title.lower() not in seen_titles:
                    seen_titles.add(family_title.lower())
                    suggestions.append({
                        "title": family_title,
                        "confidence": "medium" if count >= 2 else "low",
                        "rationale": f"Your skills in {domain} ({count} matching skills) align with this title.",
                    })

        return suggestions[:8]  # cap at 8
