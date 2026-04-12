"""
Bot API routes — CRUD, run, stop, status.
All endpoints are tenant-scoped via the auth dependency.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, get_current_user, require_role
from app.database import get_db
from app.models import Bot, BotRun
from app.models.client import UserRole
from app.schemas.bot import BotOut, BotRunRequest, BotStopRequest, BotWithStatus
from app.schemas.bot_run import BotRunOut, BotRunListOut
from app.services.bot_service import BotService

router = APIRouter(prefix="/api/bots", tags=["bots"])


def get_bot_service(db: Annotated[AsyncSession, Depends(get_db)]) -> BotService:
    return BotService(db)


# ── GET /api/bots/status ─────────────────────────────────────────
@router.get("/status", response_model=list[BotWithStatus])
async def list_bots_with_status(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[BotService, Depends(get_bot_service)],
):
    """List all bots for the current client with their runtime status."""
    return await service.list_bots_with_status(user.client_id)


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

    from sqlalchemy import func
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
    user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[BotService, Depends(get_bot_service)],
):
    """Trigger a bot execution."""
    run = await service.trigger_bot_run(req.bot_id, user.client_id, req.parameters)
    return BotRunOut.model_validate(run)


# ── POST /api/bots/stop ──────────────────────────────────────────
@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_bot(
    req: BotStopRequest,
    user: Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[BotService, Depends(get_bot_service)],
):
    """Stop a running bot execution."""
    return await service.stop_bot_run(req.bot_id, user.client_id, req.run_id)
