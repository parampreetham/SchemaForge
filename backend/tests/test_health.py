"""Tests for health check endpoints."""


def test_health_check(client):
    """Test liveness endpoint returns 200 with status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "schemaforge-api"
    assert "timestamp" in data


def test_health_check_has_correct_content_type(client):
    """Test health endpoint returns JSON content type."""
    response = client.get("/api/v1/health")
    assert "application/json" in response.headers["content-type"]
