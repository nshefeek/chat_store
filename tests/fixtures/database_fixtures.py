"""
Database fixtures for testing.
"""
import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncpg

from chat_store.main import app
from chat_store.db.base import Base, get_db
from chat_store.core.config import config


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