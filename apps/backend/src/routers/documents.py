from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from typing import List
from pydantic import BaseModel
import datetime

from src.database.database import get_db
from src.database.models import User, Document, DocumentParseEvent
from src.routers.auth import get_current_user
from src.utils.storage import upload_file_to_s3, get_file_url
# We will import the celery task once it's created
from src.worker.tasks import parse_document_task
from src.utils.logger import log

router = APIRouter(prefix="/api/documents", tags=["documents"])

from src.schemas.documents import DocumentResponse, DocumentDetailsResponse

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Uploads a document to S3, writes it to DB, and triggers parse job."""
    
    log.info("Starting document upload", extra={"user_id": user.id, "phase": "upload", "status": "start"})
    
    ALLOWED_TYPES = ["resume", "linkedin_pdf", "linkedin_export"]
    if document_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid document type")

    # Read size (resetting stream)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    MAX_SIZE = 50 * 1024 * 1024 # 50 MB
    if file_size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # Upload to S3
    prefix = f"{user.id}/{document_type}/"
    storage_key = upload_file_to_s3(file, prefix=prefix)
    
    # Write DB Metadata
    new_doc = Document(
        user_id=user.id,
        document_type=document_type,
        original_filename=file.filename,
        mime_type=file.content_type,
        file_size=file_size,
        storage_key=storage_key,
        upload_status="success",
        parse_status="pending"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # Enqueue Parse Task
    task = parse_document_task.delay(new_doc.id)
    
    log.info("Document successfully uploaded and task queued", extra={
        "user_id": user.id, 
        "document_id": new_doc.id, 
        "task_id": task.id,
        "phase": "upload", 
        "status": "success"
    })
    
    return new_doc

@router.get("", response_model=List[DocumentResponse])
async def list_documents(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Returns list of all documents uploaded by the user."""
    docs = db.query(Document).filter(Document.user_id == user.id).order_by(Document.created_at.desc()).all()
    return docs

@router.get("/{doc_id}", response_model=DocumentDetailsResponse)
async def get_document_details(doc_id: int, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Returns details of a specific document including events and a temp URL for raw text."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    events = db.query(DocumentParseEvent).filter(DocumentParseEvent.document_id == doc.id).order_by(DocumentParseEvent.created_at.asc()).all()
    
    extracted_text_url = None
    if doc.extracted_text_path:
        extracted_text_url = get_file_url(doc.extracted_text_path)
        
    return {
        "document": {
            "id": doc.id,
            "original_filename": doc.original_filename,
            "document_type": doc.document_type,
            "parse_status": doc.parse_status,
            "parse_error_code": doc.parse_error_code,
            "parse_error_message": doc.parse_error_message,
        },
        "extracted_text_url": extracted_text_url,
        "events": [{"type": e.event_type, "details": e.details, "created_at": e.created_at} for e in events]
    }
