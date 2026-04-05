"""
Seed script — populates the database with demo data for development.
Run: python -m app.seed
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext

from app.database import async_session, init_db
from app.models import Bot, BotRun, Client, Log, LogLevel, RunStatus, User
from app.models.client import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Demo Client IDs (stable for dev) ────────────────────────────
CLIENT_A_ID = "c1000000-0000-0000-0000-000000000001"
CLIENT_B_ID = "c2000000-0000-0000-0000-000000000002"


async def seed() -> None:
    await init_db()

    async with async_session() as session:
        # ── Clients ──────────────────────────────────────────────
        client_a = Client(
            id=CLIENT_A_ID,
            name="Acme Healthcare",
            api_key="acme-api-key-dev-001",
        )
        client_b = Client(
            id=CLIENT_B_ID,
            name="Pinnacle Insurance",
            api_key="pinnacle-api-key-dev-002",
        )
        session.add_all([client_a, client_b])

        # ── Users ────────────────────────────────────────────────
        users = [
            User(
                id=str(uuid.uuid4()),
                client_id=CLIENT_A_ID,
                username="admin@acme",
                password_hash=pwd_context.hash("admin123"),
                role=UserRole.ADMIN,
            ),
            User(
                id=str(uuid.uuid4()),
                client_id=CLIENT_A_ID,
                username="viewer@acme",
                password_hash=pwd_context.hash("viewer123"),
                role=UserRole.VIEWER,
            ),
            User(
                id=str(uuid.uuid4()),
                client_id=CLIENT_B_ID,
                username="admin@pinnacle",
                password_hash=pwd_context.hash("admin123"),
                role=UserRole.ADMIN,
            ),
        ]
        session.add_all(users)

        # ── Bots (Acme Healthcare) ──────────────────────────────
        bot_ids_a = [str(uuid.uuid4()) for _ in range(4)]
        bots_a = [
            Bot(
                id=bot_ids_a[0],
                client_id=CLIENT_A_ID,
                name="Claims Processor",
                process_name="claims_processing",
                description="Processes incoming insurance claims via the portal, validates data, and submits to adjudication queue.",
                script_path="bots/acme/claims_processor.py",
            ),
            Bot(
                id=bot_ids_a[1],
                client_id=CLIENT_A_ID,
                name="Eligibility Checker",
                process_name="eligibility_verification",
                description="Verifies patient eligibility against payer databases using the clearinghouse portal.",
                script_path="bots/acme/eligibility_checker.py",
            ),
            Bot(
                id=bot_ids_a[2],
                client_id=CLIENT_A_ID,
                name="Denial Manager",
                process_name="denial_management",
                description="Monitors denied claims, categorizes denial reasons, and initiates appeal workflows.",
                script_path="bots/acme/denial_manager.py",
            ),
            Bot(
                id=bot_ids_a[3],
                client_id=CLIENT_A_ID,
                name="Payment Poster",
                process_name="payment_posting",
                description="Posts ERA/EOB payments to patient accounts in the billing system.",
                script_path="bots/acme/payment_poster.py",
            ),
        ]
        session.add_all(bots_a)

        # ── Bots (Pinnacle Insurance) ────────────────────────────
        bot_ids_b = [str(uuid.uuid4()) for _ in range(3)]
        bots_b = [
            Bot(
                id=bot_ids_b[0],
                client_id=CLIENT_B_ID,
                name="Policy Renewal Bot",
                process_name="policy_renewal",
                description="Automates policy renewal notices and updates in the underwriting system.",
                script_path="bots/pinnacle/policy_renewal.py",
            ),
            Bot(
                id=bot_ids_b[1],
                client_id=CLIENT_B_ID,
                name="Quote Generator",
                process_name="quote_generation",
                description="Generates insurance quotes by pulling data from multiple rating engines.",
                script_path="bots/pinnacle/quote_generator.py",
            ),
            Bot(
                id=bot_ids_b[2],
                client_id=CLIENT_B_ID,
                name="Collections Agent",
                process_name="collections_processing",
                description="Manages overdue premium collections with automated follow-up sequences.",
                script_path="bots/pinnacle/collections_agent.py",
            ),
        ]
        session.add_all(bots_b)

        # ── Bot Runs (historical data) ──────────────────────────
        now = _utcnow()
        all_runs = []

        # Helper to create realistic run history
        def _make_runs(bot_id: str, client_id: str, count: int) -> list[BotRun]:
            runs = []
            for i in range(count):
                offset = timedelta(hours=i * 4, minutes=i * 7)
                start = now - timedelta(days=3) + offset
                duration = timedelta(minutes=2 + (i % 5) * 3, seconds=i * 11 % 60)
                # Mix of statuses
                if i % 7 == 0:
                    status = RunStatus.FAILED
                    error = "TimeoutError: Element not found after 30s wait"
                elif i % 11 == 0:
                    status = RunStatus.CANCELLED
                    error = None
                else:
                    status = RunStatus.SUCCESS
                    error = None

                run = BotRun(
                    id=str(uuid.uuid4()),
                    bot_id=bot_id,
                    client_id=client_id,
                    celery_task_id=str(uuid.uuid4()),
                    status=status,
                    start_time=start,
                    end_time=start + duration if status != RunStatus.CANCELLED else start + timedelta(seconds=15),
                    error_message=error,
                    retry_count=1 if status == RunStatus.FAILED else 0,
                    artifacts_path=f"artifacts/{client_id}/{bot_id}/{start.strftime('%Y%m%d_%H%M%S')}",
                )
                runs.append(run)
            return runs

        # Create runs for all bots
        for bid in bot_ids_a:
            all_runs.extend(_make_runs(bid, CLIENT_A_ID, 8))
        for bid in bot_ids_b:
            all_runs.extend(_make_runs(bid, CLIENT_B_ID, 6))

        # Mark one bot as currently running
        running_run = BotRun(
            id=str(uuid.uuid4()),
            bot_id=bot_ids_a[0],
            client_id=CLIENT_A_ID,
            celery_task_id=str(uuid.uuid4()),
            status=RunStatus.RUNNING,
            start_time=now - timedelta(minutes=3),
            retry_count=0,
            artifacts_path=f"artifacts/{CLIENT_A_ID}/{bot_ids_a[0]}/{now.strftime('%Y%m%d_%H%M%S')}",
        )
        all_runs.append(running_run)

        session.add_all(all_runs)

        # ── Logs (for the running run + some history) ────────────
        log_messages = [
            (LogLevel.INFO, "Bot started — initializing browser session"),
            (LogLevel.INFO, "Navigating to claims portal: https://portal.acme-health.example.com"),
            (LogLevel.INFO, "Login successful — session established"),
            (LogLevel.INFO, "Navigating to claims queue — 47 pending claims found"),
            (LogLevel.INFO, "Processing claim #CLM-2024-00893 — patient: John D."),
            (LogLevel.DEBUG, "Filling form field: diagnosis_code = E11.65"),
            (LogLevel.INFO, "Claim #CLM-2024-00893 submitted successfully"),
            (LogLevel.WARNING, "Slow page load detected — portal response > 5s"),
            (LogLevel.INFO, "Processing claim #CLM-2024-00894 — patient: Sarah M."),
            (LogLevel.INFO, "Screenshot captured: claim_894_submission.png"),
        ]
        logs = []
        for i, (level, msg) in enumerate(log_messages):
            logs.append(Log(
                id=str(uuid.uuid4()),
                run_id=running_run.id,
                client_id=CLIENT_A_ID,
                level=level,
                message=msg,
                timestamp=running_run.start_time + timedelta(seconds=i * 18),  # type: ignore[operator]
            ))
        session.add_all(logs)

        await session.commit()
        print("✅ Database seeded successfully!")
        print("   Clients:  2  (Acme Healthcare, Pinnacle Insurance)")
        print("   Users:    3  (admin@acme, viewer@acme, admin@pinnacle)")
        print("   Bots:     7  (4 Acme + 3 Pinnacle)")
        print(f"   Runs:     {len(all_runs)}  (mixed statuses, 1 currently running)")
        print(f"   Logs:     {len(logs)}")


if __name__ == "__main__":
    asyncio.run(seed())
