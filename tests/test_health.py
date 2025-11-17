"""Tests for health check endpoint."""

import pytest


def test_health_endpoint_success(client):
    """Test health endpoint returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["status"] in ["ok", "degraded"]
    assert "version" in data
    assert "db" in data
    assert "latency_ms" in data
    assert data["db"] in ["ok", "down"]


def test_health_endpoint_has_version(client):
    """Test health endpoint includes version."""
    response = client.get("/health")
    data = response.get_json()
    
    assert "version" in data
    assert isinstance(data["version"], str)


def test_health_endpoint_db_check(client):
    """Test health endpoint checks database."""
    response = client.get("/health")
    data = response.get_json()
    
    # Should be ok since we have a working test database
    assert data["db"] == "ok"
    assert data["status"] == "ok"
    assert isinstance(data["latency_ms"], (int, float))
    assert data["latency_ms"] >= 0
