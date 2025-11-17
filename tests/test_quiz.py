"""Tests for quiz routes."""

import pytest


def test_start_quiz_success(client, sample_user):
    """Test starting a quiz."""
    response = client.post(
        "/api/quiz/start",
        json={"user_id": sample_user["id"], "n": 5}
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 5
    
    # Check song structure
    for song in data:
        assert "id" in song
        assert "title" in song
        assert "artist" in song


def test_start_quiz_default_count(client, sample_user):
    """Test starting quiz with default count."""
    response = client.post(
        "/api/quiz/start",
        json={"user_id": sample_user["id"]}
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 10


def test_start_quiz_missing_user_id(client):
    """Test starting quiz without user_id fails."""
    response = client.post("/api/quiz/start", json={"n": 5})
    assert response.status_code == 400
    
    data = response.get_json()
    assert "error" in data


def test_start_quiz_invalid_user(client):
    """Test starting quiz with non-existent user."""
    response = client.post(
        "/api/quiz/start",
        json={"user_id": 99999, "n": 5}
    )
    assert response.status_code == 404
    
    data = response.get_json()
    assert "error" in data


def test_answer_quiz_success(client, sample_user, sample_songs):
    """Test submitting quiz answer."""
    response = client.post(
        "/api/quiz/answer",
        json={
            "user_id": sample_user["id"],
            "song_id": sample_songs[0]["id"],
            "liked": True
        }
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["status"] == "success"


def test_answer_quiz_update_existing(client, sample_user, sample_songs):
    """Test updating existing quiz answer."""
    song_id = sample_songs[0]["id"]
    
    # Submit first answer
    client.post(
        "/api/quiz/answer",
        json={"user_id": sample_user["id"], "song_id": song_id, "liked": True}
    )
    
    # Update answer
    response = client.post(
        "/api/quiz/answer",
        json={"user_id": sample_user["id"], "song_id": song_id, "liked": False}
    )
    assert response.status_code == 200


def test_answer_quiz_missing_fields(client, sample_user):
    """Test submitting quiz answer with missing fields."""
    response = client.post(
        "/api/quiz/answer",
        json={"user_id": sample_user["id"]}
    )
    assert response.status_code == 400
    
    data = response.get_json()
    assert "error" in data


def test_answer_quiz_invalid_user(client, sample_songs):
    """Test submitting answer with invalid user."""
    response = client.post(
        "/api/quiz/answer",
        json={"user_id": 99999, "song_id": sample_songs[0]["id"], "liked": True}
    )
    assert response.status_code == 404


def test_answer_quiz_invalid_song(client, sample_user):
    """Test submitting answer with invalid song."""
    response = client.post(
        "/api/quiz/answer",
        json={"user_id": sample_user["id"], "song_id": 99999, "liked": True}
    )
    assert response.status_code == 404
