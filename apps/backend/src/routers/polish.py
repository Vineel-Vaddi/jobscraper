"""Presets, pins, resume history, snippets, saved-session routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime
import json

from src.database.database import get_db
from src.database.models import (
    User, RolePreset, ResumePin, JobSearchSession, ResumeVariant,
    Job, Profile, ApplyEvent,
)
from src.routers.auth import get_current_user
from src.schemas.polish import (
    RolePresetCreate, RolePresetUpdate, RolePresetResponse,
    ResumePinCreate, ResumePinResponse,
    SaveSessionRequest, SnippetResponse,
)
from src.services.polish.snippets_engine import SnippetsEngine

router = APIRouter(tags=["polish"])


# ── Role Presets CRUD ────────────────────────────────────────────

@router.get("/api/presets", response_model=list[RolePresetResponse])
def list_presets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    presets = db.query(RolePreset).filter(RolePreset.user_id == current_user.id).all()
    out = []
    for p in presets:
        out.append({
            "id": p.id,
            "name": p.name,
            "target_titles": json.loads(p.target_titles_json) if p.target_titles_json else [],
            "priority_skills": json.loads(p.priority_skills_json) if p.priority_skills_json else [],
            "summary_focus": p.summary_focus,
            "created_at": p.created_at,
        })
    return out


@router.post("/api/presets", response_model=RolePresetResponse)
def create_preset(
    body: RolePresetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preset = RolePreset(
        user_id=current_user.id,
        name=body.name,
        target_titles_json=json.dumps(body.target_titles),
        priority_skills_json=json.dumps(body.priority_skills),
        summary_focus=body.summary_focus,
        preference_overrides_json=json.dumps(body.preference_overrides) if body.preference_overrides else None,
        pinned_section_rules_json=json.dumps(body.pinned_section_rules) if body.pinned_section_rules else None,
    )
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return {
        "id": preset.id,
        "name": preset.name,
        "target_titles": body.target_titles,
        "priority_skills": body.priority_skills,
        "summary_focus": preset.summary_focus,
        "created_at": preset.created_at,
    }


@router.patch("/api/presets/{preset_id}", response_model=RolePresetResponse)
def update_preset(
    preset_id: int,
    body: RolePresetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preset = db.query(RolePreset).filter(
        RolePreset.id == preset_id, RolePreset.user_id == current_user.id
    ).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    if body.name is not None:
        preset.name = body.name
    if body.target_titles is not None:
        preset.target_titles_json = json.dumps(body.target_titles)
    if body.priority_skills is not None:
        preset.priority_skills_json = json.dumps(body.priority_skills)
    if body.summary_focus is not None:
        preset.summary_focus = body.summary_focus

    db.commit()
    db.refresh(preset)
    return {
        "id": preset.id,
        "name": preset.name,
        "target_titles": json.loads(preset.target_titles_json) if preset.target_titles_json else [],
        "priority_skills": json.loads(preset.priority_skills_json) if preset.priority_skills_json else [],
        "summary_focus": preset.summary_focus,
        "created_at": preset.created_at,
    }


@router.delete("/api/presets/{preset_id}")
def delete_preset(
    preset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preset = db.query(RolePreset).filter(
        RolePreset.id == preset_id, RolePreset.user_id == current_user.id
    ).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    db.delete(preset)
    db.commit()
    return {"status": "deleted"}


# ── Resume Pins CRUD ─────────────────────────────────────────────

@router.get("/api/pins", response_model=list[ResumePinResponse])
def list_pins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(ResumePin).filter(ResumePin.user_id == current_user.id).all()


@router.post("/api/pins", response_model=ResumePinResponse)
def create_pin(
    body: ResumePinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.pin_mode not in ("soft", "strong", "locked_if_supported"):
        raise HTTPException(status_code=400, detail="pin_mode must be soft, strong, or locked_if_supported")
    pin = ResumePin(
        user_id=current_user.id,
        source_type=body.source_type,
        source_ref=body.source_ref,
        label=body.label,
        pin_mode=body.pin_mode,
    )
    db.add(pin)
    db.commit()
    db.refresh(pin)
    return pin


@router.delete("/api/pins/{pin_id}")
def delete_pin(
    pin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pin = db.query(ResumePin).filter(
        ResumePin.id == pin_id, ResumePin.user_id == current_user.id
    ).first()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    db.delete(pin)
    db.commit()
    return {"status": "deleted"}


# ── Saved Sessions ───────────────────────────────────────────────

@router.patch("/api/jobs/sessions/{session_id}/save")
def save_session(
    session_id: int,
    body: SaveSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sess = db.query(JobSearchSession).filter(
        JobSearchSession.id == session_id, JobSearchSession.user_id == current_user.id
    ).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    sess.is_saved = body.is_saved
    if body.saved_label is not None:
        sess.saved_label = body.saved_label
    db.commit()
    return {"status": "ok", "is_saved": sess.is_saved}


@router.patch("/api/jobs/sessions/{session_id}/archive")
def archive_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sess = db.query(JobSearchSession).filter(
        JobSearchSession.id == session_id, JobSearchSession.user_id == current_user.id
    ).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    sess.archived_at = func.now()
    db.commit()
    return {"status": "archived"}


@router.get("/api/jobs/sessions/saved")
def get_saved_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = db.query(JobSearchSession).filter(
        JobSearchSession.user_id == current_user.id,
        JobSearchSession.is_saved == True,
        JobSearchSession.archived_at == None,
    ).order_by(JobSearchSession.updated_at.desc()).all()
    return [{
        "id": s.id,
        "source_url": s.source_url,
        "saved_label": s.saved_label,
        "status": s.status,
        "deduped_result_count": s.deduped_result_count,
        "created_at": s.created_at,
    } for s in sessions]


# ── Resume History ───────────────────────────────────────────────

@router.get("/api/resume-variants/history")
def get_resume_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    variants = db.query(ResumeVariant).filter(
        ResumeVariant.user_id == current_user.id
    ).order_by(ResumeVariant.created_at.desc()).limit(50).all()

    result = []
    for v in variants:
        job = db.query(Job).filter(Job.id == v.job_id).first()
        applied = db.query(ApplyEvent).filter(
            ApplyEvent.resume_variant_id == v.id,
            ApplyEvent.event_type == "go_apply_clicked"
        ).first()

        ats = json.loads(v.ats_score_json) if v.ats_score_json else {}
        validator = json.loads(v.validator_report_json) if v.validator_report_json else {}

        result.append({
            "id": v.id,
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "Unknown",
            "status": v.status,
            "ats_coverage": ats.get("coverage_percentage"),
            "validator_status": validator.get("status"),
            "applied": applied is not None,
            "created_at": v.created_at,
            "has_docx": v.export_docx_storage_key is not None,
            "has_pdf": v.export_pdf_storage_key is not None,
        })
    return result


# ── Snippets ─────────────────────────────────────────────────────

@router.post("/api/resume-variants/{variant_id}/snippets", response_model=SnippetResponse)
def generate_snippets(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    variant = db.query(ResumeVariant).filter(
        ResumeVariant.id == variant_id, ResumeVariant.user_id == current_user.id
    ).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    profile = db.query(Profile).filter(Profile.id == variant.profile_id).first()
    job = db.query(Job).filter(Job.id == variant.job_id).first()
    if not profile or not job:
        raise HTTPException(status_code=400, detail="Missing profile/job data")

    canonical = json.loads(profile.canonical_profile_json) if profile.canonical_profile_json else {}
    job_dict = {"title": job.title, "company": job.company}
    kw_align = json.loads(variant.keyword_alignment_json) if variant.keyword_alignment_json else {}

    snippets = SnippetsEngine.generate(canonical, job_dict, keyword_alignment=kw_align)
    return snippets


@router.get("/api/resume-variants/{variant_id}/snippets", response_model=SnippetResponse)
def get_snippets(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # For MVP, re-generate on the fly (cheap deterministic operation)
    return generate_snippets(variant_id, db, current_user)
