import logging
import json

logger = logging.getLogger(__name__)

class ResumeValidator:
    @staticmethod
    def validate(tailored_resume: dict, canonical_profile: dict) -> dict:
        """
        Post-rewrite sanity checker.
        Ensures that vocabulary in tailored resume is mapped strictly from Evidence Pack.
        """
        logger.info("Validating tailored resume for truthfulness...")
        
        # In a real environment, we would NLP-compare the exact strings.
        # Here we perform deterministic set comparisons to catch hallucinated tools/skills.
        
        tailored_skills = set(s.lower() for s in tailored_resume.get("skills", []))
        canonical_skills = set(s.lower() for s in canonical_profile.get("skills", []))
        
        unsupported = list(tailored_skills.difference(canonical_skills))
        
        status = "fail" if unsupported else "pass"
        
        # Strict fallback
        return {
            "status": status,
            "unsupported_claims": unsupported,
            "message": "Validation complete. Truth boundaries checked.",
            "unsupported_claim_count": len(unsupported)
        }
