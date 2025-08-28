"""
Pytest configuration and fixtures for chat_store tests.

This file contains shared fixtures and configuration for all test files.
"""
import asyncio
import os
import sys
from typing import AsyncGenerator, Generator

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncpg

from chat_store.main import app
from chat_store.db.base import Base, get_db
from chat_store.core.config import config
from chat_store.models.session import Session
from chat_store.models.message import Message, Sender


# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/chat_store_test"

# Create test engine
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine() -> AsyncGenerator:
    """Create database engine for testing."""
    # Create test database if it doesn't exist
    try:
        conn = await asyncpg.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres",
        )
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            "chat_store_test",
        )
        if not exists:
            await conn.execute("CREATE DATABASE chat_store_test")
        await conn.close()
    except Exception as e:
        print(f"Warning: Could not ensure test database exists: {e}")
    
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def override_get_db(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Override the get_db dependency for testing."""
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Import all fixtures from the fixtures module
from tests.fixtures.database_fixtures import *  # noqa: E402, F403
from tests.fixtures.model_fixtures import *  # noqa: E402, F403
from tests.fixtures.schema_fixtures import *  # noqa: E402, F403
from tests.fixtures.auth_fixtures import *  # noqa: E402, F403


# Legacy fixtures for backward compatibility
@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "user_id": "test-user-123",
        "name": "Test Chat Session",
        "is_favorite": False
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "sender": Sender.USER,
        "content": "Hello, this is a test message",
        "context": {"test": True}
    }


@pytest_asyncio.fixture
async def test_session(db_session: AsyncSession) -> Session:
    """Create a test session."""
    session = Session(
        user_id="test-user-123",
        name="Test Session",
        is_favorite=False
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


@pytest_asyncio.fixture
async def test_messages(db_session: AsyncSession, test_session: Session) -> list[Message]:
    """Create test messages."""
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
    
    db_session.add_all(messages)
    await db_session.commit()
    
    for msg in messages:
        await db_session.refresh(msg)
    
    return messages


@pytest.fixture
def api_key():
    """Test API key."""
    return config.auth.API_KEY


@pytest.fixture
def auth_headers(api_key):
    """Return authorization headers."""
    return {"Authorization": f"Bearer {api_key}"}


@pytest.fixture
def invalid_api_key():
    """Invalid API key for testing."""
    return "invalid-api-key"


@pytest.fixture
def invalid_auth_headers(invalid_api_key):
    """Return invalid authorization headers."""
    return {"Authorization": f"Bearer {invalid_api_key}"}