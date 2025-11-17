"""Tests for user routes."""

import pytest


def test_create_user_success(client):
    """Test creating a new user."""
    response = client.post(
        "/api/users",
        json={"name": "NewUser"}
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["name"] == "NewUser"
    assert "id" in data
    assert "created_at" in data


def test_create_user_duplicate_returns_existing(client):
    """Test creating duplicate user returns existing user."""
    # Create first user
    response1 = client.post("/api/users", json={"name": "DuplicateUser"})
    user1 = response1.get_json()
    
    # Try to create same user again
    response2 = client.post("/api/users", json={"name": "DuplicateUser"})
    user2 = response2.get_json()
    
    # Should return the same user
    assert user1["id"] == user2["id"]
    assert user1["name"] == user2["name"]


def test_create_user_missing_name(client):
    """Test creating user without name fails."""
    response = client.post("/api/users", json={})
    assert response.status_code == 400
    
    data = response.get_json()
    assert "error" in data


def test_create_user_invalid_json(client):
    """Test creating user with invalid JSON fails."""
    response = client.post(
        "/api/users",
        data="not json",
        content_type="text/plain"
    )
    assert response.status_code == 400


def test_create_user_empty_name(client):
    """Test creating user with empty name fails."""
    response = client.post("/api/users", json={"name": ""})
    assert response.status_code == 400
    
    data = response.get_json()
    assert "error" in data
