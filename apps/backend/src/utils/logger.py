import json
import logging
from datetime import datetime, timezone
import uuid
import sys

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
            "document_id": getattr(record, "document_id", None),
            "task_id": getattr(record, "task_id", None),
            "phase": getattr(record, "phase", None),
            "status": getattr(record, "status", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "error_code": getattr(record, "error_code", None),
        }
        
        # Remove empty keys for cleaner logs
        log_record = {k: v for k, v in log_record.items() if v is not None}
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def get_logger(name="jobtailor"):
    logger = logging.getLogger(name)
    
    # Only configure if no handlers exist specifically to avoid duplicate logs in uvicorn
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
    return logger

# Single generic instance
log = get_logger()
