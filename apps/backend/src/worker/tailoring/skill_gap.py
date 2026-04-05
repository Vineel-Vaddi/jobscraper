import logging

logger = logging.getLogger(__name__)

class SkillGapAnalyzer:
    @staticmethod
    def analyze(jd_summary: dict, canonical_profile: dict) -> dict:
        """
        Compares structured JD requirements against Canonical Profile skills.
        """
        must_have = set(v.lower() for v in jd_summary.get("must_have_skills", []))
        
        profile_skills = set(v.lower() for v in canonical_profile.get("skills", []))
        
        matched_skills = list(must_have.intersection(profile_skills))
        unsupported_skills = list(must_have.difference(profile_skills))
        
        gap_json = {
            "matched_skills": matched_skills,
            "unsupported_skills": unsupported_skills,
            "experience_signals_present": True if matched_skills else False
        }
        
        return gap_json

class KeywordAligner:
    @staticmethod
    def align(jd_summary: dict, gap_json: dict) -> dict:
        """
        Identifies which keywords are supported and specifies 
        where they should surface in the resume.
        """
        alignment = {
            "supported_keywords": gap_json["matched_skills"],
            "unsupported_keywords": gap_json["unsupported_skills"],
            "suggested_emphasis": {
                "summary": gap_json["matched_skills"][:2],
                "skills": gap_json["matched_skills"]
            }
        }
        return alignment
