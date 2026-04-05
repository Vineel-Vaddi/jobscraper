from src.worker.job_scorer import JobScorer
import json

def test_job_scorer_empty_profile():
    job = {"title": "Engineer"}
    scored = JobScorer.score_job(job, None)
    assert scored["fit_score"] == 0

def test_job_scorer_baseline():
    job = {"title": "Software Engineer", "requirements_json": {"skills": ["python", "docker"]}}
    profile = {
        "summary": {"title": "Software Engineer"},
        "skills": ["Python", "Docker", "AWS"]
    }
    
    scored = JobScorer.score_job(job, json.dumps(profile))
    # Base 50 + 15 (title) + 10 (2 skills matched) = 75
    assert scored["fit_score"] >= 75
    
def test_job_scorer_penalties():
    job = {"title": "Backend Engineer", "requirements_json": {"skills": ["rust", "go"]}}
    profile = {
        "summary": {"title": "Frontend Engineer"},
        "skills": ["JavaScript", "React"]
    }
    
    scored = JobScorer.score_job(job, json.dumps(profile))
    # Base 50 - 4 (2 missed skills) = 46. (Title doesn't align either).
    assert scored["fit_score"] < 50
