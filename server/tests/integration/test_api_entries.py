"""
Integration tests for Entry API endpoints.

These tests verify the entry logging functionality.
"""

from fastapi.testclient import TestClient

from app.models import EntryLog, Member


class TestEntryEndpoints:
    """Tests for /api/entry endpoints."""

    def test_log_entry_success(self, client: TestClient, sample_member: Member):
        """Test successful entry logging."""
        response = client.post(
            "/api/entry",
            json={"member_id": sample_member.id, "notes": "Court A"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == sample_member.id
        assert data["member_name"] == sample_member.name
        assert data["notes"] == "Court A"
        assert "Entry logged" in data["message"]
        assert "id" in data
        assert "timestamp" in data

    def test_log_entry_without_notes(self, client: TestClient, sample_member: Member):
        """Test entry logging without notes."""
        response = client.post(
            "/api/entry",
            json={"member_id": sample_member.id},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] is None

    def test_log_entry_member_not_found(self, client: TestClient):
        """Test entry logging for non-existent member."""
        response = client.post(
            "/api/entry",
            json={"member_id": 99999},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_log_entry_invalid_member_id(self, client: TestClient):
        """Test entry logging with invalid member_id."""
        response = client.post(
            "/api/entry",
            json={"member_id": 0},
        )

        assert response.status_code == 422

    def test_get_member_entries_success(
        self, client: TestClient, sample_member: Member, sample_entry: EntryLog
    ):
        """Test getting entry history for a member."""
        response = client.get(f"/api/entries/{sample_member.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == sample_member.id
        assert data["member_name"] == sample_member.name
        assert data["total_entries"] == 1
        assert len(data["entries"]) == 1

    def test_get_member_entries_empty(self, client: TestClient, sample_member: Member):
        """Test getting entry history when member has no entries."""
        response = client.get(f"/api/entries/{sample_member.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total_entries"] == 0
        assert data["entries"] == []

    def test_get_member_entries_not_found(self, client: TestClient):
        """Test getting entries for non-existent member."""
        response = client.get("/api/entries/99999")

        assert response.status_code == 404

    def test_multiple_entries_same_member(self, client: TestClient, sample_member: Member):
        """Test logging multiple entries for the same member."""
        # Log 3 entries
        for i in range(3):
            response = client.post(
                "/api/entry",
                json={"member_id": sample_member.id, "notes": f"Entry {i + 1}"},
            )
            assert response.status_code == 200

        # Verify all entries are recorded
        response = client.get(f"/api/entries/{sample_member.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total_entries"] == 3
