from src.worker.job_normalizer import JobNormalizer

def test_job_normalizer_work_mode():
    job1 = {"location": "San Francisco", "title": "Software Engineer"}
    assert JobNormalizer.normalize_job(job1)["work_mode"] == "unknown"
    
    job2 = {"location": "Remote - US"}
    assert JobNormalizer.normalize_job(job2)["work_mode"] == "remote"
    
    job3 = {"description_text": "We offer a flexible hybrid schedule"}
    assert JobNormalizer.normalize_job(job3)["work_mode"] == "hybrid"

def test_job_canonical_url():
    job = {"source_job_url": "https://linkedin.com/jobs/view/12345?trackingId=abcd"}
    normalized = JobNormalizer.normalize_job(job)
    assert normalized["canonical_job_url"] == "https://linkedin.com/jobs/view/12345"

def test_skill_extraction():
    desc = "We need extensive experience with Python, React, and AWS."
    job = {"description_text": desc}
    normalized = JobNormalizer.normalize_job(job)
    skills = normalized["requirements_json"].get("skills", [])
    assert "python" in skills
    assert "react" in skills
    assert "aws" in skills
