"""
Log Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel


class LogOut(BaseModel):
    id: str
    run_id: str
    level: str
    message: str
    metadata_json: dict | None = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class LogListOut(BaseModel):
    logs: list[LogOut]
    total: int
