from src.worker.tailoring.skill_gap import SkillGapAnalyzer, KeywordAligner
from src.worker.tailoring.validator import ResumeValidator
from src.worker.tailoring.ats_scorer import ATSScorer

def test_skill_gap_analyzer():
    jd = {"must_have_skills": ["python", "react", "golang"]}
    profile = {"skills": ["Python", "Docker"]}
    
    gap = SkillGapAnalyzer.analyze(jd, profile)
    
    assert "python" in gap["matched_skills"]
    assert "react" in gap["unsupported_skills"]
    assert "golang" in gap["unsupported_skills"]
    assert gap["experience_signals_present"] is True

def test_keyword_aligner():
    gap = {
        "matched_skills": ["python"],
        "unsupported_skills": ["react", "golang"]
    }
    jd = {"must_have_skills": ["python", "react", "golang"]}
    
    alignment = KeywordAligner.align(jd, gap)
    assert alignment["supported_keywords"] == ["python"]
    assert "python" in alignment["suggested_emphasis"]["summary"]

def test_resume_validator():
    canonical = {"skills": ["python"]}
    
    # 1. Truth preserved
    tailored_safe = {"skills": ["python"]}
    report1 = ResumeValidator.validate(tailored_safe, canonical)
    assert report1["status"] == "pass"
    assert len(report1["unsupported_claims"]) == 0
    
    # 2. Hallucinated injection
    tailored_unsafe = {"skills": ["python", "react", "golang"]}
    report2 = ResumeValidator.validate(tailored_unsafe, canonical)
    assert report2["status"] == "fail"
    assert "react" in report2["unsupported_claims"]

def test_ats_scorer():
    jd = {"must_have_skills": ["python", "react", "golang", "aws"]}
    tailored = {"skills": ["python", "aws"]}
    
    score = ATSScorer.score(jd, tailored)
    
    assert score["coverage_percentage"] == 50 # 2 out of 4
    assert len(score["missing_critical_terms"]) == 2
    assert "react" in score["missing_critical_terms"]
