from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ProfileResponse(BaseModel):
    id: int
    status: str
    canonical_profile_json: Optional[Dict[str, Any]] = None
    confidence_summary_json: Optional[Dict[str, Any]] = None
    merged_from_document_ids: Optional[List[int]] = None
    
    class Config:
        from_attributes = True

class ProfileUpdateRequest(BaseModel):
    canonical_profile_json: Dict[str, Any]
