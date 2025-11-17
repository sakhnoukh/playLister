"""Tests for metrics endpoint."""

import pytest


def test_metrics_endpoint_exists(client):
    """Test metrics endpoint is accessible."""
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_endpoint_format(client):
    """Test metrics endpoint returns Prometheus format."""
    response = client.get("/metrics")
    data = response.data.decode('utf-8')
    
    # Check for Prometheus format indicators
    assert "# HELP" in data or "# TYPE" in data or "playlister" in data


def test_metrics_includes_app_info(client):
    """Test metrics includes app info."""
    response = client.get("/metrics")
    data = response.data.decode('utf-8')
    
    # Should contain app_info metric
    assert "playlister_app_info" in data or "app_info" in data


def test_metrics_includes_http_metrics(client):
    """Test metrics includes HTTP request metrics."""
    # Make a few requests to generate metrics
    client.get("/health")
    client.get("/api/songs")
    
    response = client.get("/metrics")
    data = response.data.decode('utf-8')
    
    # Should track requests
    assert "http" in data.lower() or "request" in data.lower()
