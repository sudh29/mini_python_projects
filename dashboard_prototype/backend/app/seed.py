"""
Seed script — populates the database with rich demo data for development.

Creates:
  - 2 clients (Acme Healthcare, Pinnacle Insurance)
  - 3 users (admin@acme, viewer@acme, admin@pinnacle)
  - 7 bots (4 Acme + 3 Pinnacle)
  - ~200 historical bot runs over the past 30 days
  - Detailed logs for recent runs + the currently-running bot
  - Realistic error scenarios and varying durations

Run:  python -m app.seed
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext

from app.database import Base, async_session, engine, init_db
from app.models import Bot, BotRun, Client, Log, LogLevel, RunStatus, User
from app.models.client import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

random.seed(42)  # Deterministic so repeated runs give identical data


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Demo Client IDs (stable for dev) ────────────────────────────
CLIENT_A_ID = "c1000000-0000-0000-0000-000000000001"
CLIENT_B_ID = "c2000000-0000-0000-0000-000000000002"


# ── Run History Generator ────────────────────────────────────────
ERROR_MESSAGES = [
    "TimeoutError: Element not found after 30s wait",
    "ConnectionError: Portal returned 503 Service Unavailable",
    "ValidationError: Missing required field — diagnosis_code",
    "SessionExpired: Login session timed out after 15 min inactivity",
    "ElementInteractionError: Button disabled — form validation failed",
    "NetworkError: DNS resolution failed for payer-portal.example.com",
    "CaptchaError: CAPTCHA detected, manual intervention required",
    "DataMismatchError: Patient DOB does not match payer records",
]


def _make_runs(
    bot_id: str,
    client_id: str,
    count: int,
    days_back: int = 30,
    success_pct: float = 0.88,
) -> list[BotRun]:
    """Generate realistic historical runs spread over `days_back` days."""
    now = _utcnow()
    runs: list[BotRun] = []

    for i in range(count):
        # Spread runs across the date range with some clustering
        day_offset = random.uniform(0, days_back)
        hour_offset = random.uniform(6, 22)  # Mostly during business hours
        start = now - timedelta(days=day_offset, hours=hour_offset)

        # Duration: 45s – 20 min, weighted toward 2–5 min
        base_duration = random.gauss(240, 120)
        duration = max(45, min(1200, base_duration))

        # Status distribution
        roll = random.random()
        if roll < success_pct:
            status = RunStatus.SUCCESS
            error = None
        elif roll < success_pct + 0.07:
            status = RunStatus.FAILED
            error = random.choice(ERROR_MESSAGES)
        elif roll < success_pct + 0.10:
            status = RunStatus.CANCELLED
            error = None
        else:
            status = RunStatus.RETRYING
            error = random.choice(ERROR_MESSAGES[:3])

        end_time = start + timedelta(seconds=duration)
        if status == RunStatus.CANCELLED:
            end_time = start + timedelta(seconds=random.uniform(5, 30))

        run = BotRun(
            id=str(uuid.uuid4()),
            bot_id=bot_id,
            client_id=client_id,
            celery_task_id=str(uuid.uuid4()),
            status=status,
            start_time=start,
            end_time=end_time,
            error_message=error,
            retry_count=random.choice([1, 2]) if status == RunStatus.FAILED else 0,
            artifacts_path=f"artifacts/{client_id}/{bot_id}/{start.strftime('%Y%m%d_%H%M%S')}",
        )
        runs.append(run)

    # Sort newest first
    runs.sort(key=lambda r: r.start_time, reverse=True)
    return runs


# ── Log Generator ────────────────────────────────────────────────
LOG_SCENARIOS: dict[str, list[tuple[LogLevel, str]]] = {
    "claims_processing": [
        (LogLevel.INFO, "Bot started — initializing browser session"),
        (LogLevel.INFO, "Navigating to claims portal: https://portal.acme-health.example.com"),
        (LogLevel.INFO, "Login successful — session established"),
        (LogLevel.INFO, "Navigating to claims queue — {n} pending claims found"),
        (LogLevel.INFO, "Processing claim #CLM-2024-{seq:05d} — patient: {patient}"),
        (LogLevel.DEBUG, "Filling form field: diagnosis_code = {code}"),
        (LogLevel.INFO, "Claim #CLM-2024-{seq:05d} submitted successfully"),
        (LogLevel.WARNING, "Slow page load detected — portal response > {delay}s"),
        (LogLevel.INFO, "Processing claim #CLM-2024-{seq2:05d} — patient: {patient2}"),
        (LogLevel.INFO, "Screenshot captured: claim_{seq2}_submission.png"),
        (LogLevel.INFO, "Claim #CLM-2024-{seq2:05d} submitted successfully"),
        (LogLevel.DEBUG, "Performing OCR on scanned document: denial_letter.pdf"),
        (LogLevel.INFO, "Processing claim #CLM-2024-{seq3:05d} — patient: {patient3}"),
        (LogLevel.INFO, "Claim #CLM-2024-{seq3:05d} submitted successfully"),
        (LogLevel.WARNING, "Duplicate claim detected — skipping CLM-2024-{dup:05d}"),
        (LogLevel.INFO, "Batch complete — {processed} claims processed, {skipped} skipped"),
    ],
    "eligibility_verification": [
        (LogLevel.INFO, "Bot started — initializing headless browser"),
        (LogLevel.INFO, "Loading clearinghouse portal: https://ch.acme-health.example.com"),
        (LogLevel.INFO, "Login successful — 2FA verification bypassed (saved session)"),
        (LogLevel.INFO, "Fetching patient roster — {n} pending verifications"),
        (LogLevel.INFO, "Verifying eligibility: Patient #PT-{id1} — {payer1}"),
        (LogLevel.INFO, "Eligibility confirmed — coverage active through 2026-12-31"),
        (LogLevel.INFO, "Verifying eligibility: Patient #PT-{id2} — {payer2}"),
        (LogLevel.WARNING, "Eligibility expired — coverage ended 2026-03-15"),
        (LogLevel.INFO, "Verifying eligibility: Patient #PT-{id3} — BCBS PPO"),
        (LogLevel.INFO, "Eligibility confirmed — coverage active, copay $25"),
        (LogLevel.DEBUG, "Cache hit: payer config loaded from local store"),
        (LogLevel.INFO, "Batch complete — {verified} verified, {flagged} flagged"),
    ],
    "denial_management": [
        (LogLevel.INFO, "Bot started — connecting to denial management queue"),
        (LogLevel.INFO, "Loaded {n} new denials since last run"),
        (LogLevel.INFO, "Categorizing denial #DEN-{seq1} — reason: Missing prior auth"),
        (LogLevel.INFO, "Auto-generating appeal letter for DEN-{seq1}"),
        (LogLevel.WARNING, "Denial #DEN-{seq2} — unrecognized denial code: XR99"),
        (LogLevel.ERROR, "Failed to process DEN-{seq3} — payer portal returned 500"),
        (LogLevel.INFO, "Retrying DEN-{seq3} in 30 seconds..."),
        (LogLevel.INFO, "DEN-{seq3} retry successful — categorized as: Timely filing"),
        (LogLevel.INFO, "Categorizing denial #DEN-{seq4} — reason: Non-covered service"),
        (LogLevel.INFO, "Batch complete — {processed} denials processed"),
    ],
    "payment_posting": [
        (LogLevel.INFO, "Bot started — checking for new ERA files"),
        (LogLevel.INFO, "Found {n} new ERA files from Aetna, BCBS, UHC"),
        (LogLevel.INFO, "Parsing ERA file: AETNA_ERA_{date}.835"),
        (LogLevel.INFO, "Matched {matched} payments to patient accounts"),
        (LogLevel.INFO, "Posting payment ${amt1} to account #AC-2024-{acct1}"),
        (LogLevel.INFO, "Posting payment ${amt2} to account #AC-2024-{acct2}"),
        (LogLevel.DEBUG, "Reconciliation check: batch total = ${total}, posted = ${total} ✓"),
        (LogLevel.INFO, "All ERA payments posted successfully"),
    ],
    "policy_renewal": [
        (LogLevel.INFO, "Bot started — opening underwriting system"),
        (LogLevel.INFO, "Login successful — authorized for policy management"),
        (LogLevel.INFO, "Scanning for policies expiring within 30 days — {n} found"),
        (LogLevel.INFO, "Generating renewal notice for Policy #POL-{pol1}"),
        (LogLevel.INFO, "Renewal notice sent to: {email1}"),
        (LogLevel.INFO, "Generating renewal notice for Policy #POL-{pol2}"),
        (LogLevel.WARNING, "Policy #POL-{pol3} — premium increase > 15%, flagging for review"),
        (LogLevel.INFO, "Batch complete — {processed} notices sent, {flagged} flagged"),
    ],
    "quote_generation": [
        (LogLevel.INFO, "Bot started — connecting to rating engines"),
        (LogLevel.INFO, "Loading quote request queue — {n} pending quotes"),
        (LogLevel.INFO, "Generating quote for: {applicant1} — Auto + Home bundle"),
        (LogLevel.DEBUG, "Querying rating engine: Progressive, Travelers, Hartford"),
        (LogLevel.INFO, "Best rate found: ${rate1}/mo from Travelers"),
        (LogLevel.INFO, "Generating quote for: {applicant2} — Commercial liability"),
        (LogLevel.INFO, "Best rate found: ${rate2}/mo from Hartford"),
        (LogLevel.INFO, "Batch complete — {generated} quotes generated"),
    ],
    "collections_processing": [
        (LogLevel.INFO, "Bot started — loading overdue accounts"),
        (LogLevel.INFO, "Found {n} accounts with overdue premiums"),
        (LogLevel.INFO, "Sending reminder email to: {email1} — ${amt1} overdue, {days1} days"),
        (LogLevel.INFO, "Sending reminder email to: {email2} — ${amt2} overdue, {days2} days"),
        (LogLevel.WARNING, "Account #ACC-{acct1} — 90+ days overdue, escalating to collections agency"),
        (LogLevel.INFO, "Generating dunning letter for Account #ACC-{acct2}"),
        (LogLevel.INFO, "Batch complete — {sent} reminders, {escalated} escalated"),
    ],
}

PATIENTS = ["John D.", "Sarah M.", "Robert K.", "Emily W.", "Michael T.", "Lisa R.", "David P.", "Jennifer H."]
PAYERS = ["Aetna PPO", "UHC HMO", "BCBS Gold", "Cigna EPO", "Humana Medicare"]
DIAGNOSIS_CODES = ["E11.65", "M54.5", "J06.9", "I10", "K21.0", "Z23"]


def _generate_logs(run: BotRun, process_name: str) -> list[Log]:
    """Generate realistic log entries for a single bot run."""
    scenario = LOG_SCENARIOS.get(process_name, LOG_SCENARIOS["claims_processing"])
    logs: list[Log] = []

    start = run.start_time or _utcnow()

    for i, (level, template) in enumerate(scenario):
        # Crude template filling — real values aren't critical for demo
        msg = template.format(
            n=random.randint(5, 60),
            seq=random.randint(800, 999),
            seq2=random.randint(800, 999),
            seq3=random.randint(800, 999),
            dup=random.randint(800, 999),
            patient=random.choice(PATIENTS),
            patient2=random.choice(PATIENTS),
            patient3=random.choice(PATIENTS),
            code=random.choice(DIAGNOSIS_CODES),
            delay=random.choice([5, 7, 8, 12]),
            processed=random.randint(3, 20),
            skipped=random.randint(0, 3),
            id1=random.randint(10000, 19999),
            id2=random.randint(10000, 19999),
            id3=random.randint(10000, 19999),
            payer1=random.choice(PAYERS),
            payer2=random.choice(PAYERS),
            verified=random.randint(3, 15),
            flagged=random.randint(0, 3),
            date=start.strftime("%Y%m%d"),
            matched=random.randint(5, 25),
            amt1=f"{random.uniform(200, 3000):.2f}",
            amt2=f"{random.uniform(200, 3000):.2f}",
            acct1=random.randint(800, 999),
            acct2=random.randint(800, 999),
            total=f"{random.uniform(5000, 20000):.2f}",
            seq1=random.randint(4500, 4999),
            seq2_=random.randint(4500, 4999),  # unused alias
            seq4=random.randint(4500, 4999),
            pol1=random.randint(10000, 19999),
            pol2=random.randint(10000, 19999),
            pol3=random.randint(10000, 19999),
            email1=f"client{random.randint(1,99)}@example.com",
            email2=f"client{random.randint(1,99)}@example.com",
            applicant1=random.choice(PATIENTS),
            applicant2=random.choice(PATIENTS),
            rate1=f"{random.uniform(80, 500):.2f}",
            rate2=f"{random.uniform(80, 500):.2f}",
            generated=random.randint(2, 10),
            acct1_=random.randint(5000, 5999),  # unused
            acct2_=random.randint(5000, 5999),  # unused
            days1=random.randint(15, 60),
            days2=random.randint(15, 90),
            sent=random.randint(3, 12),
            escalated=random.randint(0, 3),
        )

        logs.append(Log(
            id=str(uuid.uuid4()),
            run_id=run.id,
            client_id=run.client_id,
            level=level,
            message=msg,
            timestamp=start + timedelta(seconds=i * random.uniform(8, 30)),
        ))

    # If the run failed, tack on error logs
    if run.status == RunStatus.FAILED:
        logs.append(Log(
            id=str(uuid.uuid4()),
            run_id=run.id,
            client_id=run.client_id,
            level=LogLevel.ERROR,
            message=run.error_message or "Unknown error",
            timestamp=start + timedelta(seconds=len(scenario) * 15 + 5),
        ))
        logs.append(Log(
            id=str(uuid.uuid4()),
            run_id=run.id,
            client_id=run.client_id,
            level=LogLevel.CRITICAL,
            message="Bot execution terminated — see error above",
            timestamp=start + timedelta(seconds=len(scenario) * 15 + 10),
        ))

    return logs


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
                username="admin",
                password_hash=pwd_context.hash("admin"),
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

        # ── Bot Runs (rich historical data — 30 days) ────────────
        now = _utcnow()
        all_runs: list[BotRun] = []
        all_logs: list[Log] = []

        # Acme bots: higher run counts (they're busier)
        acme_run_counts = [50, 35, 25, 18]
        acme_success_rates = [0.94, 0.97, 0.88, 0.96]
        acme_process_names = [
            "claims_processing",
            "eligibility_verification",
            "denial_management",
            "payment_posting",
        ]

        for i, bid in enumerate(bot_ids_a):
            runs = _make_runs(
                bid, CLIENT_A_ID,
                count=acme_run_counts[i],
                days_back=30,
                success_pct=acme_success_rates[i],
            )
            all_runs.extend(runs)

            # Generate logs for the 5 most recent runs
            for run in runs[:5]:
                all_logs.extend(_generate_logs(run, acme_process_names[i]))

        # Pinnacle bots: moderate run counts
        pinnacle_run_counts = [20, 15, 12]
        pinnacle_success_rates = [0.92, 0.95, 0.85]
        pinnacle_process_names = [
            "policy_renewal",
            "quote_generation",
            "collections_processing",
        ]

        for i, bid in enumerate(bot_ids_b):
            runs = _make_runs(
                bid, CLIENT_B_ID,
                count=pinnacle_run_counts[i],
                days_back=30,
                success_pct=pinnacle_success_rates[i],
            )
            all_runs.extend(runs)

            for run in runs[:3]:
                all_logs.extend(_generate_logs(run, pinnacle_process_names[i]))

        # ── Mark one Acme bot as currently running ───────────────
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

        # Live logs for the running run
        running_logs = [
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
            (LogLevel.INFO, "Claim #CLM-2024-00894 submitted successfully"),
            (LogLevel.INFO, "Processing claim #CLM-2024-00895 — patient: Robert K."),
            (LogLevel.DEBUG, "OCR scan on denial_letter_895.pdf — extracted 3 fields"),
            (LogLevel.INFO, "Claim #CLM-2024-00895 submitted successfully"),
            (LogLevel.INFO, "Processing claim #CLM-2024-00896 — patient: Emily W."),
            (LogLevel.WARNING, "Duplicate claim detected — matches #CLM-2024-00847, skipping"),
            (LogLevel.INFO, "Processing claim #CLM-2024-00897 — patient: Michael T."),
            (LogLevel.INFO, "Claim #CLM-2024-00897 submitted successfully"),
            (LogLevel.INFO, "Batch progress — 4 of 47 claims processed, 1 duplicate skipped"),
        ]
        for j, (level, msg) in enumerate(running_logs):
            all_logs.append(Log(
                id=str(uuid.uuid4()),
                run_id=running_run.id,
                client_id=CLIENT_A_ID,
                level=level,
                message=msg,
                timestamp=running_run.start_time + timedelta(seconds=j * 10),
            ))

        session.add_all(all_runs)
        session.add_all(all_logs)

        await session.commit()

        # ── Summary ──────────────────────────────────────────────
        succeeded = sum(1 for r in all_runs if r.status == RunStatus.SUCCESS)
        failed = sum(1 for r in all_runs if r.status == RunStatus.FAILED)
        running = sum(1 for r in all_runs if r.status == RunStatus.RUNNING)

        print("✅ Database seeded successfully!")
        print(f"   Clients:  2  (Acme Healthcare, Pinnacle Insurance)")
        print(f"   Users:    3  (admin, viewer@acme, admin@pinnacle)")
        print(f"   Bots:     7  (4 Acme + 3 Pinnacle)")
        print(f"   Runs:     {len(all_runs)}  ({succeeded} success, {failed} failed, {running} running)")
        print(f"   Logs:     {len(all_logs)}")
        print(f"   Spanning: 30 days of historical data")


if __name__ == "__main__":
    asyncio.run(seed())
