import logging
import functools
import traceback
from requests.exceptions import Timeout, ConnectionError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class NonRetryableException(Exception):
    """
    Exceptions known to be terminal (e.g. invalid document format).
    """
    pass

def with_db_retry(max_retries=3):
    """
    A unified decorator for Celely tasks trapping specific transient
    failures vs definitive data faults. Binds directly to the AgentRun.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                # Log execution start securely
                logger.info(f"Executing task {self.name} [ID: {self.request.id}]")
                return func(self, *args, **kwargs)
                
            except NonRetryableException as e:
                # E.g. Corrupted Document, Truth-Validator hard failures.
                logger.error(f"Task {self.name} failed definitively: {str(e)}")
                self.update_state(state='FAILURE', meta={'exc_type': 'NonRetryableException', 'exc_message': str(e)})
                raise e # Celery auto-stops if we disable backoff here or we just raise without celery retry logic
                
            except (Timeout, ConnectionError) as e:
                # Transient network boundaries
                retries = self.request.retries
                logger.warning(f"Transient error in {self.name}: {str(e)}. Attempt {retries}/{max_retries}")
                if retries >= max_retries:
                    logger.error(f"Max retries exhausted for {self.name}.")
                    raise e
                raise self.retry(exc=e, countdown=2 ** retries) # Exponential backoff
                
            except Exception as e:
                # Catch-all
                logger.exception(f"Unexpected failure in {self.name}: {str(e)}")
                raise self.retry(exc=e, countdown=60, max_retries=1) # One safe generic retry
                
        return wrapper
    return decorator
