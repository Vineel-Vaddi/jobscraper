from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List
import os

from src.database.database import get_db
from src.database.models import User, ResumeVariant, Job, Profile, Document
from src.routers.auth import get_current_user
from src.schemas.resume import CreateTailoredResumeRequest, ResumeVariantResponse

router = APIRouter(prefix="/api/resume-variants", tags=["resume"])

@router.post("/generate", response_model=ResumeVariantResponse)
def create_resume_variant(
    request: CreateTailoredResumeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve job
    job = db.query(Job).filter(Job.id == request.job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Retrieve canonical profile
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Profile must be generated before tailoring")
        
    # Get latest successful document as a base if it exists
    base_document = db.query(Document)\
        .filter(Document.user_id == current_user.id, Document.status == "success")\
        .order_by(Document.created_at.desc())\
        .first()
        
    base_document_id = base_document.id if base_document else None

    variant = ResumeVariant(
        user_id=current_user.id,
        profile_id=profile.id,
        job_id=job.id,
        base_document_id=base_document_id,
        status="pending"
    )
    
    db.add(variant)
    db.commit()
    db.refresh(variant)
    
    # Trigger celery task
    from src.worker.resume_tasks import process_resume_tailoring_task
    process_resume_tailoring_task.delay(variant.id)
    
    return variant

@router.get("", response_model=List[ResumeVariantResponse])
def get_resume_variants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    variants = db.query(ResumeVariant)\
        .filter(ResumeVariant.user_id == current_user.id)\
        .order_by(ResumeVariant.created_at.desc())\
        .all()
    return variants

@router.get("/{variant_id}", response_model=ResumeVariantResponse)
def get_resume_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    variant = db.query(ResumeVariant)\
        .filter(ResumeVariant.id == variant_id, ResumeVariant.user_id == current_user.id)\
        .first()
        
    if not variant:
        raise HTTPException(status_code=404, detail="Resume Variant not found")
        
    return variant

@router.get("/{variant_id}/download/docx")
def download_resume_docx(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    variant = db.query(ResumeVariant).filter(ResumeVariant.id == variant_id, ResumeVariant.user_id == current_user.id).first()
    if not variant or variant.status != "success" or not variant.export_docx_storage_key:
        raise HTTPException(status_code=404, detail="DOCX not ready or not found")
        
    # Standard MinIO fallback / Mock Read block
    file_path = f"/tmp/{variant.export_docx_storage_key}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="DOCX file not found on disk")
        
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    headers = {
        'Content-Disposition': f'attachment; filename="Tailored_Resume_{variant.id}.docx"'
    }
    return Response(content=file_bytes, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', headers=headers)

@router.get("/{variant_id}/download/pdf")
def download_resume_pdf(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    variant = db.query(ResumeVariant).filter(ResumeVariant.id == variant_id, ResumeVariant.user_id == current_user.id).first()
    if not variant or variant.status != "success" or not variant.export_pdf_storage_key:
        raise HTTPException(status_code=404, detail="PDF not ready or not found")
        
    file_path = f"/tmp/{variant.export_pdf_storage_key}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
        
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    headers = {
        'Content-Disposition': f'attachment; filename="Tailored_Resume_{variant.id}.pdf"'
    }
    return Response(content=file_bytes, media_type='application/pdf', headers=headers)
