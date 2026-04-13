"""
Log API routes — fetch and stream logs for bot runs.
Also includes internal endpoints for workers to post logs.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BotRun, Log, LogLevel
from app.schemas.log import LogOut, LogListOut
from app.auth.dependencies import verify_worker_key, get_db, CurrentUser, get_current_user
from app.services.run_service import RunService

router = APIRouter(tags=["logs"])


def get_run_service(db: Annotated[AsyncSession, Depends(get_db)]) -> RunService:
    return RunService(db)


# ── GET /api/logs/{run_id} ───────────────────────────────────────
@router.get("/api/logs/{run_id}", response_model=LogListOut)
async def get_run_logs(
    run_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[RunService, Depends(get_run_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    level: Optional[str] = Query(None, description="Filter by log level"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get logs for a specific bot run (tenant-scoped)."""
    if not await service.verify_run_ownership(run_id, user.client_id):
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
@router.post("/api/internal/runs/{run_id}/logs", status_code=201, dependencies=[Depends(verify_worker_key)])
async def post_run_log(
    run_id: str,
    body: dict,
    service: Annotated[RunService, Depends(get_run_service)],
):
    """Internal endpoint for workers to post log entries."""
    log_id = await service.post_log(run_id, body)
    return {"id": log_id}


# ── Internal: PUT /api/internal/runs/{run_id}/status ─────────────
@router.put("/api/internal/runs/{run_id}/status", dependencies=[Depends(verify_worker_key)])
async def update_run_status(
    run_id: str,
    body: dict,
    service: Annotated[RunService, Depends(get_run_service)],
):
    """Internal endpoint for workers to update run status."""
    status_val = await service.update_run_status(run_id, body)
    return {"status": status_val}
