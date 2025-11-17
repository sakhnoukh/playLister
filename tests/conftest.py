"""Pytest configuration and fixtures."""

import os
import tempfile
import pytest
from pathlib import Path

from app import create_app
from app.database import init_db


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Set environment for test config
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Create app with test config
    app = create_app("test")
    app.config.update({
        "TESTING": True,
        "DATABASE_URL": f"sqlite:///{db_path}",
    })
    
    # Initialize database with seed data
    init_db(db_path)
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(client):
    """Create a sample user for testing."""
    response = client.post(
        "/api/users",
        json={"name": "TestUser"}
    )
    return response.get_json()


@pytest.fixture
def sample_songs(app):
    """Get sample songs from the database."""
    from app.database import get_db
    from app.services.song_service import SongService
    
    with app.app_context():
        db = get_db()
        songs = SongService.get_all_songs(db)
        return songs[:5]  # Return first 5 songs
