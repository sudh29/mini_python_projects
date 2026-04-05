"""
BotRun Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel


class BotRunOut(BaseModel):
    id: str
    bot_id: str
    client_id: str
    celery_task_id: str | None
    status: str
    start_time: datetime | None
    end_time: datetime | None
    error_message: str | None
    retry_count: int
    artifacts_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BotRunListOut(BaseModel):
    runs: list[BotRunOut]
    total: int
