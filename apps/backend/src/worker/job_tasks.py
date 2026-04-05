from src.worker.celery_app import celery_app
from src.database.database import SessionLocal
from src.database.models import JobSearchSession, Job, Profile
from src.utils.logger import log
import json

from src.worker.job_extractors.linkedin_extractor import LinkedinJobExtractor
from src.worker.job_normalizer import JobNormalizer
from src.worker.job_dedupe import JobDeduper
from src.worker.job_scorer import JobScorer

@celery_app.task(bind=True, max_retries=3)
def process_job_session_task(self, session_id: int):
    log.info(f"Processing job session: {session_id}")
    db = SessionLocal()
    session = db.query(JobSearchSession).filter(JobSearchSession.id == session_id).first()
    
    if not session:
        db.close()
        return "Session not found"
        
    session.status = "processing"
    db.commit()
    
    try:
        # Load user profile
        profile = db.query(Profile).filter(Profile.user_id == session.user_id).first()
        profile_json_str = profile.canonical_profile_json if profile else None
        
        # 1. Extract
        extractor = LinkedinJobExtractor()
        raw_jobs = extractor.extract_jobs(session.source_url)
        session.raw_result_count = len(raw_jobs)
        
        seen_dedupe_keys = set()
        deduped_count = 0
        normalized_count = 0
        
        jobs_to_insert = []
        
        for raw_job in raw_jobs:
            # 2. Normalize
            normalized = JobNormalizer.normalize_job(raw_job)
            normalized_count += 1
            
            # 3. Dedupe
            dedupe_key = JobDeduper.generate_dedupe_key(normalized)
            if dedupe_key in seen_dedupe_keys:
                continue
                
            # Check DB for existing dedupe key for this user
            existing_job = db.query(Job).filter(Job.user_id == session.user_id, Job.dedupe_key == dedupe_key).first()
            if existing_job:
                continue
                
            seen_dedupe_keys.add(dedupe_key)
            deduped_count += 1
            
            # 4. Score
            scored = JobScorer.score_job(normalized, profile_json_str)
            
            # Prepare DB Model
            job_obj = Job(
                user_id=session.user_id,
                job_search_session_id=session.id,
                external_job_id=scored.get('external_job_id'),
                source_type="linkedin_search_url",
                source_job_url=scored.get('source_job_url'),
                canonical_job_url=scored.get('canonical_job_url'),
                title=scored.get('title'),
                company=scored.get('company'),
                location=scored.get('location'),
                work_mode=scored.get('work_mode'),
                employment_type=scored.get('employment_type'),
                seniority=scored.get('seniority'),
                posted_at_raw=scored.get('posted_at_raw'),
                posted_at_normalized=scored.get('posted_at_normalized'),
                description_text=scored.get('description_text'),
                requirements_json=json.dumps(scored.get('requirements_json')) if scored.get('requirements_json') else None,
                metadata_json=json.dumps(scored.get('metadata_json')) if scored.get('metadata_json') else None,
                normalization_confidence=scored.get('normalization_confidence'),
                dedupe_key=dedupe_key,
                fit_score=scored.get('fit_score'),
                fit_reasons_json=scored.get('fit_reasons_json'),
                fit_gaps_json=scored.get('fit_gaps_json')
            )
            jobs_to_insert.append(job_obj)
            
        if jobs_to_insert:
            db.add_all(jobs_to_insert)
            
        session.normalized_result_count = normalized_count
        session.deduped_result_count = deduped_count
        session.status = "success"
        db.commit()
    except Exception as e:
        db.rollback()
        session.status = "failed"
        session.ingest_error_message = str(e)
        session.ingest_error_code = "PIPELINE_ERROR"
        log.error(f"Pipeline error for session {session_id}: {str(e)}")
        db.commit()
    finally:
        db.close()

