import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy import select
from fastapi import HTTPException

from app.models import BotRun, Log, LogLevel, Bot
from app.models.bot_run import RunStatus
from app.prometheus_metrics import RPA_ACTIVE_RUNS, RPA_BOT_RUNS_TOTAL, RPA_BOT_FAILURES_TOTAL
from app.services.base import BaseService

class RunService(BaseService):
    async def update_run_status(self, run_id: str, data: Dict[str, Any]) -> str:
        """Update run status and metrics (internal worker endpoint logic)."""
        result = await self.db.execute(
            select(BotRun).join(Bot).where(BotRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        new_status_str = data.get("status")
        if new_status_str:
            run.status = RunStatus(new_status_str)

        if new_status_str in ("success", "failed", "cancelled"):
            run.end_time = datetime.now(timezone.utc)
            
            # Update Metrics
            labels = {"client_id": run.client_id, "bot_id": run.bot_id, "bot_name": run.bot.name}
            RPA_ACTIVE_RUNS.labels(**labels).dec()
            RPA_BOT_RUNS_TOTAL.labels(**labels, status=new_status_str).inc()
            
            if new_status_str == "failed":
                error_type = data.get("error") or "Unknown"
                RPA_BOT_FAILURES_TOTAL.labels(**labels, error_type=error_type).inc()

        if data.get("error_message"):
            run.error_message = data["error_message"]

        await self.db.flush()
        return run.status.value

    async def post_log(self, run_id: str, data: Dict[str, Any]) -> str:
        """Create a new log entry (internal worker endpoint logic)."""
        log = Log(
            id=str(uuid.uuid4()),
            run_id=run_id,
            client_id=data.get("client_id", ""),
            level=LogLevel(data.get("level", "info")),
            message=data.get("message", ""),
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(log)
        await self.db.flush()
        return log.id

    async def verify_run_ownership(self, run_id: str, client_id: str) -> bool:
        """Verify that a run belongs to a specific client."""
        run_q = await self.db.execute(
            select(BotRun.id).where(
                BotRun.id == run_id,
                BotRun.client_id == client_id,
            )
        )
        return run_q.scalar_one_or_none() is not None
