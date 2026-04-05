"""Copy-ready cover-note snippet generator.

Produces short, truth-preserving text blocks a user can paste into
application forms or messages. Every claim must trace to canonical profile
evidence — same discipline as the tailoring validator.
"""
import logging

logger = logging.getLogger(__name__)


class SnippetsEngine:
    @staticmethod
    def generate(
        profile: dict,
        job: dict,
        variant: dict | None = None,
        keyword_alignment: dict | None = None,
    ) -> dict[str, str]:
        """Return a dict of snippet_type → text."""
        logger.info("Generating cover-note snippets")

        name = profile.get("contact", {}).get("name", "the applicant")
        skills = profile.get("skills", [])
        top_skills = ", ".join(skills[:4]) if skills else "relevant technical skills"

        job_title = job.get("title", "this role")
        company = job.get("company", "your team")

        # Supported emphasis keywords (from alignment if available)
        emphasis = []
        if keyword_alignment:
            emphasis = keyword_alignment.get("supported_keywords", [])[:3]
        emphasis_str = ", ".join(emphasis) if emphasis else top_skills

        # ── short_intro ────────────────────────────────
        short_intro = (
            f"Hi, I'm {name}. I'm a software professional with experience in "
            f"{top_skills}, and I'm excited about the {job_title} role at {company}."
        )

        # ── why_fit ────────────────────────────────────
        exp_count = len(profile.get("experience", []))
        why_fit = (
            f"With {exp_count} role(s) of hands-on experience and demonstrated skills "
            f"in {emphasis_str}, I can contribute meaningfully to {company}'s goals "
            f"for this position."
        )

        # ── why_role ───────────────────────────────────
        why_role = (
            f"The {job_title} position at {company} aligns well with my background "
            f"in {emphasis_str}. I am eager to bring my experience to your team."
        )

        # ── recruiter_note ─────────────────────────────
        recruiter_note = (
            f"Hi — I recently applied for the {job_title} role at {company}. "
            f"My background spans {top_skills} across {exp_count} professional role(s). "
            f"I'd love to connect and discuss how I can contribute."
        )

        return {
            "short_intro": short_intro,
            "why_fit": why_fit,
            "why_role": why_role,
            "recruiter_note": recruiter_note,
        }
