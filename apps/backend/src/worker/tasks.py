from src.worker.celery_app import celery_app
from src.database.database import SessionLocal
from src.database.models import Document, DocumentParseEvent
from src.utils.storage import download_file_to_memory, upload_bytes_to_s3
from src.worker.parsers.pdf_parser import parse_pdf
from src.worker.parsers.docx_parser import parse_docx
from src.worker.parsers.linkedin_export_parser import parse_linkedin_export
from src.utils.logger import log
import traceback

def log_event(db, doc_id: int, event_type: str, details: str = None):
    event = DocumentParseEvent(document_id=doc_id, event_type=event_type, details=details)
    db.add(event)
    db.commit()

@celery_app.task(bind=True, max_retries=3)
def parse_document_task(self, document_id: int):
    """Downloads document from object storage, extracts text, and uploads results."""
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        db.close()
        return "Document not found"

    doc.parse_status = "processing"
    log_event(db, doc.id, "started", "Started parsing document")
    db.commit()
    
    log.info("Started document parsing task", extra={"document_id": doc.id, "user_id": doc.user_id, "task_id": self.request.id, "phase": "extraction", "status": "start"})

    try:
        # Download from S3
        log_event(db, doc.id, "downloading", f"Downloading {doc.storage_key} from MinIO")
        log.info("Downloading file from storage", extra={"document_id": doc.id, "task_id": self.request.id, "phase": "download"})
        file_bytes = download_file_to_memory(doc.storage_key)
        
        # Parse based on mimetype or type
        extracted_text = ""
        parser_used = ""
        
        if doc.mime_type == "application/pdf" or doc.original_filename.lower().endswith(".pdf"):
            parser_used = "PyMuPDF"
            extracted_text = parse_pdf(file_bytes)
        elif "wordprocessingml.document" in doc.mime_type or doc.original_filename.lower().endswith(".docx"):
            parser_used = "python-docx"
            extracted_text = parse_docx(file_bytes)
        elif "zip" in doc.mime_type or doc.original_filename.lower().endswith(".zip"):
            parser_used = "zip-csv"
            extracted_text = parse_linkedin_export(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {doc.mime_type}")
            
        # Upload extracted text back
        text_storage_key = f"{doc.storage_key}.extracted.txt"
        log_event(db, doc.id, "uploading_text", "Uploading extracted text to MinIO")
        log.info("Uploading extracted text", extra={"document_id": doc.id, "task_id": self.request.id, "phase": "upload"})
        
        text_bytes = extracted_text.encode('utf-8')
        upload_bytes_to_s3(text_bytes, text_storage_key)
        
        # Update Document
        doc.extracted_text_path = text_storage_key
        doc.parse_status = "success"
        doc.parser_confidence = f"{parser_used} (Length: {len(extracted_text)})"
        
        log_event(db, doc.id, "success", f"Successfully parsed using {parser_used}")
        log.info("Document parsing complete", extra={"document_id": doc.id, "task_id": self.request.id, "phase": "extraction", "status": "success"})
        db.commit()
        return "Success"

    except ValueError as e:
        # Expected parsing errors like password-protected, encrypted, or empty
        db.rollback()
        doc.parse_status = "failed"
        doc.parse_error_code = "PARSE_ERROR"
        doc.parse_error_message = str(e)
        log_event(db, doc.id, "failed", f"Parse ValueError: {str(e)}")
        log.warning("Document parsing failed", extra={"document_id": doc.id, "task_id": self.request.id, "phase": "extraction", "status": "failed", "error_code": "PARSE_ERROR"})
        db.commit()
        return f"Failed: {str(e)}"
        
    except Exception as e:
        # Unexpected errors (time limits, S3 failures, etc)
        db.rollback()
        doc.parse_status = "failed"
        doc.parse_error_code = "SYSTEM_ERROR"
        doc.parse_error_message = "An unexpected error occurred during parsing."
        log_event(db, doc.id, "failed", f"System Exception: {str(e)}\n{traceback.format_exc()}")
        log.error("Document parsing system exception", extra={"document_id": doc.id, "task_id": self.request.id, "phase": "extraction", "status": "failed", "error_code": "SYSTEM_ERROR"})
        db.commit()
        
        # Retry logic if it's transient (s3 download failed, etc)
        try:
            self.retry(countdown=2 ** self.request.retries)
        except self.MaxRetriesExceededError:
            pass
            
        return f"Failed: {str(e)}"
        
    finally:
        db.close()
