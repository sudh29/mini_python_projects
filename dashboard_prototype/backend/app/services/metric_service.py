from typing import Dict, Any
from sqlalchemy import func, select, case
from app.models import Bot, BotRun, RunStatus
from app.services.base import BaseService

class MetricService(BaseService):
    async def get_dashboard_metrics(self, client_id: str) -> Dict[str, Any]:
        """Aggregate metrics for the client dashboard."""
        
        # Total active bots
        bots_q = await self.db.execute(
            select(func.count(Bot.id)).where(Bot.client_id == client_id, Bot.is_active == True)
        )
        total_bots = bots_q.scalar() or 0

        # Run history and current state
        runs_q = await self.db.execute(
            select(
                func.count(BotRun.id).label("total_runs"),
                func.sum(case((BotRun.status == RunStatus.SUCCESS, 1), else_=0)).label("successful"),
                func.sum(case((BotRun.status == RunStatus.FAILED, 1), else_=0)).label("failed"),
                func.sum(case((BotRun.status == RunStatus.RUNNING, 1), else_=0)).label("active"),
                func.sum(case((BotRun.status == RunStatus.PENDING, 1), else_=0)).label("pending"),
            ).where(BotRun.client_id == client_id)
        )
        stats = runs_q.one()

        total_runs = stats.total_runs or 0
        successful = stats.successful or 0
        failed = stats.failed or 0
        active = stats.active or 0
        pending = stats.pending or 0

        # Average duration (converted from SQLite days to seconds)
        dur_q = await self.db.execute(
            select(
                func.avg(
                    func.julianday(BotRun.end_time) - func.julianday(BotRun.start_time)
                ).label("avg_days")
            ).where(
                BotRun.client_id == client_id,
                BotRun.end_time != None,
                BotRun.start_time != None,
            )
        )
        avg_days = dur_q.scalar() or 0
        avg_duration_seconds = round(avg_days * 86400, 1)

        return {
            "total_bots": total_bots,
            "total_runs": total_runs,
            "successful_runs": successful,
            "failed_runs": failed,
            "active_runs": active,
            "pending_runs": pending,
            "success_rate": round(successful / total_runs * 100, 1) if total_runs > 0 else 0,
            "avg_duration_seconds": avg_duration_seconds,
        }
