from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database.models import User, Profile
from src.schemas.profiles import ProfileResponse, ProfileUpdateRequest
from src.routers.auth import get_current_user
from src.worker.profile_tasks import build_profile_task
from src.utils.logger import log
import json

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.post("/build")
def build_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Triggers the profile builder celery task."""
    build_profile_task.delay(current_user.id)
    log.info("Profile build task submitted", extra={"user_id": current_user.id})
    return {"message": "Profile build started"}

@router.get("", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve the current canonical profile."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found or not built yet")
        
    return {
        "id": profile.id,
        "status": profile.status,
        "canonical_profile_json": json.loads(profile.canonical_profile_json) if profile.canonical_profile_json else None,
        "confidence_summary_json": json.loads(profile.confidence_summary_json) if profile.confidence_summary_json else None,
        "merged_from_document_ids": json.loads(profile.merged_from_document_ids) if profile.merged_from_document_ids else None
    }

@router.patch("", response_model=ProfileResponse)
def update_profile(update_req: ProfileUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Used for saving manual corrections to the canonical profile."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    profile.canonical_profile_json = json.dumps(update_req.canonical_profile_json)
    db.commit()
    db.refresh(profile)
    log.info("Profile manually updated", extra={"user_id": current_user.id})
    
    return {
        "id": profile.id,
        "status": profile.status,
        "canonical_profile_json": json.loads(profile.canonical_profile_json) if profile.canonical_profile_json else None,
        "confidence_summary_json": json.loads(profile.confidence_summary_json) if profile.confidence_summary_json else None,
        "merged_from_document_ids": json.loads(profile.merged_from_document_ids) if profile.merged_from_document_ids else None
    }
