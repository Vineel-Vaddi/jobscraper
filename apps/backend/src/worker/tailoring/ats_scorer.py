import logging

logger = logging.getLogger(__name__)

class ATSScorer:
    @staticmethod
    def score(jd_summary: dict, tailored_resume: dict) -> dict:
        """
        Calculates heuristic ATS coverage summarizing keyword distributions.
        """
        logger.info("Scoring ATS performance...")
        
        must_have = jd_summary.get("must_have_skills", [])
        if not must_have:
            return {"coverage_percentage": 0, "missing_critical_terms": []}
            
        must_have_lower = set(s.lower() for s in must_have)
        tailored_skills = set(s.lower() for s in tailored_resume.get("skills", []))
        
        matched = must_have_lower.intersection(tailored_skills)
        missing = must_have_lower.difference(tailored_skills)
        
        coverage = len(matched) / len(must_have_lower) if must_have_lower else 0
        score = int(coverage * 100)
        
        return {
            "coverage_percentage": score,
            "must_have_keyword_coverage": score,
            "missing_critical_terms": list(missing),
            "readability_heuristic": "Pass",
            "section_distribution": {
                "skills": len(matched)
            }
        }
