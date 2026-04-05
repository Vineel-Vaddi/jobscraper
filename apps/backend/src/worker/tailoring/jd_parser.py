import json
import logging

logger = logging.getLogger(__name__)

class JDParser:
    @staticmethod
    def parse_jd(job_record) -> dict:
        """
        Parses the selected job's description_text and requirements_json 
        into a structured JD representation.
        """
        logger.info(f"Parsing JD for job {job_record.id}...")
        
        # In a full deployment, this would invoke an LLM.
        # Here, we enrich the existing requirements_json or use simulated NLP extraction.
        
        reqs = {}
        if job_record.requirements_json:
            try:
                if isinstance(job_record.requirements_json, str):
                    reqs = json.loads(job_record.requirements_json)
                else:
                    reqs = job_record.requirements_json
            except Exception as e:
                logger.error(f"Failed to parse requirements_json: {e}")
                
        # Mocking structured extraction output
        must_have = reqs.get("skills", [])
        
        # Simulated extraction fallback if sparse
        if not must_have and job_record.description_text:
            desc_lower = job_record.description_text.lower()
            possible_skills = ["python", "react", "typescript", "aws", "docker", "kubernetes", "go", "java", "sql"]
            must_have = [s for s in possible_skills if s in desc_lower]
            
        jd_summary = {
            "normalized_title": job_record.title,
            "must_have_skills": must_have,
            "preferred_skills": reqs.get("preferred_skills", ["agile", "communication"]),
            "seniority": job_record.seniority or "Not specified",
            "employment_type": job_record.employment_type or "Full-time",
            "domain_keywords": ["scalability", "performance", "backend"] if "backend" in (job_record.title or "").lower() else []
        }
        
        return jd_summary
