"""Pydantic schemas for Phase 7 polish features."""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


# ── Profile Preferences ──────────────────────────────────────────
class ProfilePreferenceUpdate(BaseModel):
    preferred_locations: Optional[list[str]] = None
    preferred_work_modes: Optional[list[str]] = None
    preferred_employment_types: Optional[list[str]] = None
    target_seniority: Optional[str] = None
    preferred_industries: Optional[list[str]] = None
    salary_notes: Optional[str] = None
    exclude_keywords: Optional[list[str]] = None
    resume_emphasis: Optional[str] = None


class ProfilePreferenceResponse(BaseModel):
    id: int
    preferred_locations: list[str] = []
    preferred_work_modes: list[str] = []
    preferred_employment_types: list[str] = []
    target_seniority: Optional[str] = None
    preferred_industries: list[str] = []
    salary_notes: Optional[str] = None
    exclude_keywords: list[str] = []
    resume_emphasis: Optional[str] = None

    class Config:
        from_attributes = True


# ── Role Presets ─────────────────────────────────────────────────
class RolePresetCreate(BaseModel):
    name: str
    target_titles: list[str] = []
    priority_skills: list[str] = []
    summary_focus: Optional[str] = None
    preference_overrides: Optional[dict[str, Any]] = None
    pinned_section_rules: Optional[dict[str, Any]] = None


class RolePresetUpdate(BaseModel):
    name: Optional[str] = None
    target_titles: Optional[list[str]] = None
    priority_skills: Optional[list[str]] = None
    summary_focus: Optional[str] = None
    preference_overrides: Optional[dict[str, Any]] = None
    pinned_section_rules: Optional[dict[str, Any]] = None


class RolePresetResponse(BaseModel):
    id: int
    name: str
    target_titles: list[str] = []
    priority_skills: list[str] = []
    summary_focus: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Resume Pins ──────────────────────────────────────────────────
class ResumePinCreate(BaseModel):
    source_type: str          # profile_section, experience_bullet, project, summary_line, skill_cluster
    source_ref: str           # text or key identifying the content
    label: Optional[str] = None
    pin_mode: str = "locked_if_supported"  # soft | strong | locked_if_supported


class ResumePinResponse(BaseModel):
    id: int
    source_type: str
    source_ref: str
    label: Optional[str] = None
    pin_mode: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Saved Sessions ───────────────────────────────────────────────
class SaveSessionRequest(BaseModel):
    is_saved: bool = True
    saved_label: Optional[str] = None


# ── Suggested Titles ─────────────────────────────────────────────
class SuggestedTitle(BaseModel):
    title: str
    confidence: str
    rationale: str


# ── Snippets ─────────────────────────────────────────────────────
class SnippetResponse(BaseModel):
    short_intro: str
    why_fit: str
    why_role: str
    recruiter_note: str
