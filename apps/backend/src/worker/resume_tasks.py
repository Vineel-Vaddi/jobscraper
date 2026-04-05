import logging
import json
import traceback
from src.database.database import SessionLocal
from src.database.models import ResumeVariant, Job, Profile
from celery import shared_task

from .tailoring.jd_parser import JDParser
from .tailoring.skill_gap import SkillGapAnalyzer, KeywordAligner
from .tailoring.rewrite_engine import RewriteEngine
from .tailoring.validator import ResumeValidator
from .tailoring.ats_scorer import ATSScorer
from .tailoring.exporter import ResumeExporter

logger = logging.getLogger(__name__)

@shared_task(name="process_resume_tailoring_task")
def process_resume_tailoring_task(variant_id: int):
    db = SessionLocal()
    try:
        variant = db.query(ResumeVariant).filter(ResumeVariant.id == variant_id).first()
        if not variant:
            logger.error(f"ResumeVariant {variant_id} not found.")
            return

        variant.status = "processing"
        db.commit()

        job = db.query(Job).filter(Job.id == variant.job_id).first()
        profile = db.query(Profile).filter(Profile.id == variant.profile_id).first()
        
        canonical_json = json.loads(profile.canonical_profile_json) if profile.canonical_profile_json else {}

        # 1. JD Parser
        jd_summary = JDParser.parse_jd(job)
        variant.jd_summary_json = json.dumps(jd_summary)
        
        # 2. Skill Gap & Alignment
        skill_gap = SkillGapAnalyzer.analyze(jd_summary, canonical_json)
        keyword_alignment = KeywordAligner.align(jd_summary, skill_gap)
        variant.skill_gap_json = json.dumps(skill_gap)
        variant.keyword_alignment_json = json.dumps(keyword_alignment)
        
        # 3. Rewrite Engine
        tailored_resume = RewriteEngine.rewrite(canonical_json, jd_summary, keyword_alignment)
        variant.tailored_resume_json = json.dumps(tailored_resume)
        
        # 4. Validator
        validator_report = ResumeValidator.validate(tailored_resume, canonical_json)
        variant.validator_report_json = json.dumps(validator_report)
        
        if validator_report.get("status") == "fail":
            variant.status = "needs_review"
            
        # 5. ATS Scoring
        ats_score = ATSScorer.score(jd_summary, tailored_resume)
        variant.ats_score_json = json.dumps(ats_score)
        
        # 6. Exporter
        try:
            docx_key, pdf_key = ResumeExporter.export_all(tailored_resume, variant.id)
            variant.export_docx_storage_key = docx_key
            variant.export_pdf_storage_key = pdf_key
        except Exception as e:
            logger.error(f"Export failed for variant {variant_id}: {e}")
            
        if variant.status != "needs_review":
            variant.status = "success"
            
        db.commit()
    except Exception as e:
        logger.error(f"Tailoring failed for variant {variant_id}: {e}")
        db.rollback()
        
        variant_fail = db.query(ResumeVariant).filter(ResumeVariant.id == variant_id).first()
        if variant_fail:
            variant_fail.status = "failed"
            variant_fail.error_message = traceback.format_exc()
            db.commit()
    finally:
        db.close()
