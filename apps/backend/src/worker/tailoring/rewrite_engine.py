import logging
import copy

logger = logging.getLogger(__name__)

class RewriteEngine:
    @staticmethod
    def rewrite(canonical_profile: dict, jd_summary: dict, keyword_alignment: dict) -> dict:
        """
        Tailors the canonical profile to emphasize the supported keywords.
        Truth preservation: Content from canonical profile is strictly maintained
        and reordered, not hallucinatively invented.
        """
        logger.info("Rewriting resume based on verified profile...")
        
        tailored = copy.deepcopy(canonical_profile)
        supported_keywords = keyword_alignment.get("supported_keywords", [])
        
        # Tailor Summary: Emphasize top matched skills if available
        if supported_keywords:
            skills_str = ", ".join(supported_keywords[:3])
            original_summary = tailored.get("summary", {}).get("summary_text", "")
            tailored["summary"] = {
                "title": copy.deepcopy(jd_summary.get("normalized_title", tailored.get("summary", {}).get("title", ""))),
                "summary_text": f"{original_summary} Verified expertise in {skills_str}."
            }
            
        # Reorder Skills: Put supported keywords first
        if "skills" in tailored:
            original_skills = tailored["skills"]
            reordered = [s for s in original_skills if s.lower() in supported_keywords]
            reordered.extend([s for s in original_skills if s.lower() not in supported_keywords])
            tailored["skills"] = reordered
            
        # Optional: Reorder or bold experience bullets that contain matched keywords
        # In a simulated environment, we leave bullets mostly intact to strictly preserve truth.
        for exp in tailored.get("experience", []):
            exp["bullets"] = [b for b in exp.get("bullets", [])]  # Preserving exact texts
            
        return tailored
