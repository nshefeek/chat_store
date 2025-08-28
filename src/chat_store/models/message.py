from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import Text, DateTime, ForeignKey, JSON, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from chat_store.db.base import Base, TimeStampMixin, UUIDMixin

if TYPE_CHECKING:
    from chat_store.models.session import Session


class MessageStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"


class Sender(str, Enum):
    USER = "user"
    AI = "ai"


class Message(Base, TimeStampMixin, UUIDMixin):
    __tablename__ = "messages"

    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender: Mapped[Sender] = mapped_column(default=Sender.USER, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict] = mapped_column(JSON, nullable=True)
    status: Mapped[MessageStatus] = mapped_column(default=MessageStatus.PENDING, nullable=False, index=True)
    partial_content: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False, index=True)

    session: Mapped["Session"] = relationship(back_populates="messages", lazy="joined")