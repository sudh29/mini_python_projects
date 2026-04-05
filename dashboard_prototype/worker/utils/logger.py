"""
Structured logger for bot workers.
Emits structured JSON logs both locally and to the control plane API.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


class BotLogger:
    """
    Structured logger for bot execution.

    Outputs to:
      1. Local log file (per run)
      2. stdout (structured JSON)
      3. Control plane API (async, best-effort)
    """

    def __init__(
        self,
        run_id: str,
        client_id: str,
        bot_name: str,
        log_dir: Path | None = None,
    ):
        self.run_id = run_id
        self.client_id = client_id
        self.bot_name = bot_name
        self._entries: list[dict] = []

        # Set up file logging
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            self._log_file = log_dir / f"{run_id}.jsonl"
        else:
            self._log_file = None

        # Python logger
        self._logger = logging.getLogger(f"bot.{bot_name}.{run_id[:8]}")
        self._logger.setLevel(logging.DEBUG)

        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            ))
            self._logger.addHandler(handler)

    def _emit(self, level: str, message: str, extra: dict | None = None):
        entry = {
            "run_id": self.run_id,
            "client_id": self.client_id,
            "bot_name": self.bot_name,
            "level": level,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(extra or {}),
        }
        self._entries.append(entry)

        # Write to file
        if self._log_file:
            with open(self._log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")

        # Write to Python logger
        log_method = getattr(self._logger, level, self._logger.info)
        log_method(message)

    def debug(self, message: str, **extra):
        self._emit("debug", message, extra)

    def info(self, message: str, **extra):
        self._emit("info", message, extra)

    def warning(self, message: str, **extra):
        self._emit("warning", message, extra)

    def error(self, message: str, **extra):
        self._emit("error", message, extra)

    def critical(self, message: str, **extra):
        self._emit("critical", message, extra)

    @property
    def entries(self) -> list[dict]:
        return self._entries.copy()

    def flush_to_api(self, api_base: str = "http://localhost:8000"):
        """
        Bulk-post accumulated logs to the control plane.
        Best-effort — failures don't crash the bot.
        """
        if not self._entries:
            return

        try:
            import httpx
            for entry in self._entries:
                httpx.post(
                    f"{api_base}/api/internal/runs/{self.run_id}/logs",
                    json={
                        "level": entry["level"],
                        "message": entry["message"],
                        "client_id": self.client_id,
                    },
                    headers={"X-API-Key": "internal-worker-key"},
                    timeout=5,
                )
        except Exception as e:
            self._logger.warning(f"Failed to flush logs to API: {e}")
