import re
import dateutil.parser
from datetime import datetime

class JobNormalizer:
    """Normalizes job data fields into a canonical internal format."""
    
    @staticmethod
    def normalize_job(raw_job: dict) -> dict:
        normalized = raw_job.copy()
        
        # 1. Normalize work mode based on location or description strings
        normalized['work_mode'] = JobNormalizer._extract_work_mode(raw_job)
        
        # 2. Normalize title
        if 'title' in normalized and normalized['title']:
            normalized['title'] = normalized['title'].strip()
            
        # 3. Canonical URL
        if 'source_job_url' in normalized and normalized['source_job_url']:
            url = normalized['source_job_url']
            # Strip queries tracking params
            normalized['canonical_job_url'] = url.split("?")[0]
            
        # 4. Dates
        if 'posted_at_raw' in normalized and normalized['posted_at_raw']:
            normalized['posted_at_normalized'] = JobNormalizer._parse_date(normalized['posted_at_raw'])
            
        # 5. Extract Requirements from Description
        desc = normalized.get('description_text', '') or ''
        normalized['requirements_json'] = JobNormalizer._extract_requirements(desc)
        
        normalized['normalization_confidence'] = "high"
        
        return normalized
        
    @staticmethod
    def _extract_work_mode(job: dict) -> str:
        loc = str(job.get('location', '')).lower()
        title = str(job.get('title', '')).lower()
        desc = str(job.get('description_text', '')).lower()
        
        combined_text = f"{loc} {title} {desc}"
        
        if "hybrid" in combined_text:
            return "hybrid"
        if "remote" in combined_text or "work from home" in combined_text:
            return "remote"
        if "onsite" in combined_text or "on-site" in combined_text:
            return "onsite"
            
        return "unknown"
        
    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        # Complex logic to parse relative dates if time permits
        if "ago" in date_str.lower():
            return datetime.utcnow() # Rough approximation for "days ago"
            
        try:
            return dateutil.parser.parse(date_str)
        except Exception:
            return None
            
    @staticmethod
    def _extract_requirements(desc: str) -> dict:
        # Heuristic extraction of common requirements
        requirements = {"skills": []}
        skills_db = ["python", "react", "fastapi", "docker", "aws", "postgres", "sql", "java", "typescript"]
        desc_lower = desc.lower()
        
        found_skills = [s for s in skills_db if s in desc_lower]
        requirements["skills"] = found_skills
        return requirements
