"""
Bot API routes — CRUD, run, stop, status.
All endpoints are tenant-scoped via the auth dependency.
"""

from datetime import datetime, timezone
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, get_current_user, require_role
from app.database import get_db
from app.models import Bot, BotRun, RunStatus
from app.models.client import UserRole
from app.schemas.bot import BotOut, BotRunRequest, BotStopRequest, BotWithStatus
from app.schemas.bot_run import BotRunOut, BotRunListOut
from app.metrics_client import BOT_RUNS_TOTAL, BOT_RUNS_ACTIVE

router = APIRouter(prefix="/api/bots", tags=["bots"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── GET /api/bots/status ─────────────────────────────────────────
@router.get("/status", response_model=list[BotWithStatus])
async def list_bots_with_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List all bots for the current client with their runtime status."""
    # Get bots
    result = await db.execute(
        select(Bot).where(
            Bot.client_id == user.client_id,
            Bot.is_active == True,
        ).order_by(Bot.name)
    )
    bots = result.scalars().all()

    enriched = []
    for bot in bots:
        # Get run stats
        stats_q = await db.execute(
            select(
                func.count(BotRun.id).label("total"),
                func.sum(
                    case(
                        (BotRun.status == RunStatus.SUCCESS, 1),
                        else_=0,
                    )
                ).label("successes"),
            ).where(BotRun.bot_id == bot.id)
        )
        stats = stats_q.one()
        total = stats.total or 0
        successes = stats.successes or 0

        # Get latest run
        latest_q = await db.execute(
            select(BotRun)
            .where(BotRun.bot_id == bot.id)
            .order_by(BotRun.created_at.desc())
            .limit(1)
        )
        latest_run = latest_q.scalar_one_or_none()

        # Check for active run
        active_q = await db.execute(
            select(BotRun)
            .where(
                BotRun.bot_id == bot.id,
                BotRun.status.in_([RunStatus.RUNNING, RunStatus.PENDING]),
            )
            .limit(1)
        )
        active_run = active_q.scalar_one_or_none()

        # Determine current status
        if active_run:
            current_status = active_run.status.value
        elif latest_run:
            current_status = latest_run.status.value
        else:
            current_status = "idle"

        enriched.append(BotWithStatus(
            id=bot.id,
            client_id=bot.client_id,
            name=bot.name,
            process_name=bot.process_name,
            description=bot.description,
            script_path=bot.script_path,
            is_active=bot.is_active,
            created_at=bot.created_at,
            updated_at=bot.updated_at,
            current_status=current_status,
            last_run_at=latest_run.start_time if latest_run else None,
            total_runs=total,
            success_rate=round(successes / total * 100, 1) if total > 0 else 0.0,
            active_run_id=active_run.id if active_run else None,
        ))

    return enriched


# ── GET /api/bots/{bot_id} ───────────────────────────────────────
@router.get("/{bot_id}", response_model=BotOut)
async def get_bot(
    bot_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get a single bot by ID (tenant-scoped)."""
    result = await db.execute(
        select(Bot).where(Bot.id == bot_id, Bot.client_id == user.client_id)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot


# ── GET /api/bots/{bot_id}/runs ──────────────────────────────────
@router.get("/{bot_id}/runs", response_model=BotRunListOut)
async def get_bot_runs(
    bot_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get run history for a bot with pagination."""
    # Verify bot ownership
    bot_q = await db.execute(
        select(Bot.id).where(Bot.id == bot_id, Bot.client_id == user.client_id)
    )
    if not bot_q.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Bot not found")

    # Count total
    count_q = await db.execute(
        select(func.count(BotRun.id)).where(BotRun.bot_id == bot_id)
    )
    total = count_q.scalar() or 0

    # Fetch runs
    result = await db.execute(
        select(BotRun)
        .where(BotRun.bot_id == bot_id)
        .order_by(BotRun.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    runs = result.scalars().all()

    return BotRunListOut(runs=[BotRunOut.model_validate(r) for r in runs], total=total)


# ── POST /api/bots/run ───────────────────────────────────────────
@router.post("/run", response_model=BotRunOut, status_code=status.HTTP_202_ACCEPTED)
async def run_bot(
    req: BotRunRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
):
    """
    Trigger a bot execution.
    Creates a BotRun record and dispatches to Celery.
    """
    # Verify bot exists and belongs to client
    result = await db.execute(
        select(Bot).where(Bot.id == req.bot_id, Bot.client_id == user.client_id)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Check no active run
    active_q = await db.execute(
        select(BotRun.id).where(
            BotRun.bot_id == req.bot_id,
            BotRun.status.in_([RunStatus.RUNNING, RunStatus.PENDING]),
        )
    )
    if active_q.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Bot already has an active run",
        )

    # Create run record
    run = BotRun(
        id=str(uuid.uuid4()),
        bot_id=req.bot_id,
        client_id=user.client_id,
        status=RunStatus.PENDING,
        start_time=_utcnow(),
    )
    session = db
    session.add(run)
    await session.flush()

    # Dispatch to Celery
    try:
        from app.tasks.bot_tasks import run_bot as run_bot_task
        task = run_bot_task.apply_async(
            args=[bot.id, user.client_id, run.id],
            kwargs={"parameters": req.parameters},
            task_id=str(uuid.uuid4()),
        )
        run.celery_task_id = task.id
    except Exception:
        # If Celery is unavailable, still create the run but mark as pending
        run.celery_task_id = f"offline-{uuid.uuid4()}"

    await session.flush()
    
    BOT_RUNS_TOTAL.labels(client_id=user.client_id, bot_id=bot.id).inc()
    BOT_RUNS_ACTIVE.labels(client_id=user.client_id, bot_id=bot.id).inc()

    return BotRunOut.model_validate(run)


# ── POST /api/bots/stop ──────────────────────────────────────────
@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_bot(
    req: BotStopRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
):
    """Stop a running bot execution."""
    # Find active run
    query = select(BotRun).where(
        BotRun.bot_id == req.bot_id,
        BotRun.client_id == user.client_id,
    )
    if req.run_id:
        query = query.where(BotRun.id == req.run_id)
    else:
        query = query.where(BotRun.status.in_([RunStatus.RUNNING, RunStatus.PENDING]))

    result = await db.execute(query)
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="No active run found")

    # Revoke Celery task
    if run.celery_task_id:
        try:
            from app.tasks.bot_tasks import stop_bot as stop_bot_task
            stop_bot_task.delay(run.celery_task_id, run.id, user.client_id)
        except Exception:
            pass  # Best effort

    # Update DB
    run.status = RunStatus.CANCELLED
    run.end_time = _utcnow()
    await db.flush()
    
    BOT_RUNS_ACTIVE.labels(client_id=user.client_id, bot_id=req.bot_id).dec()
    from app.metrics_client import BOT_RUNS_COMPLETED
    BOT_RUNS_COMPLETED.labels(client_id=user.client_id, bot_id=req.bot_id, status="cancelled").inc()

    return {"status": "cancelled", "run_id": run.id}
