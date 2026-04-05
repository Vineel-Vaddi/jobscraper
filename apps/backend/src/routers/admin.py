from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
import prometheus_client
import json

from src.database.database import get_db, SessionLocal
from src.database.models import User, AgentRun, Job, ResumeVariant
from src.routers.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

def check_is_admin(user: User):
    # MVP: Currently any user can access local debug since we are in dev/staging.
    # In prod, this would check user.role == 'admin'.
    return True

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/health/deep")
def deep_health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"failed: {e}"
        
    # In a full setup we'd also ping Redis explicitly 
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status
    }

@router.get("/metrics")
def get_metrics():
    """
    Exposes raw prometheus metrics.
    We don't restrict this tightly in MVP so docker prometheus can scrape easily.
    """
    return Response(
        content=prometheus_client.generate_latest(),
        media_type=prometheus_client.CONTENT_TYPE_LATEST
    )

@router.get("/runs")
def get_recent_runs(
    limit: int = 50,
    run_type: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user)
    
    query = db.query(AgentRun)
    if run_type:
        query = query.filter(AgentRun.run_type == run_type)
    if status:
        query = query.filter(AgentRun.status == status)
        
    runs = query.order_by(AgentRun.started_at.desc()).limit(limit).all()
    
    # Quick serialization MVP
    return [{
        "id": r.id,
        "run_type": r.run_type,
        "target_entity_type": r.target_entity_type,
        "target_entity_id": r.target_entity_id,
        "status": r.status,
        "duration_ms": r.duration_ms,
        "error_code": r.error_code,
        "error_message": r.error_message,
        "started_at": r.started_at,
        "finished_at": r.finished_at,
        "metadata_json": json.loads(r.metadata_json) if r.metadata_json else {}
    } for r in runs]
    
@router.get("/system-summary")
def get_system_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user)
    
    total_jobs = db.query(func.count(Job.id)).scalar()
    total_variants = db.query(func.count(ResumeVariant.id)).scalar()
    
    failed_runs = db.query(func.count(AgentRun.id)).filter(AgentRun.status == "failed").scalar()
    success_runs = db.query(func.count(AgentRun.id)).filter(AgentRun.status == "success").scalar()
    
    return {
        "total_jobs": total_jobs,
        "total_variants": total_variants,
        "failed_runs": failed_runs,
        "success_runs": success_runs
    }
