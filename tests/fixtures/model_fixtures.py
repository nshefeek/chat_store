"""
Model fixtures for testing.
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timezone

from chat_store.models.session import Session
from chat_store.models.message import Message, MessageStatus, Sender


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return str(uuid4())


@pytest.fixture
def sample_session_id():
    """Sample session ID for testing."""
    return uuid4()


@pytest.fixture
def sample_message_id():
    """Sample message ID for testing."""
    return uuid4()


@pytest.fixture
def sample_session_data(sample_user_id):
    """Sample session data for testing."""
    return {
        "user_id": sample_user_id,
        "name": "Test Chat Session",
        "is_favorite": False
    }


@pytest.fixture
def sample_session_data_with_favorite(sample_user_id):
    """Sample session data with favorite flag."""
    return {
        "user_id": sample_user_id,
        "name": "Favorite Chat Session",
        "is_favorite": True
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "sender": Sender.USER,
        "content": "Hello, this is a test message",
        "context": {"test": True}
    }


@pytest.fixture
def sample_ai_message_data():
    """Sample AI message data for testing."""
    return {
        "sender": Sender.AI,
        "content": "Hello! How can I help you today?",
        "context": {"type": "ai_response"}
    }


@pytest.fixture
def sample_message_data_with_status():
    """Sample message data with specific status."""
    return {
        "sender": Sender.USER,
        "content": "Test message with status",
        "status": MessageStatus.COMPLETE,
        "context": {"priority": "high"}
    }


@pytest_asyncio.fixture
async def test_session(db_session, sample_user_id) -> Session:
    """Create a test session."""
    session = Session(
        user_id=sample_user_id,
        name="Test Session",
        is_favorite=False
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


@pytest_asyncio.fixture
async def test_favorite_session(db_session, sample_user_id) -> Session:
    """Create a test favorite session."""
    session = Session(
        user_id=sample_user_id,
        name="Favorite Test Session",
        is_favorite=True
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


@pytest_asyncio.fixture
async def test_sessions_bulk(db_session, sample_user_id) -> list[Session]:
    """Create multiple test sessions for bulk operations."""
    sessions = []
    for i in range(5):
        session = Session(
            user_id=sample_user_id,
            name=f"Test Session {i+1}",
            is_favorite=(i % 2 == 0)
        )
        sessions.append(session)
        db_session.add(session)
    
    await db_session.commit()
    
    for session in sessions:
        await db_session.refresh(session)
    
    return sessions


@pytest_asyncio.fixture
async def test_message(db_session, test_session) -> Message:
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


@pytest_asyncio.fixture
async def test_messages_bulk(db_session, test_session) -> list[Message]:
    """Create multiple test messages for bulk operations."""
    messages = []
    
    # Create user message
    user_msg = Message(
        session_id=test_session.id,
        sender=Sender.USER,
        content="Hello, this is a user message",
        context={"type": "user_input"}
    )
    messages.append(user_msg)
    
    # Create AI message
    ai_msg = Message(
        session_id=test_session.id,
        sender=Sender.AI,
        content="Hello! How can I help you today?",
        context={"type": "ai_response"}
    )
    messages.append(ai_msg)
    
    # Create additional messages
    for i in range(3):
        msg = Message(
            session_id=test_session.id,
            sender=Sender.USER if i % 2 == 0 else Sender.AI,
            content=f"Message {i+1}",
            context={"sequence": i+1}
        )
        messages.append(msg)
    
    db_session.add_all(messages)
    await db_session.commit()
    
    for msg in messages:
        await db_session.refresh(msg)
    
    return messages


@pytest_asyncio.fixture
async def test_messages_different_statuses(db_session, test_session) -> list[Message]:
    """Create test messages with different statuses."""
    messages = []
    statuses = [MessageStatus.PENDING, MessageStatus.IN_PROGRESS, MessageStatus.COMPLETE, MessageStatus.FAILED]
    
    for i, status in enumerate(statuses):
        msg = Message(
            session_id=test_session.id,
            sender=Sender.AI if i % 2 == 0 else Sender.USER,
            content=f"Message with status {status.value}",
            status=status,
            context={"status": status.value}
        )
        messages.append(msg)
        db_session.add(msg)
    
    await db_session.commit()
    
    for msg in messages:
        await db_session.refresh(msg)
    
    return messages


@pytest.fixture
def session_model_dict(sample_user_id):
    """Dictionary representation of a session model."""
    return {
        "id": uuid4(),
        "user_id": sample_user_id,
        "name": "Test Session",
        "is_favorite": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def message_model_dict(sample_session_id):
    """Dictionary representation of a message model."""
    return {
        "id": uuid4(),
        "session_id": sample_session_id,
        "sender": Sender.USER,
        "content": "Test message",
        "status": MessageStatus.PENDING,
        "context": {"test": True},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }