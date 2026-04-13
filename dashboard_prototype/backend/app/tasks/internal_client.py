"""
Internal API Client for Workers.

Encapsulates all communication from the Celery workers back to the 
FastAPI control plane (status updates, logs, artifacts).
"""

import httpx
from typing import Optional
from app.config import settings

class InternalClient:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = (base_url or settings.INTERNAL_API_BASE).rstrip("/")
        self.api_key = api_key or settings.INTERNAL_API_KEY
        self.headers = {"X-API-Key": self.api_key}

    def post_status(self, run_id: str, status: str, error: Optional[str] = None):
        """Post a status update for a bot run."""
        url = f"{self.base_url}/api/internal/runs/{run_id}/status"
        payload = {"status": status}
        if error:
            payload["error_message"] = error
            
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.put(url, json=payload, headers=self.headers)
                res.raise_for_status()
                return res.json()
        except Exception as e:
            # We log but don't crash the worker if health reporting fails
            print(f"⚠️ Failed to post status update to {url}: {e}")
            return None

    def post_log(self, run_id: str, client_id: str, level: str, message: str):
        """Post a log entry for a bot run."""
        url = f"{self.base_url}/api/internal/runs/{run_id}/logs"
        payload = {
            "level": level,
            "message": message,
            "client_id": client_id
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload, headers=self.headers)
                res.raise_for_status()
                return res.json()
        except Exception as e:
            print(f"⚠️ Failed to post log to {url}: {e}")
            return None

# Singleton instance for easy import
internal_client = InternalClient()
