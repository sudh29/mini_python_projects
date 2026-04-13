import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import Bot, BotRun, RunStatus
from app.models.client import User
from app.schemas.bot import BotWithStatus, BotRunRequest
from app.prometheus_metrics import RPA_BOT_RUNS_TOTAL, RPA_ACTIVE_RUNS
from app.services.base import BaseService

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class BotService(BaseService):
    async def list_bots_with_status(self, client_id: str) -> List[BotWithStatus]:
        """List all bots for a client with their current runtime status."""
        
        # 1. Total stats for each bot (Subquery)
        stats_sub = (
            select(
                BotRun.bot_id,
                func.count(BotRun.id).label("total_runs"),
                func.sum(case((BotRun.status == RunStatus.SUCCESS, 1), else_=0)).label("success_count"),
            )
            .where(BotRun.client_id == client_id)
            .group_by(BotRun.bot_id)
            .subquery()
        )

        # 2. Latest run for each bot
        latest_sub = (
            select(
                BotRun.bot_id,
                BotRun.status.label("latest_status"),
                BotRun.start_time.label("last_run_at"),
                func.row_number().over(
                    partition_by=BotRun.bot_id,
                    order_by=BotRun.created_at.desc()
                ).label("rn")
            )
            .where(BotRun.client_id == client_id)
            .subquery()
        )

        # 3. Currently active run
        active_sub = (
            select(
                BotRun.bot_id,
                BotRun.id.label("active_run_id"),
                BotRun.status.label("active_status"),
                func.row_number().over(
                    partition_by=BotRun.bot_id,
                    order_by=BotRun.created_at.desc()
                ).label("rn")
            )
            .where(
                BotRun.client_id == client_id,
                BotRun.status.in_([RunStatus.RUNNING, RunStatus.PENDING])
            )
            .subquery()
        )

        # 4. Final join query
        stmt = (
            select(
                Bot,
                stats_sub.c.total_runs,
                stats_sub.c.success_count,
                latest_sub.c.latest_status,
                latest_sub.c.last_run_at,
                active_sub.c.active_run_id,
                active_sub.c.active_status,
            )
            .outerjoin(stats_sub, Bot.id == stats_sub.c.bot_id)
            .outerjoin(latest_sub, (Bot.id == latest_sub.c.bot_id) & (latest_sub.c.rn == 1))
            .outerjoin(active_sub, (Bot.id == active_sub.c.bot_id) & (active_sub.c.rn == 1))
            .where(
                Bot.client_id == client_id,
                Bot.is_active == True,
            )
            .order_by(Bot.name)
        )

        result = await self.db.execute(stmt)
        
        enriched = []
        for row in result.mappings():
            bot = row["Bot"]
            total = row["total_runs"] or 0
            successes = row["success_count"] or 0
            
            if row["active_run_id"]:
                current_status = row["active_status"].value
            elif row["latest_status"]:
                current_status = row["latest_status"].value
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
                last_run_at=row["last_run_at"],
                total_runs=total,
                success_rate=round(successes / total * 100, 1) if total > 0 else 0.0,
                active_run_id=row["active_run_id"],
            ))

        return enriched

    async def trigger_bot_run(self, bot_id: str, client_id: str, parameters: Optional[dict] = None) -> BotRun:
        """Trigger a bot execution via Celery."""
        # Verify bot exists
        result = await self.db.execute(
            select(Bot).where(Bot.id == bot_id, Bot.client_id == client_id)
        )
        bot = result.scalar_one_or_none()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        # Check no active run
        active_q = await self.db.execute(
            select(BotRun.id).where(
                BotRun.bot_id == bot_id,
                BotRun.status.in_([RunStatus.RUNNING, RunStatus.PENDING]),
            )
        )
        if active_q.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Bot already has an active run")

        # Create run record
        run = BotRun(
            id=str(uuid.uuid4()),
            bot_id=bot_id,
            client_id=client_id,
            status=RunStatus.PENDING,
            start_time=_utcnow(),
        )
        self.db.add(run)
        await self.db.flush()

        # Dispatch to Celery
        try:
            from app.tasks.bot_tasks import run_bot as run_bot_task
            task = run_bot_task.apply_async(
                args=[bot.id, client_id, run.id],
                kwargs={"parameters": parameters or {}},
                task_id=str(uuid.uuid4()),
            )
            run.celery_task_id = task.id
        except Exception:
            run.celery_task_id = f"offline-{uuid.uuid4()}"

        await self.db.flush()
        
        # Metrics
        RPA_BOT_RUNS_TOTAL.labels(client_id=client_id, bot_id=bot.id, bot_name=bot.name, status="pending").inc()
        RPA_ACTIVE_RUNS.labels(client_id=client_id, bot_id=bot.id, bot_name=bot.name).inc()

        return run

    async def stop_bot_run(self, bot_id: str, client_id: str, run_id: Optional[str] = None):
        """Stop a running bot execution."""
        query = select(BotRun).where(
            BotRun.bot_id == bot_id,
            BotRun.client_id == client_id,
        )
        if run_id:
            query = query.where(BotRun.id == run_id)
        else:
            query = query.where(BotRun.status.in_([RunStatus.RUNNING, RunStatus.PENDING]))

        result = await self.db.execute(query)
        run = result.scalar_one_or_none()

        if not run:
            raise HTTPException(status_code=404, detail="No active run found")

        # Revoke Celery task
        if run.celery_task_id:
            try:
                from app.tasks.bot_tasks import stop_bot as stop_bot_task
                stop_bot_task.delay(run.celery_task_id, run.id, client_id)
            except Exception:
                pass 

        # Update DB
        run.status = RunStatus.CANCELLED
        run.end_time = _utcnow()
        await self.db.flush()
        
        # Metrics
        RPA_ACTIVE_RUNS.labels(client_id=client_id, bot_id=run.bot_id, bot_name=run.bot.name).dec()
        RPA_BOT_RUNS_TOTAL.labels(client_id=client_id, bot_id=run.bot_id, bot_name=run.bot.name, status="cancelled").inc()

        return {"status": "cancelled", "run_id": run.id}
