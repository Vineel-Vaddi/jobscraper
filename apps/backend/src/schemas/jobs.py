from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobIntakeRequest(BaseModel):
    source_url: HttpUrl

class JobSearchSessionBase(BaseModel):
    source_url: str
    source_type: str
    status: str
    ingest_error_code: Optional[str] = None
    ingest_error_message: Optional[str] = None
    raw_result_count: int
    normalized_result_count: int
    deduped_result_count: int
    created_at: datetime

class JobSearchSessionResponse(JobSearchSessionBase):
    id: int

    class Config:
        from_attributes = True

class JobBase(BaseModel):
    job_search_session_id: int
    external_job_id: Optional[str] = None
    source_type: str
    source_job_url: str
    canonical_job_url: Optional[str] = None
    
    title: str
    company: str
    location: Optional[str] = None
    work_mode: Optional[str] = None
    employment_type: Optional[str] = None
    seniority: Optional[str] = None
    
    posted_at_raw: Optional[str] = None
    posted_at_normalized: Optional[datetime] = None
    
    description_text: Optional[str] = None
    requirements_json: Optional[Dict[str, Any]] = None
    metadata_json: Optional[Dict[str, Any]] = None
    
    normalization_confidence: Optional[str] = None
    fit_score: Optional[int] = None
    fit_reasons_json: Optional[str] = None
    fit_gaps_json: Optional[str] = None

class JobResponse(JobBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
