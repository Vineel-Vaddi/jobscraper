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

    class Config:
        from_attributes = True
