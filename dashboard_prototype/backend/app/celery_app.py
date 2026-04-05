"""
Celery application instance.

This module is imported by both the API (to dispatch tasks) and
the worker (to register and execute them).
"""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "rpa_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task behavior
    task_track_started=True,
    task_acks_late=True,  # Acknowledge after execution (crash safety)
    worker_prefetch_multiplier=1,  # One task at a time per worker

    # Result expiry
    result_expires=3600,  # 1 hour

    # Task routes
    task_routes={
        "app.tasks.bot_tasks.*": {"queue": "bots"},
    },

    # Retry defaults
    task_default_retry_delay=30,
    task_max_retries=3,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
