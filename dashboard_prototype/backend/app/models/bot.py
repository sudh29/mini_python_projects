"""
Bot model — represents an automation bot owned by a client.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.bot_run import BotRun


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Bot(Base):
    __tablename__ = "bots"
    __table_args__ = (
        Index("ix_bots_client_process", "client_id", "process_name"),
        Index("ix_bots_client_active", "client_id", "is_active"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    process_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    script_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    client: Mapped["Client"] = relationship(back_populates="bots")
    runs: Mapped[list["BotRun"]] = relationship(back_populates="bot", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Bot {self.name} ({self.process_name})>"
