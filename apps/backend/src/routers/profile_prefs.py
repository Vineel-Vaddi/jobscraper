"""Profile preferences + suggested titles router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from src.database.database import get_db
from src.database.models import User, Profile, ProfilePreference
from src.routers.auth import get_current_user
from src.schemas.polish import (
    ProfilePreferenceUpdate, ProfilePreferenceResponse,
    SuggestedTitle,
)
from src.services.polish.titles_engine import TitlesEngine

router = APIRouter(prefix="/api/profile", tags=["profile-prefs"])


def _pref_to_response(pref: ProfilePreference) -> dict:
    """Deserialize JSON columns into the response shape."""
    return {
        "id": pref.id,
        "preferred_locations": json.loads(pref.preferred_locations_json) if pref.preferred_locations_json else [],
        "preferred_work_modes": json.loads(pref.preferred_work_modes_json) if pref.preferred_work_modes_json else [],
        "preferred_employment_types": json.loads(pref.preferred_employment_types_json) if pref.preferred_employment_types_json else [],
        "target_seniority": pref.target_seniority,
        "preferred_industries": json.loads(pref.preferred_industries_json) if pref.preferred_industries_json else [],
        "salary_notes": pref.salary_notes,
        "exclude_keywords": json.loads(pref.exclude_keywords_json) if pref.exclude_keywords_json else [],
        "resume_emphasis": pref.resume_emphasis,
    }


@router.get("/preferences", response_model=ProfilePreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = db.query(ProfilePreference).filter(ProfilePreference.user_id == current_user.id).first()
    if not pref:
        # Auto-create empty prefs
        pref = ProfilePreference(user_id=current_user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return _pref_to_response(pref)


@router.patch("/preferences", response_model=ProfilePreferenceResponse)
def update_preferences(
    body: ProfilePreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = db.query(ProfilePreference).filter(ProfilePreference.user_id == current_user.id).first()
    if not pref:
        pref = ProfilePreference(user_id=current_user.id)
        db.add(pref)
        db.flush()

    if body.preferred_locations is not None:
        pref.preferred_locations_json = json.dumps(body.preferred_locations)
    if body.preferred_work_modes is not None:
        pref.preferred_work_modes_json = json.dumps(body.preferred_work_modes)
    if body.preferred_employment_types is not None:
        pref.preferred_employment_types_json = json.dumps(body.preferred_employment_types)
    if body.target_seniority is not None:
        pref.target_seniority = body.target_seniority
    if body.preferred_industries is not None:
        pref.preferred_industries_json = json.dumps(body.preferred_industries)
    if body.salary_notes is not None:
        pref.salary_notes = body.salary_notes
    if body.exclude_keywords is not None:
        pref.exclude_keywords_json = json.dumps(body.exclude_keywords)
    if body.resume_emphasis is not None:
        pref.resume_emphasis = body.resume_emphasis

    db.commit()
    db.refresh(pref)
    return _pref_to_response(pref)


@router.get("/suggested-titles", response_model=list[SuggestedTitle])
def get_suggested_titles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile or not profile.canonical_profile_json:
        raise HTTPException(status_code=400, detail="Build a profile first")

    canonical = json.loads(profile.canonical_profile_json)

    pref = db.query(ProfilePreference).filter(ProfilePreference.user_id == current_user.id).first()
    pref_dict = _pref_to_response(pref) if pref else None

    return TitlesEngine.suggest(canonical, pref_dict)
