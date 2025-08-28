# Test Fixtures Documentation

This directory contains comprehensive test fixtures for the chat_store application.

## Directory Structure

```
fixtures/
├── __init__.py           # Exports all fixtures
├── database_fixtures.py  # Database and session fixtures
├── model_fixtures.py     # Model instance fixtures
├── schema_fixtures.py    # Schema validation fixtures
├── auth_fixtures.py      # Authentication fixtures
└── README.md            # This documentation
```

## Available Fixtures

### Database Fixtures (database_fixtures.py)

| Fixture | Scope | Description |
|---------|--------|-------------|
| `event_loop` | session | Async event loop for tests |
| `db_engine` | session | Database engine for testing |
| `db_session` | function | Fresh database session per test |
| `override_get_db` | function | Dependency override for FastAPI |
| `client` | function | HTTP test client |

### Model Fixtures (model_fixtures.py)

| Fixture | Description |
|---------|-------------|
| `sample_user_id` | UUID string for testing |
| `sample_session_id` | UUID for session testing |
| `sample_message_id` | UUID for message testing |
| `sample_session_data` | Basic session data dict |
| `sample_message_data` | Basic message data dict |
| `test_session` | Actual Session model instance |
| `test_favorite_session` | Session with is_favorite=True |
| `test_sessions_bulk` | List of 5 test sessions |
| `test_message` | Actual Message model instance |
| `test_messages_bulk` | List of test messages |
| `test_messages_different_statuses` | Messages with all status types |

### Schema Fixtures (schema_fixtures.py)

| Fixture | Description |
|---------|-------------|
| `session_create_data` | Valid SessionCreate data |
| `session_create_minimal_data` | Minimal required session data |
| `session_update_data` | Valid SessionUpdate data |
| `message_create_data` | Valid MessageCreate data |
| `message_create_ai_data` | AI message creation data |
| `session_create_schema` | SessionCreate schema instance |
| `message_create_schema` | MessageCreate schema instance |

### Auth Fixtures (auth_fixtures.py)

| Fixture | Description |
|---------|-------------|
| `valid_api_key` | Valid API key from config |
| `invalid_api_key` | Invalid API key for testing |
| `auth_headers` | Valid authorization headers |
| `invalid_auth_headers` | Invalid authorization headers |
| `malformed_auth_headers` | Malformed auth headers |
| `missing_auth_headers` | Empty headers dict |

## Usage Examples

### Basic Test with Database

```python
import pytest

@pytest.mark.asyncio
async def test_create_session(db_session, sample_session_data):
    session = Session(**sample_session_data)
    db_session.add(session)
    await db_session.commit()
    assert session.id is not None
```

### Test with HTTP Client

```python
import pytest

@pytest.mark.asyncio
async def test_create_session_endpoint(client, auth_headers, session_create_data):
    response = await client.post(
        "/api/v1/sessions",
        json=session_create_data,
        headers=auth_headers
    )
    assert response.status_code == 201
```

### Test with Bulk Data

```python
import pytest

@pytest.mark.asyncio
async def test_list_sessions_pagination(client, auth_headers, test_sessions_bulk):
    response = await client.get(
        "/api/v1/sessions?skip=2&limit=2",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) == 2
```

### Test with Different Message Statuses

```python
import pytest

@pytest.mark.asyncio
async def test_filter_messages_by_status(test_messages_different_statuses):
    pending_messages = [m for m in test_messages_different_statuses 
                       if m.status == MessageStatus.PENDING]
    assert len(pending_messages) >= 1
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_fixtures.py -v

# Run with coverage
pytest --cov=src/chat_store tests/

# Run async tests only
pytest -m asyncio
```

## Adding New Fixtures

1. Create the fixture in the appropriate file
2. Add it to the `__init__.py` exports
3. Update this README
4. Add tests to `test_fixtures.py`

## Best Practices

1. **Scope appropriately**: Use `function` scope for database-isolated fixtures
2. **Cleanup**: Always clean up test data in fixtures
3. **Naming**: Use descriptive names like `test_user_message` vs `sample_message_data`
4. **Dependencies**: Chain fixtures appropriately (e.g., `test_message` depends on `test_session`)
5. **Validation**: Include fixtures for both valid and invalid data