"""
Status reporter for bot workers.
Reports bot execution status back to the control plane.
"""

from datetime import datetime, timezone


class StatusReporter:
    """
    Reports bot run status changes back to the control plane API.
    All calls are best-effort (fire-and-forget).
    """

    def __init__(self, api_base: str = "http://localhost:8000", api_key: str = "internal-worker-key"):
        self.api_base = api_base
        self.api_key = api_key

    def report(self, run_id: str, status: str, error_message: str | None = None):
        """Report a status change for a bot run."""
        try:
            import httpx
            httpx.put(
                f"{self.api_base}/api/internal/runs/{run_id}/status",
                json={
                    "status": status,
                    "error_message": error_message,
                },
                headers={"X-API-Key": self.api_key},
                timeout=5,
            )
        except Exception as e:
            print(f"[WARNING] Failed to report status: {e}")

    def running(self, run_id: str):
        self.report(run_id, "running")

    def success(self, run_id: str):
        self.report(run_id, "success")

    def failed(self, run_id: str, error: str):
        self.report(run_id, "failed", error_message=error)

    def cancelled(self, run_id: str):
        self.report(run_id, "cancelled")

    def retrying(self, run_id: str, error: str):
        self.report(run_id, "retrying", error_message=error)
