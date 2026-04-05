import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from src.telemetry.metrics import http_requests_total, http_request_duration_seconds

logger = logging.getLogger(__name__)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        method = request.method
        # Simplify endpoint to avoid exploding cardinality (e.g. /api/resume-variants/{id} instead of /api/resume-variants/1)
        endpoint = request.url.path
        
        # Extremely basic regex masking for IDs locally (naive approach for MVP)
        import re
        endpoint_masked = re.sub(r'/[0-9]+', '/{id}', endpoint)

        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            http_requests_total.labels(method=method, endpoint=endpoint_masked, status_code=status_code).inc()
            http_request_duration_seconds.labels(method=method, endpoint=endpoint_masked).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # Trap explicitly 500
            http_requests_total.labels(method=method, endpoint=endpoint_masked, status_code=500).inc()
            logger.exception(f"Unhandled endpoint failure on {endpoint_masked}")
            raise e
