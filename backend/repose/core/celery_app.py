import os

from celery import Celery

from repose.core.config import settings

# Celery Configuration
# Use Redis as both broker and backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("repose", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover tasks in the workers module
celery_app.autodiscover_tasks(["repose.workers"])
