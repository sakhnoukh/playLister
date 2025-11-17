"""Tests for song routes."""

import pytest


def test_get_songs_success(client):
    """Test getting all songs."""
    response = client.get("/api/songs")
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check song structure
    song = data[0]
    assert "id" in song
    assert "title" in song
    assert "artist" in song


def test_get_songs_with_search(client):
    """Test searching songs by title/artist."""
    # Get all songs first to know what exists
    all_response = client.get("/api/songs")
    all_songs = all_response.get_json()
    
    if len(all_songs) > 0:
        # Search for part of first song's title
        search_term = all_songs[0]["title"][:5]
        response = client.get(f"/api/songs?search={search_term}")
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)


def test_get_songs_with_genre_filter(client):
    """Test filtering songs by genre."""
    # Get all songs first
    all_response = client.get("/api/songs")
    all_songs = all_response.get_json()
    
    if len(all_songs) > 0:
        genre = all_songs[0]["subgenre"]
        response = client.get(f"/api/songs?genre={genre}")
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        # All returned songs should have the requested genre
        for song in data:
            assert song["subgenre"] == genre


def test_get_songs_titles_only(client):
    """Test getting songs with titles_only flag."""
    response = client.get("/api/songs?titles_only=true")
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    
    if len(data) > 0:
        song = data[0]
        # Should have limited fields
        assert "id" in song
        assert "title" in song
        assert "artist" in song


def test_get_songs_combined_filters(client):
    """Test combining search and genre filters."""
    response = client.get("/api/songs?genre=deep-house&search=love")
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
