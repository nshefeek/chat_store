"""
Schema fixtures for testing.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from chat_store.schemas.session import SessionCreate, SessionUpdate, Session as SessionSchema
from chat_store.schemas.message import MessageCreate, Message as MessageSchema
from chat_store.models.message import Sender, MessageStatus


@pytest.fixture
def session_create_data():
    """Valid session creation data."""
    return {
        "user_id": str(uuid4()),
        "name": "New Test Session",
        "is_favorite": False
    }


@pytest.fixture
def session_create_minimal_data():
    """Minimal session creation data."""
    return {
        "user_id": str(uuid4())
    }


@pytest.fixture
def session_update_data():
    """Valid session update data."""
    return {
        "name": "Updated Session Name",
        "is_favorite": True
    }


@pytest.fixture
def session_update_partial_data():
    """Partial session update data."""
    return {
        "name": "Only Name Updated"
    }


@pytest.fixture
def message_create_data():
    """Valid message creation data."""
    return {
        "sender": Sender.USER,
        "content": "Hello, this is a test message",
        "context": {"test": True, "metadata": {"source": "test"}}
    }


@pytest.fixture
def message_create_ai_data():
    """Valid AI message creation data."""
    return {
        "sender": Sender.AI,
        "content": "This is an AI response",
        "context": {"response_type": "answer", "confidence": 0.95}
    }


@pytest.fixture
def message_create_minimal_data():
    """Minimal message creation data."""
    return {
        "sender": Sender.USER,
        "content": "Simple message"
    }


@pytest.fixture
def session_schema_dict():
    """Dictionary representation of session schema."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "Test Session",
        "is_favorite": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def message_schema_dict():
    """Dictionary representation of message schema."""
    return {
        "id": str(uuid4()),
        "session_id": str(uuid4()),
        "sender": Sender.USER.value,
        "content": "Test message content",
        "context": {"test": True},
        "status": MessageStatus.PENDING.value,
        "partial_content": None,
        "error_message": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def session_create_schema(session_create_data):
    """SessionCreate schema instance."""
    return SessionCreate(**session_create_data)


@pytest.fixture
def session_update_schema(session_update_data):
    """SessionUpdate schema instance."""
    return SessionUpdate(**session_update_data)


@pytest.fixture
def message_create_schema(message_create_data):
    """MessageCreate schema instance."""
    return MessageCreate(**message_create_data)


@pytest.fixture
def session_schema_list():
    """List of session schemas for testing pagination."""
    sessions = []
    for i in range(5):
        sessions.append({
            "id": str(uuid4()),
            "user_id": str(uuid4()),
            "name": f"Test Session {i+1}",
            "is_favorite": i % 2 == 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    return sessions


@pytest.fixture
def message_schema_list():
    """List of message schemas for testing pagination."""
    messages = []
    session_id = str(uuid4())
    for i in range(10):
        messages.append({
            "id": str(uuid4()),
            "session_id": session_id,
            "sender": Sender.USER.value if i % 2 == 0 else Sender.AI.value,
            "content": f"Message {i+1}",
            "context": {"sequence": i+1},
            "status": MessageStatus.COMPLETE.value,
            "partial_content": None,
            "error_message": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    return messages