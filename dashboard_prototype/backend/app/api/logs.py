"""
Log API routes — fetch and stream logs for bot runs.
Also includes internal endpoints for workers to post logs.
"""

from datetime import datetime, timezone
from typing import Annotated, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, get_current_user
from app.database import get_db
from app.models import BotRun, Log, LogLevel
from app.schemas.log import LogOut, LogListOut

router = APIRouter(tags=["logs"])


# ── GET /api/logs/{run_id} ───────────────────────────────────────
@router.get("/api/logs/{run_id}", response_model=LogListOut)
async def get_run_logs(
    run_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
    level: Optional[str] = Query(None, description="Filter by log level"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get logs for a specific bot run (tenant-scoped)."""
    # Verify run belongs to client
    run_q = await db.execute(
        select(BotRun.id).where(
            BotRun.id == run_id,
            BotRun.client_id == user.client_id,
        )
    )
    if not run_q.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Run not found")

    # Build query
    query = select(Log).where(Log.run_id == run_id)
    count_query = select(func.count(Log.id)).where(Log.run_id == run_id)

    if level:
        try:
            log_level = LogLevel(level.lower())
            query = query.where(Log.level == log_level)
            count_query = count_query.where(Log.level == log_level)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid log level: {level}")

    total = (await db.execute(count_query)).scalar() or 0

    result = await db.execute(
        query.order_by(Log.timestamp.asc()).limit(limit).offset(offset)
    )
    logs = result.scalars().all()

    return LogListOut(
        logs=[LogOut.model_validate(log) for log in logs],
        total=total,
    )


# ── Internal: POST /api/internal/runs/{run_id}/logs ──────────────
@router.post("/api/internal/runs/{run_id}/logs", status_code=201)
async def post_run_log(
    run_id: str,
    body: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Internal endpoint for workers to post log entries.
    Bypasses normal auth — only accessible from workers.
    """
    log = Log(
        id=str(uuid.uuid4()),
        run_id=run_id,
        client_id=body.get("client_id", ""),
        level=LogLevel(body.get("level", "info")),
        message=body.get("message", ""),
        timestamp=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.flush()
    return {"id": log.id}


# ── Internal: PUT /api/internal/runs/{run_id}/status ─────────────
@router.put("/api/internal/runs/{run_id}/status")
async def update_run_status(
    run_id: str,
    body: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Internal endpoint for workers to update run status.
    """
    result = await db.execute(select(BotRun).where(BotRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    from app.models.bot_run import RunStatus as RS
    new_status = body.get("status")
    if new_status:
        run.status = RS(new_status)

    if new_status in ("success", "failed", "cancelled"):
        run.end_time = datetime.now(timezone.utc)
        from app.metrics_client import BOT_RUNS_ACTIVE, BOT_RUNS_COMPLETED
        BOT_RUNS_ACTIVE.labels(client_id=run.client_id, bot_id=run.bot_id).dec()
        BOT_RUNS_COMPLETED.labels(client_id=run.client_id, bot_id=run.bot_id, status=new_status).inc()

    if body.get("error_message"):
        run.error_message = body["error_message"]

    await db.flush()
    return {"status": run.status.value}
