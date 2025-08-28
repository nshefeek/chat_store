"""
Test to verify that all fixtures are working correctly.
"""
import pytest
from uuid import UUID

# Test basic fixture functionality
class TestFixtures:
    
    def test_sample_data_fixtures(self, sample_session_data, sample_message_data):
        """Test that sample data fixtures are available."""
        assert "user_id" in sample_session_data
        assert "name" in sample_session_data
        assert "sender" in sample_message_data
        assert "content" in sample_message_data
    
    def test_auth_fixtures(self, valid_api_key, invalid_api_key, auth_headers):
        """Test that auth fixtures are available."""
        assert isinstance(valid_api_key, str)
        assert isinstance(invalid_api_key, str)
        assert "Authorization" in auth_headers
    
    def test_schema_fixtures(self, session_create_data, message_create_data):
        """Test that schema fixtures are available."""
        assert "user_id" in session_create_data
        assert "sender" in message_create_data
    
    @pytest.mark.asyncio
    async def test_database_fixture(self, db_session):
        """Test that database session fixture works."""
        assert db_session is not None
    
    @pytest.mark.asyncio
    async def test_model_fixtures(self, test_session, test_message):
        """Test that model fixtures work."""
        assert test_session.id is not None
        assert test_message.id is not None
        assert test_message.session_id == test_session.id
    
    @pytest.mark.asyncio
    async def test_bulk_fixtures(self, test_sessions_bulk, test_messages_bulk):
        """Test that bulk fixtures work."""
        assert len(test_sessions_bulk) == 5
        assert len(test_messages_bulk) >= 2
    
    def test_uuid_fixtures(self, sample_user_id, sample_session_id, sample_message_id):
        """Test that UUID fixtures are valid."""
        # Check if they can be converted to UUID
        try:
            UUID(sample_user_id)
            UUID(sample_session_id)
            UUID(sample_message_id)
            assert True
        except ValueError:
            pytest.fail("Invalid UUID format in fixtures")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])