from uuid import uuid4
from datetime import datetime, timezone

from chat_store.models.session import Session
from chat_store.models.message import Message, MessageStatus, Sender


class TestSessionModel:
    def test_session_creation(self):
        user_id = uuid4()
        session = Session(
            id=uuid4(),
            user_id=user_id,
            name="Test Chat",
            is_favorite=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assert session.user_id == user_id
        assert session.name == "Test Chat"
        assert session.is_favorite is True
        assert session.created_at is not None
        assert session.updated_at is not None


class TestMessageModel:
    def test_message_creation(self):
        session_id = uuid4()
        message = Message(
            id=uuid4(),
            session_id=session_id,
            sender=Sender.USER,
            content="Hello, world!",
            status=MessageStatus.PENDING,
            context={"key": "value"},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assert message.session_id == session_id
        assert message.sender == Sender.USER
        assert message.content == "Hello, world!"
        assert message.status == MessageStatus.PENDING
        assert message.context == {"key": "value"}
        assert message.created_at is not None
        assert message.updated_at is not None

    def test_message_status_enum(self):
        assert MessageStatus.PENDING.value == "pending"
        assert MessageStatus.IN_PROGRESS.value == "in_progress"
        assert MessageStatus.COMPLETE.value == "complete"
        assert MessageStatus.FAILED.value == "failed"

    def test_sender_enum(self):
        assert Sender.USER.value == "user"
        assert Sender.AI.value == "ai"