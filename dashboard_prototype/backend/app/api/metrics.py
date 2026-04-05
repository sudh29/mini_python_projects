"""
Metrics API route — Prometheus-compatible /metrics endpoint.
Also provides a JSON summary at /api/metrics for the dashboard.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, get_current_user
from app.database import get_db
from app.models import Bot, BotRun, RunStatus

router = APIRouter(tags=["metrics"])


@router.get("/api/metrics")
async def get_dashboard_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Returns aggregated metrics for the current tenant's dashboard.
    """
    client_id = user.client_id

    # Total bots
    bots_q = await db.execute(
        select(func.count(Bot.id)).where(Bot.client_id == client_id, Bot.is_active == True)
    )
    total_bots = bots_q.scalar() or 0

    # Run stats
    runs_q = await db.execute(
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

    # Average duration (for completed runs)
    dur_q = await db.execute(
        select(
            func.avg(
                func.julianday(BotRun.end_time) - func.julianday(BotRun.start_time)
            ).label("avg_days")  # SQLite returns days
        ).where(
            BotRun.client_id == client_id,
            BotRun.end_time != None,
            BotRun.start_time != None,
        )
    )
    avg_days = dur_q.scalar() or 0
    avg_duration_seconds = round(avg_days * 86400, 1)  # Convert days to seconds

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
