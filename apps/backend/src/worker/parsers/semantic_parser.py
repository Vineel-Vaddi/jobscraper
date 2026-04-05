from src.utils.gemini_client import generate_profile_json
from src.utils.logger import log

def parse_with_gemini(document_id: int, extracted_text: str, document_type: str) -> dict:
    """
    Given raw extracted text, convert to semantic JSON using Gemini.
    """
    log.info("Starting semantic extraction", extra={"document_id": document_id, "document_type": document_type, "phase": "semantic_extract"})
    
    parsed_json = generate_profile_json(extracted_text)
    
    if parsed_json:
        log.info("Semantic extraction successful", extra={"document_id": document_id, "phase": "semantic_extract", "status": "success"})
    else:
        log.warning("Semantic extraction failed to return valid JSON", extra={"document_id": document_id, "phase": "semantic_extract", "status": "failed"})
        
    return parsed_json or {}
