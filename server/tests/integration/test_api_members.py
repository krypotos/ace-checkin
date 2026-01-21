"""
Integration tests for Member API endpoints.

These tests use a test database and test the full request/response cycle.
"""

from fastapi.testclient import TestClient

from app.models import Member


class TestMemberEndpoints:
    """Tests for /api/members endpoints."""

    def test_create_member_success(self, client: TestClient, valid_member_data: dict):
        """Test successful member creation."""
        response = client.post("/api/members", json=valid_member_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == valid_member_data["name"]
        assert data["email"] == valid_member_data["email"]
        assert data["phone"] == valid_member_data["phone"]
        assert "id" in data
        assert "created_at" in data

    def test_create_member_minimal(self, client: TestClient):
        """Test member creation with only required fields."""
        response = client.post("/api/members", json={"name": "Minimal Member"})

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Minimal Member"
        assert data["email"] is None
        assert data["phone"] is None

    def test_create_member_invalid_name_empty(self, client: TestClient):
        """Test member creation fails with empty name."""
        response = client.post("/api/members", json={"name": ""})

        assert response.status_code == 422

    def test_create_member_missing_name(self, client: TestClient):
        """Test member creation fails without name."""
        response = client.post("/api/members", json={"email": "test@example.com"})

        assert response.status_code == 422

    def test_get_member_success(self, client: TestClient, sample_member: Member):
        """Test successful member retrieval."""
        response = client.get(f"/api/members/{sample_member.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_member.id
        assert data["name"] == sample_member.name
        assert data["email"] == sample_member.email

    def test_get_member_not_found(self, client: TestClient):
        """Test member retrieval for non-existent ID."""
        response = client.get("/api/members/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_members_empty(self, client: TestClient):
        """Test listing members when database is empty."""
        response = client.get("/api/members")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_members_with_data(self, client: TestClient, sample_members: list[Member]):
        """Test listing members returns all members."""
        response = client.get("/api/members")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(sample_members)

    def test_list_members_pagination(self, client: TestClient, sample_members: list[Member]):
        """Test listing members with pagination."""
        response = client.get("/api/members?skip=1&limit=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
