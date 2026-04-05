import json
from src.worker.celery_app import celery_app
from src.database.database import SessionLocal
from src.database.models import Document, Profile
from src.utils.logger import log
from src.utils.storage import download_file_to_memory
from src.worker.parsers.semantic_parser import parse_with_gemini
from src.worker.profile_merger import merge_profiles

@celery_app.task(bind=True, max_retries=1)
def build_profile_task(self, user_id: int):
    db = SessionLocal()
    try:
        # Get profile or create
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            profile = Profile(user_id=user_id, status="building")
            db.add(profile)
        else:
            profile.status = "building"
        db.commit()

        log.info("Starting profile build", extra={"user_id": user_id, "task_id": self.request.id})

        # Fetch successful documents for user
        docs = db.query(Document).filter(Document.user_id == user_id, Document.parse_status == "success").all()
        
        parsed_data = []
        for doc in docs:
            # Download extracted text
            if not doc.extracted_text_path:
                continue
                
            text_bytes = download_file_to_memory(doc.extracted_text_path)
            extracted_text = text_bytes.decode('utf-8')
            
            # Semantic parsing via Gemini
            doc_type = doc.document_type or "unknown" # e.g. resume, linkedin_pdf
            if getattr(doc, "mime_type", "") and "zip" in doc.mime_type:
                doc_type = "linkedin_export"
            elif doc.original_filename and doc.original_filename.lower().endswith(".pdf"):
                doc_type = "resume" if not "linkedin" in doc.original_filename.lower() else "linkedin_pdf"

            json_resp = parse_with_gemini(doc.id, extracted_text, doc_type)
            if json_resp:
                parsed_data.append({
                    "document_id": doc.id,
                    "document_type": doc_type,
                    "json": json_resp
                })

        if not parsed_data:
            profile.status = "failed"
            profile.confidence_summary_json = json.dumps({"error": "No parseable valid documents."})
            db.commit()
            return "No documents mapped."

        # Merge them
        merged_json, conf_summary = merge_profiles(parsed_data)
        
        profile.canonical_profile_json = json.dumps(merged_json)
        profile.confidence_summary_json = json.dumps(conf_summary)
        profile.merged_from_document_ids = json.dumps(merged_json["metadata"]["source_documents"])
        profile.status = "success"
        
        db.commit()
        log.info("Profile build complete", extra={"user_id": user_id, "status": "success"})
        return "Success"

    except Exception as e:
        log.error("Profile build failed", extra={"user_id": user_id, "error": str(e)})
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if profile:
            profile.status = "failed"
            db.commit()
        raise e
    finally:
        db.close()
