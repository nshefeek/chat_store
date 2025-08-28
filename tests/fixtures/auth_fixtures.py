"""
Authentication fixtures for testing.
"""
import pytest
from chat_store.core.config import config


@pytest.fixture
def valid_api_key():
    """Valid API key for testing."""
    return config.auth.API_KEY


@pytest.fixture
def invalid_api_key():
    """Invalid API key for testing."""
    return "invalid-api-key-12345"


@pytest.fixture
def expired_api_key():
    """Expired API key for testing."""
    return "expired-key-67890"


@pytest.fixture
def auth_headers(valid_api_key):
    """Valid authorization headers."""
    return {"Authorization": f"Bearer {valid_api_key}"}


@pytest.fixture
def invalid_auth_headers(invalid_api_key):
    """Invalid authorization headers."""
    return {"Authorization": f"Bearer {invalid_api_key}"}


@pytest.fixture
def malformed_auth_headers():
    """Malformed authorization headers."""
    return {"Authorization": "InvalidFormat no-bearer-prefix"}


@pytest.fixture
def missing_auth_headers():
    """Missing authorization headers."""
    return {}


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test-user-123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def sample_user_id_2():
    """Second sample user ID for testing."""
    return "test-user-987e6543-e21b-12d3-a456-426614174001"


@pytest.fixture
def sample_session_id():
    """Sample session ID for testing."""
    return "test-session-123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def sample_message_id():
    """Sample message ID for testing."""
    return "test-message-123e4567-e89b-12d3-a456-426614174000"