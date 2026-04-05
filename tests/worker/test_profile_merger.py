import pytest
from src.worker.profile_merger import merge_profiles

def test_empty_profiles():
    merged, conf = merge_profiles([])
    assert merged["identity"] == {}
    assert merged["skills"] == []

def test_precedence_merge():
    # Lower precedence resume
    doc1 = {
        "document_id": 1,
        "document_type": "resume",
        "json": {
            "identity": {"name": "John Doe", "email": "john@old.com"},
            "skills": ["Python", "Java"],
            "experience": [{"title": "Dev", "company": "A Corp"}]
        }
    }
    # Higher precedence linkedin
    doc2 = {
        "document_id": 2,
        "document_type": "linkedin_export",
        "json": {
            "identity": {"email": "john@new.com", "location": "NY"},
            "skills": ["Go", "Python"],
            "experience": [{"title": "Dev", "company": "A Corp", "start_date": "2020"}]
        }
    }
    
    merged, conf = merge_profiles([doc1, doc2])
    
    # Precedence ensures LinkedIn data wins where overlapping
    # But wait, our merger sorting puts linkedin first, so first field wins.
    # linkedin has email=john@new.com. Resume has name=John Doe, email=john@old.com
    # Expected: name="John Doe", email="john@new.com", location="NY"
    assert merged["identity"]["email"] == "john@new.com"
    assert merged["identity"]["name"] == "John Doe"
    assert merged["identity"]["location"] == "NY"
    
    # Skills deduplicated
    assert sorted(merged["skills"]) == ["Go", "Java", "Python"]
    
    # Experience: The A Corp entry from LinkedIn should win, Resume duplicate is ignored
    assert len(merged["experience"]) == 1
    assert merged["experience"][0]["start_date"] == "2020"
    
    assert conf["conflicts_resolved"] == 1
    assert "identity.email" in conf["section_provenance"]
    assert conf["section_provenance"]["identity.email"] == 2 # doc_id 2
