from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class CreateTailoredResumeRequest(BaseModel):
    job_id: int

class ResumeVariantResponse(BaseModel):
    id: int
    user_id: int
    profile_id: Optional[int]
    job_id: Optional[int]
    base_document_id: Optional[int]
    
    status: str
    
    jd_summary_json: Optional[Dict[str, Any]] = None
    keyword_alignment_json: Optional[Dict[str, Any]] = None
    skill_gap_json: Optional[Dict[str, Any]] = None
    tailored_resume_json: Optional[Dict[str, Any]] = None
    tailored_resume_text: Optional[str] = None
    validator_report_json: Optional[Dict[str, Any]] = None
    ats_score_json: Optional[Dict[str, Any]] = None
    
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None


class ApplyEventCreate(BaseModel):
    event_type: str
    metadata_json: Optional[Dict[str, Any]] = None

class ApplyEventResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    resume_variant_id: int
    event_type: str
    target_url: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class BulletDiff(BaseModel):
    text: str
    type: str # unchanged, added, removed, rewritten

class SectionDiff(BaseModel):
    section_name: str
    status: str
    bullets: list[BulletDiff]

class ReviewPayloadResponse(BaseModel):
    base_resume_summary: Dict[str, Any]
    tailored_resume_summary: Dict[str, Any]
    section_diffs: list[SectionDiff]
    why_changed_notes: list[str]
    validator_summary: Dict[str, Any]
    ats_summary: Dict[str, Any]
    original_job_url: Optional[str] = None
