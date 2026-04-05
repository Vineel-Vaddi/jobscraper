from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from src.database.database import get_db
from src.database.models import User, JobSearchSession, Job
from src.routers.auth import get_current_user
from src.schemas.jobs import JobIntakeRequest, JobSearchSessionResponse, JobResponse
import importlib

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/intake", response_model=JobSearchSessionResponse)
def create_job_intake_session(
    request: JobIntakeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    source_url_str = str(request.source_url)
    
    # 1. Create DB session
    session = JobSearchSession(
        user_id=current_user.id,
        source_url=source_url_str,
        source_type="linkedin_search_url",
        status="pending"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # 2. Trigger Celery Task
    # Importing here to prevent circular imports if needed, though usually safe
    from src.worker.job_tasks import process_job_session_task
    process_job_session_task.delay(session.id)
    
    return session

@router.get("/sessions", response_model=List[JobSearchSessionResponse])
def get_job_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(JobSearchSession)\
        .filter(JobSearchSession.user_id == current_user.id)\
        .order_by(JobSearchSession.created_at.desc())\
        .all()
    return sessions

@router.get("/sessions/{session_id}", response_model=JobSearchSessionResponse)
def get_job_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(JobSearchSession)\
        .filter(JobSearchSession.id == session_id, JobSearchSession.user_id == current_user.id)\
        .first()
        
    if not session:
        raise HTTPException(status_code=404, detail="Job search session not found")
        
    return session

@router.get("/sessions/{session_id}/jobs", response_model=List[JobResponse])
def get_jobs_for_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session ownership
    session = db.query(JobSearchSession)\
        .filter(JobSearchSession.id == session_id, JobSearchSession.user_id == current_user.id)\
        .first()
        
    if not session:
        raise HTTPException(status_code=404, detail="Job search session not found")
        
    jobs = db.query(Job)\
        .filter(Job.job_search_session_id == session_id)\
        .order_by(Job.fit_score.desc().nullslast())\
        .all()
        
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job)\
        .filter(Job.id == job_id, Job.user_id == current_user.id)\
        .first()
        
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return job
