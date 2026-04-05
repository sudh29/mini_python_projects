"""
Celery Worker entry point.

Run with:
    celery -A celery_worker.celery_app worker --loglevel=info --queues=bots
"""

import sys
import os

# Add backend to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.celery_app import celery_app  # noqa: E402, F401
from app.tasks import bot_tasks  # noqa: E402, F401

if __name__ == "__main__":
    celery_app.worker_main(
        argv=[
            "worker",
            "--loglevel=info",
            "--queues=bots",
            "--concurrency=2",
            "--hostname=worker@%h",
        ]
    )
