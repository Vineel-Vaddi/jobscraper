from celery import Celery
from src.config import settings

celery_app = Celery("jobtailor_worker")

celery_app.conf.update(
    broker_url=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 minutes max
)

# Autodiscover tasks in the worker package
celery_app.autodiscover_tasks(['src.worker'])
