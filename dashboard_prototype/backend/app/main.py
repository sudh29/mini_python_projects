"""
FastAPI Application — main entry point.

Assembles all routes, middleware, and lifecycle events.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import init_db, close_db, get_db
from app import prometheus_metrics  # Ensure custom metrics are registered
from app.models.client import User
from app.auth.dependencies import verify_password, create_access_token

# ── Routers ──────────────────────────────────────────────────────
from app.api.bots import router as bots_router
from app.api.logs import router as logs_router
from app.api.screenshots import router as screenshots_router
from app.api.metrics import router as metrics_router
from app.ws.status import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # ── Startup ──────────────────────────────────────────────────
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    print("✅ Database initialized")
    yield
    # ── Shutdown ─────────────────────────────────────────────────
    await close_db()
    print("👋 Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Jorie AI — RPA Orchestration & Monitoring Control Plane",
    lifespan=lifespan,
)

# ── Metrics ──────────────────────────────────────────────────────
Instrumentator().instrument(app).expose(app)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ──────────────────────────────────────────────
app.include_router(bots_router)
app.include_router(logs_router)
app.include_router(screenshots_router)
app.include_router(metrics_router)
app.include_router(ws_router)


# ── Auth Route (Login) ──────────────────────────────────────────
@app.post("/api/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT token."""
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({
        "user_id": user.id,
        "client_id": user.client_id,
        "role": user.role.value,
        "username": user.username,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role.value,
            "client_id": user.client_id,
        },
    }


# ── Health Check ─────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}
