from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from chat_store.db.base import Base, TimeStampMixin, UUIDMixin

if TYPE_CHECKING:
    from chat_store.models.message import Message


class Session(Base, TimeStampMixin, UUIDMixin):
    __tablename__ = "sessions"

    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    name: Mapped[str] = mapped_column(default="New Chat", nullable=False, index=True)
    is_favorite: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

    messages: Mapped[list["Message"]] = relationship(back_populates="session", cascade="all, delete-orphan", lazy="joined")