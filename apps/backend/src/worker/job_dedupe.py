import hashlib

class JobDeduper:
    """Provides a deduplication key strategy for normalized jobs."""
    
    @staticmethod
    def generate_dedupe_key(normalized_job: dict) -> str:
        """
        Generates a deterministic hash representing the job.
        Rules:
        - If external_job_id exists, use it.
        - Else, use canonical_job_url
        - Else, use lowercase [Title + Company + Location]
        """
        
        ext_id = normalized_job.get("external_job_id")
        if ext_id:
            return f"ext_id:{ext_id}"
            
        canonical_url = normalized_job.get("canonical_job_url")
        if canonical_url:
            return f"url:{hashlib.md5(canonical_url.encode()).hexdigest()}"
            
        # Fallback heuristic
        title = str(normalized_job.get("title", "")).lower().strip()
        company = str(normalized_job.get("company", "")).lower().strip()
        loc = str(normalized_job.get("location", "")).lower().strip()
        
        raw_key = f"{title}||{company}||{loc}"
        return f"heuristic:{hashlib.md5(raw_key.encode()).hexdigest()}"
