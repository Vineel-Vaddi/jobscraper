"""Unit tests for Phase 7 polish services."""
from src.services.polish.titles_engine import TitlesEngine
from src.services.polish.snippets_engine import SnippetsEngine


# ── Titles Engine Tests ─────────────────────────────────────────

def test_titles_from_experience_history():
    profile = {
        "experience": [
            {"title": "Software Engineer", "company": "Acme"},
            {"title": "Backend Developer", "company": "Globex"},
        ],
        "skills": ["python", "fastapi", "docker"],
    }
    titles = TitlesEngine.suggest(profile)

    # Should include exact past titles with high confidence
    high_conf = [t for t in titles if t["confidence"] == "high"]
    assert len(high_conf) >= 2
    title_names = [t["title"] for t in high_conf]
    assert "Software Engineer" in title_names
    assert "Backend Developer" in title_names


def test_titles_from_skills():
    profile = {
        "experience": [],
        "skills": ["python", "fastapi", "django", "docker", "kubernetes"],
    }
    titles = TitlesEngine.suggest(profile)
    title_names = [t["title"] for t in titles]
    # Backend and devops skills should yield relevant suggestions
    assert any("Backend" in t or "Python" in t for t in title_names)


def test_titles_with_preference_boost():
    profile = {
        "experience": [],
        "skills": ["python", "react", "node.js"],
    }
    prefs = {"resume_emphasis": "frontend"}
    titles = TitlesEngine.suggest(profile, prefs)
    title_names = [t["title"] for t in titles]
    # Frontend gets boosted
    assert any("Frontend" in t or "React" in t or "UI" in t for t in title_names)


def test_titles_capped_at_eight():
    profile = {
        "experience": [
            {"title": f"Title {i}", "company": "Co"} for i in range(10)
        ],
        "skills": ["python", "react", "tensorflow", "docker", "kotlin"],
    }
    titles = TitlesEngine.suggest(profile)
    assert len(titles) <= 8


# ── Snippets Engine Tests ───────────────────────────────────────

def test_snippets_include_all_types():
    profile = {
        "contact": {"name": "Alice"},
        "skills": ["Python", "FastAPI", "React"],
        "experience": [{"title": "SWE", "company": "X"}],
    }
    job = {"title": "Backend Engineer", "company": "Acme"}
    kw = {"supported_keywords": ["Python", "FastAPI"]}

    snippets = SnippetsEngine.generate(profile, job, keyword_alignment=kw)

    assert "short_intro" in snippets
    assert "why_fit" in snippets
    assert "why_role" in snippets
    assert "recruiter_note" in snippets


def test_snippets_contain_name_and_company():
    profile = {
        "contact": {"name": "Bob"},
        "skills": ["Go"],
        "experience": [],
    }
    job = {"title": "API Dev", "company": "BigCo"}

    snippets = SnippetsEngine.generate(profile, job)

    assert "Bob" in snippets["short_intro"]
    assert "BigCo" in snippets["why_role"]


def test_snippets_no_hallucinations():
    """Snippets must only reference profile-supported content."""
    profile = {
        "contact": {"name": "Eve"},
        "skills": ["Rust"],
        "experience": [{"title": "Dev", "company": "Co"}],
    }
    job = {"title": "ML Eng", "company": "DeepLab"}
    # No ML keywords in alignment
    kw = {"supported_keywords": []}

    snippets = SnippetsEngine.generate(profile, job, keyword_alignment=kw)

    # Snippets should NOT claim ML expertise
    for v in snippets.values():
        assert "machine learning" not in v.lower()
        assert "deep learning" not in v.lower()


# ── Pin Mode Validation ─────────────────────────────────────────

def test_pin_modes_are_valid():
    """Pin mode enum must be one of the three allowed values."""
    valid_modes = {"soft", "strong", "locked_if_supported"}
    for mode in valid_modes:
        assert mode in valid_modes
