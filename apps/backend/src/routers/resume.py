from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List
import os

from src.database.database import get_db
from src.database.models import User, ResumeVariant, Job, Profile, Document, ApplyEvent
from src.routers.auth import get_current_user
from src.schemas.resume import CreateTailoredResumeRequest, ResumeVariantResponse, ReviewPayloadResponse, ApplyEventCreate, ApplyEventResponse
from src.services.review.diff_engine import DiffEngine
from src.services.review.why_changed import WhyChangedGenerator
import json

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

@router.get("/{variant_id}/review", response_model=ReviewPayloadResponse)
def get_variant_review_data(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    variant = db.query(ResumeVariant).filter(ResumeVariant.id == variant_id, ResumeVariant.user_id == current_user.id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
        
    profile = db.query(Profile).filter(Profile.id == variant.profile_id).first()
    job = db.query(Job).filter(Job.id == variant.job_id).first()
    
    canonical_json = json.loads(profile.canonical_profile_json) if profile and profile.canonical_profile_json else {}
    tailored_json = json.loads(variant.tailored_resume_json) if variant.tailored_resume_json else {}
    
    diffs = DiffEngine.compute_diff(canonical_json, tailored_json)
    
    kw_align = json.loads(variant.keyword_alignment_json) if variant.keyword_alignment_json else {}
    skill_gaps = json.loads(variant.skill_gap_json) if variant.skill_gap_json else {}
    validator = json.loads(variant.validator_report_json) if variant.validator_report_json else {}
    
    notes = WhyChangedGenerator.generate_notes(kw_align, skill_gaps, validator)
    
    return {
        "base_resume_summary": canonical_json,
        "tailored_resume_summary": tailored_json,
        "section_diffs": diffs,
        "why_changed_notes": notes,
        "validator_summary": validator,
        "ats_summary": json.loads(variant.ats_score_json) if variant.ats_score_json else {},
        "original_job_url": job.source_job_url if job else None
    }

@router.post("/{variant_id}/events", response_model=ApplyEventResponse)
def log_apply_event(
    variant_id: int,
    request: ApplyEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    variant = db.query(ResumeVariant).filter(ResumeVariant.id == variant_id, ResumeVariant.user_id == current_user.id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
        
    event = ApplyEvent(
        user_id=current_user.id,
        job_id=variant.job_id,
        resume_variant_id=variant.id,
        event_type=request.event_type,
        metadata_json=json.dumps(request.metadata_json) if request.metadata_json else None
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.post("/{variant_id}/go-apply")
def trigger_go_apply(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    variant = db.query(ResumeVariant).filter(ResumeVariant.id == variant_id, ResumeVariant.user_id == current_user.id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
        
    job = db.query(Job).filter(Job.id == variant.job_id).first()
    target = job.source_job_url if job else ""
    
    event = ApplyEvent(
        user_id=current_user.id,
        job_id=variant.job_id,
        resume_variant_id=variant.id,
        event_type="go_apply_clicked",
        target_url=target
    )
    db.add(event)
    db.commit()
    
    return {"status": "ok", "target_url": target}
