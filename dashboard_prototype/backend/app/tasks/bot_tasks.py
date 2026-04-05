"""
Celery tasks for bot execution.

These tasks are dispatched by the API and executed on worker VMs.
Each task manages the full bot lifecycle: START → RUNNING → SUCCESS/FAILED → RETRY.
"""

import time
from typing import Optional
from datetime import datetime, timezone

from celery import Task
from celery.utils.log import get_task_logger

from app.celery_app import celery_app

logger = get_task_logger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BotTask(Task):
    """Base task class with lifecycle callbacks."""

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(f"Task {task_id} retrying: {exc}")


@celery_app.task(
    base=BotTask,
    bind=True,
    name="app.tasks.bot_tasks.run_bot",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=3,
    acks_late=True,
)
def run_bot(self, bot_id: str, client_id: str, run_id: str, parameters: Optional[dict] = None):
    """
    Execute a bot on the worker VM.

    This is a SYNCHRONOUS Celery task (Celery workers are sync by default).
    It uses httpx to post status updates back to the control plane.

    Args:
        bot_id:     UUID of the bot to run
        client_id:  UUID of the owning client (for tenant scoping)
        run_id:     UUID of the bot_run record
        parameters: Optional runtime parameters
    """

    api_base = "http://localhost:8000"
    task_id = self.request.id

    logger.info(f"[{run_id}] Starting bot {bot_id} for client {client_id}")

    try:
        # ── Update status → RUNNING ─────────────────────────────
        _post_status(api_base, run_id, "running", client_id)

        # ── Simulate bot execution ──────────────────────────────
        # In production, this would import and run the actual bot script
        steps = [
            "Initializing browser session (Selenium WebDriver)",
            "Navigating to target application",
            "Performing login sequence",
            "Navigating to work queue",
            "Processing items in queue",
            "Validating results",
            "Capturing final screenshots",
            "Cleaning up browser session",
        ]

        for i, step in enumerate(steps):
            # Check if task was revoked
            if self.is_aborted():
                _post_status(api_base, run_id, "cancelled", client_id)
                _post_log(api_base, run_id, client_id, "info", "Task cancelled by user")
                return {"status": "cancelled", "run_id": run_id}

            _post_log(api_base, run_id, client_id, "info", f"Step {i+1}/{len(steps)}: {step}")

            # Simulate work
            time.sleep(2)

            # Simulate occasional warnings
            if i == 4:
                _post_log(
                    api_base, run_id, client_id, "warning",
                    "Slow page response detected (> 5s)"
                )

        # ── Success ──────────────────────────────────────────────
        _post_status(api_base, run_id, "success", client_id)
        _post_log(api_base, run_id, client_id, "info", "Bot execution completed successfully")

        return {
            "status": "success",
            "run_id": run_id,
            "items_processed": 47,
        }

    except Exception as exc:
        logger.error(f"[{run_id}] Bot failed: {exc}")
        _post_status(api_base, run_id, "failed", client_id, error=str(exc))
        _post_log(api_base, run_id, client_id, "error", f"Bot execution failed: {exc}")
        raise  # Let Celery handle retry


@celery_app.task(
    bind=True,
    name="app.tasks.bot_tasks.stop_bot",
)
def stop_bot(self, celery_task_id: str, run_id: str, client_id: str):
    """Revoke a running bot task."""
    logger.info(f"Revoking task {celery_task_id} for run {run_id}")
    celery_app.control.revoke(celery_task_id, terminate=True, signal="SIGTERM")
    _post_status("http://localhost:8000", run_id, "cancelled", client_id)
    return {"status": "cancelled", "run_id": run_id}


# ── Helper: Post status update to control plane ─────────────────
def _post_status(api_base: str, run_id: str, status: str, client_id: str, error: Optional[str] = None):
    """Post a status update to the API. Fire-and-forget."""
    try:
        import httpx
        httpx.put(
            f"{api_base}/api/internal/runs/{run_id}/status",
            json={"status": status, "error_message": error},
            headers={"X-API-Key": "internal-worker-key"},
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"Failed to post status update: {e}")


def _post_log(api_base: str, run_id: str, client_id: str, level: str, message: str):
    """Post a log entry to the API. Fire-and-forget."""
    try:
        import httpx
        httpx.post(
            f"{api_base}/api/internal/runs/{run_id}/logs",
            json={"level": level, "message": message, "client_id": client_id},
            headers={"X-API-Key": "internal-worker-key"},
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"Failed to post log: {e}")
