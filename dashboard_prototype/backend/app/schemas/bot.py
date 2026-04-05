"""
Bot-related Pydantic schemas for request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class BotCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    process_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    script_path: str | None = None


class BotOut(BaseModel):
    id: str
    client_id: str
    name: str
    process_name: str
    description: str | None
    script_path: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BotWithStatus(BotOut):
    """Bot with its current runtime status (from Redis or latest run)."""
    current_status: str = "idle"  # idle | running | failed | success
    last_run_at: datetime | None = None
    total_runs: int = 0
    success_rate: float = 0.0
    active_run_id: str | None = None


class BotRunRequest(BaseModel):
    """Request to start a bot execution."""
    bot_id: str
    parameters: dict | None = None  # Optional runtime parameters


class BotStopRequest(BaseModel):
    """Request to stop a running bot."""
    bot_id: str
    run_id: str | None = None  # If None, stop the currently active run
    force: bool = False
