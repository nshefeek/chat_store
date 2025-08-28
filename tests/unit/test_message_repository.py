import pytest
import pytest_asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from chat_store.repositories.message_repository import MessageRepository
from chat_store.models.message import Message, MessageStatus, Sender


class TestMessageRepository:
    """Unit tests for MessageRepository."""

    @pytest_asyncio.fixture
    async def repository(self, db_session: AsyncSession) -> MessageRepository:
        """Create a message repository instance."""
        return MessageRepository(db_session)

    @pytest_asyncio.fixture
    async def test_session(self, db_session: AsyncSession):
        """Create a test session for message tests."""
        from chat_store.models.session import Session
        session = Session(user_id="test-user-123", name="Test Session")
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        return session

    @pytest_asyncio.fixture
    async def test_message(self, db_session: AsyncSession, test_session):
        """Create a test message."""
        message = Message(
            session_id=test_session.id,
            sender=Sender.USER,
            content="Test message content",
            context={"test": True}
        )
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)
        return message

    async def test_create_message(self, repository: MessageRepository):
        """Test creating a new message."""
        # Create a session first
        from chat_store.models.session import Session
        session = Session(user_id="test-user-456", name="Test Session")
        # This would need to be handled differently in actual tests
        
        message = Message(
            session_id=UUID("12345678-1234-1234-1234-123456789abc"),
            sender=Sender.AI,
            content="Test AI response",
            context={"response": True}
        )
        
        created = await repository.create(message)
        
        assert created.id is not None
        assert created.sender == Sender.AI
        assert created.content == "Test AI response"
        assert created.status == MessageStatus.PENDING

    async def test_get_by_id(self, repository: MessageRepository, test_message):
        """Test getting message by ID."""
        retrieved = await repository.get_by_id(test_message.id)
        
        assert retrieved is not None
        assert retrieved.id == test_message.id
        assert retrieved.content == test_message.content

    async def test_list_by_session(self, repository: MessageRepository, db_session, test_session):
        """Test listing messages by session."""
        # Create multiple messages
        messages = []
        for i in range(3):
            msg = Message(
                session_id=test_session.id,
                sender=Sender.USER if i % 2 == 0 else Sender.AI,
                content=f"Message {i}"
            )
            messages.append(msg)
            db_session.add(msg)
        await db_session.commit()
        
        listed = await repository.list_by_session(test_session.id)
        assert len(listed) == 3
        assert all(m.session_id == test_session.id for m in listed)

    async def test_count_by_session(self, repository: MessageRepository, db_session, test_session):
        """Test counting messages by session."""
        # Create messages
        for i in range(5):
            msg = Message(
                session_id=test_session.id,
                sender=Sender.USER,
                content=f"Message {i}"
            )
            db_session.add(msg)
        await db_session.commit()
        
        count = await repository.count_by_session(test_session.id)
        assert count == 5

    async def test_get_latest_by_session(self, repository: MessageRepository, db_session, test_session):
        """Test getting latest message by session."""
        # Create messages with different timestamps
        messages = []
        for i in range(3):
            msg = Message(
                session_id=test_session.id,
                sender=Sender.USER,
                content=f"Message {i}"
            )
            messages.append(msg)
            db_session.add(msg)
        await db_session.commit()
        
        latest = await repository.get_latest_by_session(test_session.id)
        assert latest is not None
        assert latest.session_id == test_session.id

    async def test_update_message(self, repository: MessageRepository, test_message):
        """Test updating message."""
        updated = await repository.update(
            test_message.id,
            status=MessageStatus.COMPLETE,
            content="Updated content"
        )
        
        assert updated is not None
        assert updated.status == MessageStatus.COMPLETE
        assert updated.content == "Updated content"

    async def test_delete_message(self, repository: MessageRepository, test_message):
        """Test deleting message."""
        success = await repository.delete(test_message.id)
        assert success is True
        
        retrieved = await repository.get_by_id(test_message.id)
        assert retrieved is None

    async def test_exists(self, repository: MessageRepository, test_message):
        """Test checking if message exists."""
        exists = await repository.exists(test_message.id)
        assert exists is True

    async def test_exists_in_session(self, repository: MessageRepository, test_message):
        """Test checking if messages exist in session."""
        exists = await repository.exists_in_session(test_message.session_id)
        assert exists is True