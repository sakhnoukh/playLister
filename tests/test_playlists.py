"""Tests for playlist routes."""

import pytest


def test_generate_playlist_cold_start(client, sample_user):
    """Test generating playlist without prior feedback (cold start)."""
    response = client.post(
        "/api/playlists/generate",
        json={"user_id": sample_user["id"], "count": 10}
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) <= 10


def test_generate_playlist_with_feedback(client, sample_user, sample_songs):
    """Test generating playlist with user feedback."""
    # Submit some feedback first
    for i, song in enumerate(sample_songs[:3]):
        client.post(
            "/api/quiz/answer",
            json={
                "user_id": sample_user["id"],
                "song_id": song["id"],
                "liked": i % 2 == 0  # Like every other song
            }
        )
    
    # Generate playlist
    response = client.post(
        "/api/playlists/generate",
        json={"user_id": sample_user["id"], "count": 15}
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) <= 15


def test_generate_playlist_with_genre(client, sample_user):
    """Test generating playlist with genre filter."""
    response = client.post(
        "/api/playlists/generate",
        json={"user_id": sample_user["id"], "count": 10, "genre": "deep-house"}
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)


def test_generate_playlist_missing_user_id(client):
    """Test generating playlist without user_id fails."""
    response = client.post(
        "/api/playlists/generate",
        json={"count": 10}
    )
    assert response.status_code == 400


def test_generate_playlist_invalid_user(client):
    """Test generating playlist with invalid user."""
    response = client.post(
        "/api/playlists/generate",
        json={"user_id": 99999, "count": 10}
    )
    assert response.status_code == 404


def test_create_playlist_success(client, sample_user, sample_songs):
    """Test creating and saving a playlist."""
    song_ids = [song["id"] for song in sample_songs[:5]]
    
    response = client.post(
        "/api/playlists",
        json={
            "user_id": sample_user["id"],
            "name": "My Test Playlist",
            "song_ids": song_ids
        }
    )
    assert response.status_code == 201
    
    data = response.get_json()
    assert "playlist_id" in data
    assert isinstance(data["playlist_id"], int)


def test_create_playlist_missing_fields(client, sample_user):
    """Test creating playlist with missing fields."""
    response = client.post(
        "/api/playlists",
        json={"user_id": sample_user["id"]}
    )
    assert response.status_code == 400


def test_create_playlist_invalid_song(client, sample_user):
    """Test creating playlist with invalid song ID."""
    response = client.post(
        "/api/playlists",
        json={
            "user_id": sample_user["id"],
            "name": "Test Playlist",
            "song_ids": [99999]
        }
    )
    assert response.status_code == 404


def test_get_user_playlists(client, sample_user, sample_songs):
    """Test getting user's playlists."""
    # Create a playlist first
    song_ids = [song["id"] for song in sample_songs[:3]]
    client.post(
        "/api/playlists",
        json={
            "user_id": sample_user["id"],
            "name": "Test Playlist",
            "song_ids": song_ids
        }
    )
    
    # Get playlists
    response = client.get(f"/api/playlists?user_id={sample_user['id']}")
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "Test Playlist"
    assert "song_count" in data[0]


def test_get_user_playlists_missing_user_id(client):
    """Test getting playlists without user_id."""
    response = client.get("/api/playlists")
    assert response.status_code == 400


def test_get_playlist_detail(client, sample_user, sample_songs):
    """Test getting detailed playlist with songs."""
    # Create a playlist
    song_ids = [song["id"] for song in sample_songs[:3]]
    create_response = client.post(
        "/api/playlists",
        json={
            "user_id": sample_user["id"],
            "name": "Detail Test",
            "song_ids": song_ids
        }
    )
    playlist_id = create_response.get_json()["playlist_id"]
    
    # Get playlist detail
    response = client.get(f"/api/playlists/{playlist_id}")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["name"] == "Detail Test"
    assert "songs" in data
    assert len(data["songs"]) == 3
    
    # Check song structure
    for item in data["songs"]:
        assert "position" in item
        assert "song" in item


def test_get_playlist_not_found(client):
    """Test getting non-existent playlist."""
    response = client.get("/api/playlists/99999")
    assert response.status_code == 404


def test_delete_playlist_success(client, sample_user, sample_songs):
    """Test deleting a playlist."""
    # Create a playlist
    song_ids = [song["id"] for song in sample_songs[:2]]
    create_response = client.post(
        "/api/playlists",
        json={
            "user_id": sample_user["id"],
            "name": "To Delete",
            "song_ids": song_ids
        }
    )
    playlist_id = create_response.get_json()["playlist_id"]
    
    # Delete playlist
    response = client.delete(f"/api/playlists/{playlist_id}")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["status"] == "success"
    
    # Verify it's deleted
    get_response = client.get(f"/api/playlists/{playlist_id}")
    assert get_response.status_code == 404


def test_delete_playlist_not_found(client):
    """Test deleting non-existent playlist."""
    response = client.delete("/api/playlists/99999")
    assert response.status_code == 404
