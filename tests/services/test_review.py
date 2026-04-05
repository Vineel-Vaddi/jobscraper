from src.services.review.diff_engine import DiffEngine
from src.services.review.why_changed import WhyChangedGenerator

def test_diff_engine_deterministic_results():
    base = {
        "summary": {"summary_text": "I am a dev."},
        "skills": ["python", "go"],
        "experience": [
            {
                "title": "Engineer",
                "company": "Tech Corp",
                "bullets": ["Wrote code", "Deployed code"]
            }
        ]
    }
    
    tailored = {
        "summary": {"summary_text": "I am a senior dev."},
        "skills": ["python", "go", "react"],
        "experience": [
            {
                "title": "Engineer",
                "company": "Tech Corp",
                "bullets": ["Deployed code", "Wrote fast code"]
            }
        ]
    }
    
    diff = DiffEngine.compute_diff(base, tailored)
    
    # Check Summary
    assert diff[0]["section_name"] == "Summary"
    assert diff[0]["status"] == "modified"
    assert diff[0]["bullets"][0]["type"] == "rewritten"
    
    # Check Skills
    assert diff[1]["section_name"] == "Technical Skills"
    assert diff[1]["status"] == "modified"
    
    # React should be added
    added_skills = [b["text"] for b in diff[1]["bullets"] if b["type"] == "added"]
    assert "react" in added_skills
    
    # Check Experience
    assert "Experience" in diff[2]["section_name"]
    assert diff[2]["status"] == "modified"
    
    # Bullets rewritten vs unchanged
    unchanged = [b["text"] for b in diff[2]["bullets"] if b["type"] == "unchanged"]
    rewritten = [b["text"] for b in diff[2]["bullets"] if b["type"] == "rewritten"]
    
    assert "Deployed code" in unchanged
    assert "Wrote fast code" in rewritten


def test_why_changed_generator():
    alignment = {"supported_keywords": ["python", "fastapi"]}
    gap = {"unsupported_skills": ["rust"]}
    validator = {"unsupported_claims": ["C++"]}
    
    notes = WhyChangedGenerator.generate_notes(alignment, gap, validator)
    
    assert any("python" in note for note in notes)
    assert any("rust" in note for note in notes)
    assert any("C++" in note for note in notes)
    assert any("WARNING" in note for note in notes)
