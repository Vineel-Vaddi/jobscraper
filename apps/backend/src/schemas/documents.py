from pydantic import BaseModel
from typing import Optional, List
import datetime

class DocumentResponse(BaseModel):
    id: int
    document_type: str
    original_filename: str
    file_size: int
    upload_status: str
    parse_status: str
    parse_error_code: Optional[str] = None
    parse_error_message: Optional[str] = None
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

class DocumentEventResponse(BaseModel):
    type: str
    details: Optional[str]
    created_at: datetime.datetime

class DocumentDetailsEmbedded(BaseModel):
    id: int
    original_filename: str
    document_type: str
    parse_status: str
    parse_error_code: Optional[str] = None
    parse_error_message: Optional[str] = None

class DocumentDetailsResponse(BaseModel):
    document: DocumentDetailsEmbedded
    extracted_text_url: Optional[str] = None
    events: List[DocumentEventResponse]
