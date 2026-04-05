import json

class JobScorer:
    """Scores a job's suitability based on the Canonical Profile."""
    
    @staticmethod
    def score_job(normalized_job: dict, canonical_profile_json_str: str) -> dict:
        """
        Compares the job against the profile JSON string.
        Modifies and returns the job dict with fit_score, reasons, gaps.
        """
        if not canonical_profile_json_str:
            normalized_job["fit_score"] = 0
            normalized_job["fit_reasons_json"] = json.dumps(["No profile provided"])
            normalized_job["fit_gaps_json"] = json.dumps([])
            return normalized_job
            
        try:
            profile = json.loads(canonical_profile_json_str)
        except Exception:
            profile = {}
            
        score = 50 # Baseline neutral
        reasons = []
        gaps = []
        
        # 1. Job Title Alignment
        job_title = str(normalized_job.get("title", "")).lower()
        if "summary" in profile and "title" in profile.get("summary", {}):
            prof_title = str(profile["summary"]["title"]).lower()
            if prof_title in job_title or job_title in prof_title:
                score += 15
                reasons.append("Job title aligns well with profile")
                
        # 2. Skills Overlap
        job_skills = normalized_job.get("requirements_json", {}).get("skills", [])
        prof_skills = [s.lower() for s in profile.get("skills", [])]
        
        matched_skills = []
        missing_skills = []
        
        for js in job_skills:
            if js.lower() in prof_skills:
                matched_skills.append(js)
            else:
                missing_skills.append(js)
                
        if matched_skills:
            score += min(len(matched_skills) * 5, 25)
            reasons.append(f"Strong skill overlap: {', '.join(matched_skills)}")
            
        if missing_skills:
            gaps.append(f"Missing some requested skills: {', '.join(missing_skills)}")
            score -= min(len(missing_skills) * 2, 10)
            
        # 3. Work Mode Override / Bump
        # We don't have perfect profile work mode extraction, but we can fake it for MVP
        mode = normalized_job.get("work_mode", "unknown")
        if mode == "remote":
            reasons.append("Remote friendly")
            score += 5
            
        # Bound score 0-100
        score = max(0, min(100, score))
        
        normalized_job["fit_score"] = score
        normalized_job["fit_reasons_json"] = json.dumps(reasons)
        normalized_job["fit_gaps_json"] = json.dumps(gaps)
        
        return normalized_job
